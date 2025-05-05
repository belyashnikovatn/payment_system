from datetime import timedelta
from decimal import Decimal, InvalidOperation
from uuid import UUID
from uuid import uuid4
from contextlib import asynccontextmanager


from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_async_session, engine
from app.config import settings

from app.security import generate_signature
from app import models, schemas, auth
import logging
import platform
import asyncio


logger = logging.getLogger(__name__)

if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Starting application...")
    yield
    # Shutdown logic
    logger.info("Shutting down application...")
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to your app!"}


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    request: Request, db: AsyncSession = Depends(get_async_session)
):
    form_data = await request.form()
    email = form_data.get("username")
    password = form_data.get("password")

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )

    user = await auth.authenticate_user(email, password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = auth.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.User)
async def read_users_me(
    current_user: models.User = Depends(auth.get_current_user),
):
    return current_user


@app.get("/users/me/accounts", response_model=list[schemas.Account])
async def read_user_accounts(
    current_user: models.User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    accounts = await models.Account.get_user_accounts(db, current_user.id)
    return accounts


@app.get("/users/me/transactions", response_model=list[schemas.Transaction])
async def read_user_transactions(
    current_user: models.User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    transactions = await models.Transaction.get_user_transactions(
        db, current_user.id
    )
    return transactions


@app.post("/webhook/payment")
async def handle_webhook(
    data: schemas.WebhookData,
    session: AsyncSession = Depends(get_async_session),
):
    """Обработчик входящих платежей с проверкой подписи и обработкой транзакций"""

    # 1. Проверка и нормализация данных
    try:
        amount = Decimal(str(data.amount)).quantize(Decimal("0.00"))
        transaction_id = str(UUID(str(data.transaction_id)))  # Валидация UUID
    except (InvalidOperation, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid data format: {str(e)}",
        )

    # 2. Генерация и проверка подписи
    expected_sig = generate_signature(
        account_id=data.account_id,
        amount=float(amount),  # Передаем float для совместимости
        transaction_id=transaction_id,
        user_id=data.user_id,
        secret_key=settings.SECRET_KEY,
    )

    if data.signature != expected_sig:
        logger.error(
            f"Signature mismatch for transaction {transaction_id}\n"
            f"Expected: {expected_sig}\n"
            f"Received: {data.signature}\n"
            f"Data: {data.dict()}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Invalid signature",
                "expected": expected_sig,
                "received": data.signature,
                "hint": "Check if secret keys match and data formats are identical",
            },
        )

    # 3. Проверка существования транзакции
    if await session.scalar(
        select(models.Transaction).where(
            models.Transaction.transaction_id == transaction_id
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transaction already processed",
        )

    # 4. Проверка пользователя
    if not await session.get(models.User, data.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # 5. Получение или создание счета
    account = await session.scalar(
        select(models.Account).where(
            models.Account.id == data.account_id,
            models.Account.user_id == data.user_id,
        )
    )

    if not account:
        account = models.Account(
            id=data.account_id, user_id=data.user_id, balance=Decimal("0.00")
        )
        session.add(account)

    # 6. Обновление баланса и создание транзакции
    try:
        account.balance += amount

        transaction = models.Transaction(
            transaction_id=transaction_id,
            user_id=data.user_id,
            account_id=account.id,
            amount=amount,
        )
        session.add(transaction)

        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.exception("Database transaction failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Transaction processing failed",
        )

    return {
        "status": "success",
        "new_balance": str(account.balance),
        "transaction_id": transaction_id,
        "account_id": account.id,
    }


@app.get("/utils/generate-uuid")
async def generate_uuid():
    """Генерация корректного UUID v4"""
    return {"uuid": str(uuid4())}


@app.post("/utils/signature-check")
async def debug_signature(data: dict):
    return {
        "generated": generate_signature(
            account_id=data["account_id"],
            amount=data["amount"],
            transaction_id=data["transaction_id"],
            user_id=data["user_id"],
            secret_key=settings.SECRET_KEY,
        ),
        "input_data": data,
    }


@app.get("/admin/users", response_model=list[schemas.User])
async def read_users(
    _: models.User = Depends(auth.get_current_admin),
    db: AsyncSession = Depends(get_async_session),
):
    users = await db.execute(select(models.User))
    return users.scalars().all()


@app.post("/admin/users", response_model=schemas.User)
async def create_user(
    user: schemas.UserCreate,
    _: models.User = Depends(auth.get_current_admin),
    db: AsyncSession = Depends(get_async_session),
):
    db_user = await models.User.get_by_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@app.get(
    "/admin/users/{user_id}/accounts", response_model=list[schemas.Account]
)
async def read_users_accounts(
    user_id: int,
    _: models.User = Depends(auth.get_current_admin),
    db: AsyncSession = Depends(get_async_session),
):
    accounts = await models.Account.get_user_accounts(db, user_id)
    return accounts


@app.put("/admin/users/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user: schemas.UserCreate,
    _: models.User = Depends(auth.get_current_admin),
    db: AsyncSession = Depends(get_async_session),
):
    db_user = await models.User.get_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db_user.email = user.email
    db_user.full_name = user.full_name
    if user.password:
        db_user.hashed_password = auth.get_password_hash(user.password)

    await db.commit()
    await db.refresh(db_user)

    return db_user


@app.delete("/admin/users/{user_id}", response_model=schemas.User)
async def delete_user(
    user_id: int,
    _: models.User = Depends(auth.get_current_admin),
    db: AsyncSession = Depends(get_async_session),
):
    db_user = await models.User.get_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    await db.delete(db_user)
    await db.commit()

    return db_user


if __name__ == "__main__":
    import subprocess
    import uvicorn

    subprocess.run(["alembic", "upgrade", "head"])
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

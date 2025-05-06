from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal, InvalidOperation
from uuid import UUID
from sqlalchemy.future import select
from app import models, schemas
from app.config import settings
from app.database import get_async_session
from app.security import generate_signature

router = APIRouter()


@router.post("/payment")
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
        # logger.error(
        #     f"Signature mismatch for transaction {transaction_id}\n"
        #     f"Expected: {expected_sig}\n"
        #     f"Received: {data.signature}\n"
        #     f"Data: {data.dict()}"
        # )
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
        # logger.exception("Database transaction failed")
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

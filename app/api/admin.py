from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app import models, schemas
from app.database import get_async_session
from app import auth

router = APIRouter()


@router.get("/users", response_model=list[schemas.User])
async def read_users(
    _: models.User = Depends(auth.get_current_admin),
    db: AsyncSession = Depends(get_async_session),
):
    users = await db.execute(select(models.User))
    return users.scalars().all()


@router.post("/users", response_model=schemas.User)
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


@router.get("/users/{user_id}/accounts", response_model=list[schemas.Account])
async def read_users_accounts(
    user_id: int,
    _: models.User = Depends(auth.get_current_admin),
    db: AsyncSession = Depends(get_async_session),
):
    accounts = await models.Account.get_user_accounts(db, user_id)
    return accounts


@router.put("/users/{user_id}", response_model=schemas.User)
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


@router.delete("/users/{user_id}", response_model=schemas.User)
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

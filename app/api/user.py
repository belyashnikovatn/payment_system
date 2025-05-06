from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas, auth, models
from app.database import get_async_session

router = APIRouter()


@router.get("/me", response_model=schemas.User)
async def read_users_me(
    current_user: models.User = Depends(auth.get_current_user),
):
    return current_user


@router.get("/me/accounts", response_model=list[schemas.Account])
async def read_user_accounts(
    current_user: models.User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    accounts = await models.Account.get_user_accounts(db, current_user.id)
    return accounts


@router.get("/me/transactions", response_model=list[schemas.Transaction])
async def read_user_transactions(
    current_user: models.User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    transactions = await models.Transaction.get_user_transactions(
        db, current_user.id
    )
    return transactions

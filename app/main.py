from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from . import models, schemas, auth
from .database import get_async_session


app = FastAPI()


@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to your app!"}


@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    request: Request,
    db: AsyncSession = Depends(get_async_session)
):
    form_data = await request.form()
    email = form_data.get("username")
    password = form_data.get("password")

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )

    user = await auth.authenticate_user(email, password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.User)
async def read_users_me(
    current_user: models.User = Depends(auth.get_current_user)
):
    return current_user


@app.get("/users/me/accounts", response_model=list[schemas.Account])
async def read_user_accounts(
    current_user: models.User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    accounts = await models.Account.get_user_accounts(db, current_user.id)
    return accounts


@app.get("/users/me/transactions", response_model=list[schemas.Transaction])
async def read_user_transactions(
    current_user: models.User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    transactions = await models.Transaction.get_user_transactions(db, current_user.id)
    return transactions

from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime
from pydantic import field_validator
from uuid import UUID


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int


class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


class AccountBase(BaseModel):
    account_number: Optional[str] = None


class Account(AccountBase):
    id: int
    user_id: int
    balance: float
    created_at: datetime
    account_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TransactionBase(BaseModel):
    amount: float


class Transaction(TransactionBase):
    id: int
    user_id: int
    account_id: int
    transaction_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WebhookData(BaseModel):
    transaction_id: str
    user_id: int
    account_id: int
    amount: float
    signature: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("amount")
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive")
        return round(v, 2)

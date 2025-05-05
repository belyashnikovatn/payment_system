from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    Numeric,
    DateTime,
    select,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(50), index=True, nullable=True)
    hashed_password = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False)

    accounts = relationship("Account", back_populates="user")
    transactions = relationship(
        "Transaction", back_populates="user", lazy="raise_on_sql"
    )

    @classmethod
    async def get_by_email(cls, db, email: str) -> "User | None":
        stmt = select(cls).where(cls.email == email)
        result = await db.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def get_by_id(cls, db, user_id: int) -> "User | None":
        stmt = select(cls).where(cls.id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    account_number = Column(
        String(36), unique=True, index=True, default=lambda: str(uuid.uuid4())
    )
    balance = Column(Numeric(10, 2), default=0.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")

    @classmethod
    async def get_user_accounts(cls, db, user_id: int) -> list["Account"]:
        stmt = select(cls).where(cls.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().all()


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        UniqueConstraint("transaction_id", name="uniq_transaction"),
    )

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True,
    )
    amount = Column(Numeric(10, 2), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")

    @classmethod
    async def get_user_transactions(
        cls, db, user_id: int
    ) -> list["Transaction"]:
        stmt = select(cls).where(cls.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().all()

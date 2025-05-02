from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Numeric, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    full_name = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(100))
    is_admin = Column(Boolean, default=False)

    accounts = relationship('Account', back_populates='owner')


class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    account_number = Column(String(20), unique=True, index=True)
    balance = Column(Numeric(10, 2), default=0.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship('User', back_populates='accounts')
    transactions = relationship('Transaction', back_populates='account')


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey('users.id'))
    account_id = Column(Integer, ForeignKey('accounts.id'))
    amount = Column(Numeric(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    account = relationship('Account', back_populates='transactions')

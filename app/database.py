import os
from sqlalchemy.ext.asyncio import (  # Импорт из правильного модуля!
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool  # NullPool импортируется отдельно
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    poolclass=NullPool
)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False
)

Base = declarative_base()

async def get_async_session():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
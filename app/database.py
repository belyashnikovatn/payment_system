from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool
from app.config import settings
import asyncio
import atexit
import platform


if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


DATABASE_URL = settings.DATABASE_URL
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in the environment")

# Создаем engine с явным указанием параметров для Windows
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    poolclass=NullPool,
    connect_args={
        "server_settings": {
            "client_encoding": "utf8",
            "application_name": "fastapi_app",
        }
    },
)


# Функция для корректного закрытия соединений при завершении
async def dispose_engine():
    await engine.dispose()


# Регистрируем очистку при выходе
atexit.register(lambda: asyncio.run(dispose_engine()))

SessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession, autoflush=False
)


async def get_async_session():
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()

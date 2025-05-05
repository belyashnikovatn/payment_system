from app.database import DATABASE_URL
from app.models import Base
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
import asyncio
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Импортируем после добавления пути
config = context.config

# Устанавливаем URL БД
config.set_main_option("sqlalchemy.url", DATABASE_URL)
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in "offline" mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in "online" mode."""
    connectable = create_async_engine(DATABASE_URL)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

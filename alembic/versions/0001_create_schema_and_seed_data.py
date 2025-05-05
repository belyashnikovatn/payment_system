from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from passlib.context import CryptContext
import uuid
from datetime import datetime

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def upgrade():
    # Таблица пользователей
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String, unique=True, index=True),
        sa.Column('full_name', sa.String),
        sa.Column('hashed_password', sa.String),
        sa.Column('is_admin', sa.Boolean, default=False),
    )

    # Таблица аккаунтов
    op.create_table(
        'accounts',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('account_number', sa.String, unique=True, index=True),
        sa.Column('balance', sa.Numeric, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()')),
    )

    # Таблица транзакций
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('transaction_id', UUID(as_uuid=True),
                  default=uuid.uuid4, unique=True, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('account_id', sa.Integer, sa.ForeignKey('accounts.id')),
        sa.Column('amount', sa.Numeric),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()')),
    )

    # Вставка пользователей
    users_table = sa.table(
        'users',
        sa.column('id', sa.Integer),
        sa.column('email', sa.String),
        sa.column('full_name', sa.String),
        sa.column('hashed_password', sa.String),
        sa.column('is_admin', sa.Boolean),
    )

    op.bulk_insert(users_table, [
        {
            'id': 1,
            'email': 'testuser@example.com',
            'full_name': 'Test User',
            'hashed_password': pwd_context.hash('userpass'),
            'is_admin': False
        },
        {
            'id': 2,
            'email': 'admin@example.com',
            'full_name': 'Admin User',
            'hashed_password': pwd_context.hash('adminpass'),
            'is_admin': True
        }
    ])

    # Вставка счёта
    accounts_table = sa.table(
        'accounts',
        sa.column('id', sa.Integer),
        sa.column('user_id', sa.Integer),
        sa.column('account_number', sa.String),
        sa.column('balance', sa.Numeric),
        sa.column('created_at', sa.DateTime),
    )

    op.bulk_insert(accounts_table, [
        {
            'id': 1,
            'user_id': 1,
            'account_number': 'ACC000001',
            'balance': 1000,
            'created_at': datetime.utcnow()
        }
    ])

    # Вставка транзакции
    transactions_table = sa.table(
        'transactions',
        sa.column('id', sa.Integer),
        sa.column('transaction_id', UUID(as_uuid=True)),
        sa.column('user_id', sa.Integer),
        sa.column('account_id', sa.Integer),
        sa.column('amount', sa.Numeric),
        sa.column('created_at', sa.DateTime),
    )

    op.bulk_insert(transactions_table, [
        {
            'id': 1,
            'transaction_id': str(uuid.uuid4()),
            'user_id': 1,
            'account_id': 1,
            'amount': 1000,
            'created_at': datetime.utcnow()
        }
    ])

    # Сброс последовательностей
    op.execute("SELECT setval('users_id_seq', (SELECT MAX(id) FROM users))")
    op.execute("SELECT setval('accounts_id_seq', (SELECT MAX(id) FROM accounts))")
    op.execute(
        "SELECT setval('transactions_id_seq', (SELECT MAX(id) FROM transactions))")


def downgrade():
    op.drop_table('transactions')
    op.drop_table('accounts')
    op.drop_table('users')

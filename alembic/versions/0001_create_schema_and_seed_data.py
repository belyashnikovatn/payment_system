from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Boolean, Numeric
from passlib.context import CryptContext

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String, unique=True, index=True),
        sa.Column('full_name', sa.String),
        sa.Column('hashed_password', sa.String),
        sa.Column('is_admin', sa.Boolean, default=False),
    )

    op.create_table(
        'accounts',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('account_number', sa.String, unique=True, index=True),
        sa.Column('balance', sa.Numeric, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('transaction_id', sa.String, unique=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('account_id', sa.Integer, sa.ForeignKey('accounts.id')),
        sa.Column('amount', sa.Numeric),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    users_table = table(
        'users',
        column('id', Integer),
        column('email', String),
        column('full_name', String),
        column('hashed_password', String),
        column('is_admin', Boolean)
    )

    password_user = pwd_context.hash('userpass')
    password_admin = pwd_context.hash('adminpass')

    op.bulk_insert(users_table, [
        {'id': 1, 'email': 'testuser@example.com', 'full_name': 'Test User', 'hashed_password': password_user, 'is_admin': False},
        {'id': 2, 'email': 'admin@example.com', 'full_name': 'Admin User', 'hashed_password': password_admin, 'is_admin': True}
    ])

    accounts_table = table(
        'accounts',
        column('id', Integer),
        column('user_id', Integer),
        column('balance', Numeric)
    )

    op.bulk_insert(accounts_table, [
        {'id': 1, 'user_id': 1, 'balance': 0}
    ])


def downgrade():
    op.drop_table('transactions')
    op.drop_table('accounts')
    op.drop_table('users')

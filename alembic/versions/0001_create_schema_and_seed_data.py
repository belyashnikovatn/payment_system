from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from passlib.context import CryptContext
import uuid

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
        sa.Column('transaction_id', UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('account_id', sa.Integer, sa.ForeignKey('accounts.id')),
        sa.Column('amount', sa.Numeric),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # Вставка пользователей
    password_user = pwd_context.hash('userpass')
    password_admin = pwd_context.hash('adminpass')

    op.execute(f"""
        INSERT INTO users (id, email, full_name, hashed_password, is_admin)
        VALUES
            (1, 'testuser@example.com', 'Test User', '{password_user}', FALSE),
            (2, 'admin@example.com', 'Admin User', '{password_admin}', TRUE);
    """)

    # Вставка аккаунта
    op.execute("""
        INSERT INTO accounts (id, user_id, account_number, balance, created_at)
        VALUES (1, 1, 'ACC000001', 0, now());
    """)

def downgrade():
    op.drop_table('transactions')
    op.drop_table('accounts')
    op.drop_table('users')

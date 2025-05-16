"""Initial database tables

Revision ID: 001_initial_tables
Revises: 
Create Date: 2024-03-19
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = '001_initial_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create user table
    op.create_table(
        'user',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(50), unique=True, index=True),
        sa.Column('password', sa.String(255), nullable=False),
        sa.Column('enabled', sa.Boolean(), default=True),
        sa.Column('account_non_expired', sa.Boolean(), default=True),
        sa.Column('account_non_locked', sa.Boolean(), default=True),
        sa.Column('credentials_non_expired', sa.Boolean(), default=True),
        sa.Column('created_date', sa.DateTime(timezone=True))
    )

    # Create authority table
    op.create_table(
        'authority',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('authority', sa.String(50), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE')
    )

def downgrade():
    op.drop_table('authority')
    op.drop_table('user') 
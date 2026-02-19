"""Add web_sessions table for UTM tracking

Revision ID: a1b2c3d4e5f6
Revises: 4cffd1d19e60
Create Date: 2026-02-19 20:00:00.000000

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '4cffd1d19e60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create web_sessions table
    op.create_table(
        'web_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # UTM tracking
        sa.Column('utm_source', sa.String(length=255), nullable=True),
        sa.Column('utm_medium', sa.String(length=255), nullable=True),
        sa.Column('utm_campaign', sa.String(length=255), nullable=True),
        sa.Column('utm_term', sa.String(length=255), nullable=True),
        sa.Column('utm_content', sa.String(length=255), nullable=True),
        sa.Column('referrer', sa.Text(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        
        # Telegram user data (filled when user opens bot)
        sa.Column('telegram_id', sa.BigInteger(), nullable=True),
        sa.Column('telegram_username', sa.String(length=255), nullable=True),
        sa.Column('bot_started_at', sa.TIMESTAMP(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    op.create_index(op.f('ix_web_sessions_id'), 'web_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_web_sessions_session_id'), 'web_sessions', ['session_id'], unique=True)
    op.create_index(op.f('ix_web_sessions_telegram_id'), 'web_sessions', ['telegram_id'], unique=False)
    
    # Add session_id to check_requests table
    op.add_column('check_requests', sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_check_requests_session_id',
        'check_requests',
        'web_sessions',
        ['session_id'],
        ['session_id'],
        ondelete='SET NULL'
    )
    op.create_index(op.f('ix_check_requests_session_id'), 'check_requests', ['session_id'], unique=False)


def downgrade() -> None:
    # Remove session_id from check_requests
    op.drop_index(op.f('ix_check_requests_session_id'), table_name='check_requests')
    op.drop_constraint('fk_check_requests_session_id', 'check_requests', type_='foreignkey')
    op.drop_column('check_requests', 'session_id')
    
    # Drop web_sessions table
    op.drop_index(op.f('ix_web_sessions_telegram_id'), table_name='web_sessions')
    op.drop_index(op.f('ix_web_sessions_session_id'), table_name='web_sessions')
    op.drop_index(op.f('ix_web_sessions_id'), table_name='web_sessions')
    op.drop_table('web_sessions')

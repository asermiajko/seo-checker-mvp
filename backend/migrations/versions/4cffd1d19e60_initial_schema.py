"""Initial schema

Revision ID: 4cffd1d19e60
Revises:
Create Date: 2026-02-19 17:00:00.000000

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '4cffd1d19e60'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create check_requests table
    op.create_table(
        'check_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('site_url', sa.String(length=500), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column(
            'updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_check_requests_id'), 'check_requests', ['id'], unique=False)
    op.create_index(
        op.f('ix_check_requests_telegram_id'),
        'check_requests',
        ['telegram_id'],
        unique=False
    )

    # Create check_results table
    op.create_table(
        'check_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('check_request_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.DECIMAL(precision=3, scale=1), nullable=False),
        sa.Column('problems_critical', sa.Integer(), nullable=True),
        sa.Column('problems_important', sa.Integer(), nullable=True),
        sa.Column('checks_ok', sa.Integer(), nullable=True),
        sa.Column('report_data', sa.JSON(), nullable=False),
        sa.Column('detailed_checks', sa.JSON(), nullable=False),
        sa.Column('processing_time_sec', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['check_request_id'], ['check_requests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_check_results_id'), 'check_results', ['id'], unique=False)


def downgrade() -> None:
    # Drop check_results table
    op.drop_index(op.f('ix_check_results_id'), table_name='check_results')
    op.drop_table('check_results')

    # Drop check_requests table
    op.drop_index(op.f('ix_check_requests_telegram_id'), table_name='check_requests')
    op.drop_index(op.f('ix_check_requests_id'), table_name='check_requests')
    op.drop_table('check_requests')

"""Add audio comparisons table

Revision ID: 003
Revises: 002
Create Date: 2025-01-03 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create audio_comparisons table."""
    op.create_table(
        'audio_comparisons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('test_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('baseline_filename', sa.String(length=255), nullable=False),
        sa.Column('current_filename', sa.String(length=255), nullable=False),
        sa.Column('baseline_file_path', sa.String(length=500), nullable=True),
        sa.Column('current_file_path', sa.String(length=500), nullable=True),
        sa.Column('baseline_duration', sa.Float(), nullable=True),
        sa.Column('current_duration', sa.Float(), nullable=True),
        sa.Column('baseline_sample_rate', sa.Integer(), nullable=True),
        sa.Column('current_sample_rate', sa.Integer(), nullable=True),
        sa.Column('baseline_channels', sa.Integer(), nullable=True),
        sa.Column('current_channels', sa.Integer(), nullable=True),
        sa.Column('baseline_format', sa.String(length=50), nullable=True),
        sa.Column('current_format', sa.String(length=50), nullable=True),
        sa.Column('similarity_score', sa.Float(), nullable=True),
        sa.Column('duration_match', sa.String(length=20), nullable=True),
        sa.Column('format_match', sa.String(length=20), nullable=True),
        sa.Column('sample_rate_match', sa.String(length=20), nullable=True),
        sa.Column('channels_match', sa.String(length=20), nullable=True),
        sa.Column('summary', sa.JSON(), nullable=True),
        sa.Column('differences', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(
        'idx_audio_status_created',
        'audio_comparisons',
        ['status', 'created_at'],
        unique=False
    )
    op.create_index(
        'idx_audio_test_name',
        'audio_comparisons',
        ['test_name'],
        unique=False
    )


def downgrade() -> None:
    """Drop audio_comparisons table."""
    op.drop_index('idx_audio_test_name', table_name='audio_comparisons')
    op.drop_index('idx_audio_status_created', table_name='audio_comparisons')
    op.drop_table('audio_comparisons')

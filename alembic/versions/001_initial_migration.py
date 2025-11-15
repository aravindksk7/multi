"""Initial migration - create comparison_jobs table

Revision ID: 001
Revises: 
Create Date: 2025-11-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create comparison_jobs table
    op.create_table(
        'comparison_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('suite_name', sa.String(length=255), nullable=True),
        sa.Column('environment', sa.String(length=100), nullable=True),
        sa.Column('run_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.Enum('QUEUED', 'RUNNING', 'COMPLETED', 'FAILED', name='jobstatus'), nullable=False),
        sa.Column('baseline_xml', sa.Text(), nullable=False),
        sa.Column('current_xml', sa.Text(), nullable=False),
        sa.Column('summary', sa.JSON(), nullable=True),
        sa.Column('differences', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_job_status_created', 'comparison_jobs', ['status', 'created_at'], unique=False)
    op.create_index('idx_job_suite_env', 'comparison_jobs', ['suite_name', 'environment'], unique=False)
    op.create_index(op.f('ix_comparison_jobs_created_at'), 'comparison_jobs', ['created_at'], unique=False)
    op.create_index(op.f('ix_comparison_jobs_environment'), 'comparison_jobs', ['environment'], unique=False)
    op.create_index(op.f('ix_comparison_jobs_id'), 'comparison_jobs', ['id'], unique=False)
    op.create_index(op.f('ix_comparison_jobs_run_id'), 'comparison_jobs', ['run_id'], unique=False)
    op.create_index(op.f('ix_comparison_jobs_status'), 'comparison_jobs', ['status'], unique=False)
    op.create_index(op.f('ix_comparison_jobs_suite_name'), 'comparison_jobs', ['suite_name'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_comparison_jobs_suite_name'), table_name='comparison_jobs')
    op.drop_index(op.f('ix_comparison_jobs_status'), table_name='comparison_jobs')
    op.drop_index(op.f('ix_comparison_jobs_run_id'), table_name='comparison_jobs')
    op.drop_index(op.f('ix_comparison_jobs_id'), table_name='comparison_jobs')
    op.drop_index(op.f('ix_comparison_jobs_environment'), table_name='comparison_jobs')
    op.drop_index(op.f('ix_comparison_jobs_created_at'), table_name='comparison_jobs')
    op.drop_index('idx_job_suite_env', table_name='comparison_jobs')
    op.drop_index('idx_job_status_created', table_name='comparison_jobs')
    
    # Drop table
    op.drop_table('comparison_jobs')

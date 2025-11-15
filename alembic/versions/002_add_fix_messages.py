"""Add fix_messages table

Revision ID: 002
Revises: 001
Create Date: 2025-11-15 20:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'fix_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('msg_type', sa.String(length=10), nullable=False),
        sa.Column('msg_seq_num', sa.Integer(), nullable=True),
        sa.Column('sender_comp_id', sa.String(length=100), nullable=False),
        sa.Column('target_comp_id', sa.String(length=100), nullable=False),
        sa.Column('message_data', sa.Text(), nullable=False),
        sa.Column('raw_message', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('PENDING', 'SENT', 'FAILED', 'ACKNOWLEDGED', 'REJECTED', name='fixmessagestatus'), nullable=False),
        sa.Column('response_message', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('cl_ord_id', sa.String(length=255), nullable=True),
        sa.Column('symbol', sa.String(length=50), nullable=True),
        sa.Column('side', sa.String(length=10), nullable=True),
        sa.Column('order_qty', sa.String(length=50), nullable=True),
        sa.Column('price', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_fix_status_created', 'fix_messages', ['status', 'created_at'])
    op.create_index('idx_fix_sender_target', 'fix_messages', ['sender_comp_id', 'target_comp_id'])
    op.create_index('idx_fix_cl_ord_id', 'fix_messages', ['cl_ord_id'])
    op.create_index(op.f('ix_fix_messages_id'), 'fix_messages', ['id'])
    op.create_index(op.f('ix_fix_messages_msg_type'), 'fix_messages', ['msg_type'])
    op.create_index(op.f('ix_fix_messages_sender_comp_id'), 'fix_messages', ['sender_comp_id'])
    op.create_index(op.f('ix_fix_messages_target_comp_id'), 'fix_messages', ['target_comp_id'])
    op.create_index(op.f('ix_fix_messages_status'), 'fix_messages', ['status'])
    op.create_index(op.f('ix_fix_messages_session_id'), 'fix_messages', ['session_id'])
    op.create_index(op.f('ix_fix_messages_symbol'), 'fix_messages', ['symbol'])
    op.create_index(op.f('ix_fix_messages_created_at'), 'fix_messages', ['created_at'])


def downgrade():
    op.drop_index(op.f('ix_fix_messages_created_at'), table_name='fix_messages')
    op.drop_index(op.f('ix_fix_messages_symbol'), table_name='fix_messages')
    op.drop_index(op.f('ix_fix_messages_session_id'), table_name='fix_messages')
    op.drop_index(op.f('ix_fix_messages_status'), table_name='fix_messages')
    op.drop_index(op.f('ix_fix_messages_target_comp_id'), table_name='fix_messages')
    op.drop_index(op.f('ix_fix_messages_sender_comp_id'), table_name='fix_messages')
    op.drop_index(op.f('ix_fix_messages_msg_type'), table_name='fix_messages')
    op.drop_index(op.f('ix_fix_messages_id'), table_name='fix_messages')
    op.drop_index('idx_fix_cl_ord_id', table_name='fix_messages')
    op.drop_index('idx_fix_sender_target', table_name='fix_messages')
    op.drop_index('idx_fix_status_created', table_name='fix_messages')
    op.drop_table('fix_messages')

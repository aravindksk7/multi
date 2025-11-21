"""004_add_protocol_testing_tables

Revision ID: 004
Revises: 003
Create Date: 2025-11-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create protocol_sessions table
    op.create_table(
        'protocol_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('protocol_type', sa.Enum('OUCH', 'ITCH', name='protocoltype'), nullable=False),
        sa.Column('host', sa.String(length=255), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('session_id', sa.String(length=50), nullable=True),
        sa.Column('status', sa.Enum('CREATED', 'CONNECTING', 'CONNECTED', 'DISCONNECTED', 'ERROR', name='sessionstatus'), nullable=True),
        sa.Column('sequence_number', sa.BigInteger(), nullable=True),
        sa.Column('client_heartbeat_interval', sa.Integer(), nullable=True),
        sa.Column('server_heartbeat_interval', sa.Integer(), nullable=True),
        sa.Column('session_metadata', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('connected_at', sa.DateTime(), nullable=True),
        sa.Column('disconnected_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_protocol_sessions_id'), 'protocol_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_protocol_sessions_protocol_type'), 'protocol_sessions', ['protocol_type'], unique=False)
    op.create_index(op.f('ix_protocol_sessions_status'), 'protocol_sessions', ['status'], unique=False)

    # Create protocol_tests table
    op.create_table(
        'protocol_tests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('test_name', sa.String(length=255), nullable=False),
        sa.Column('protocol_type', sa.Enum('OUCH', 'ITCH', name='protocoltype'), nullable=False),
        sa.Column('test_description', sa.Text(), nullable=True),
        sa.Column('test_config', sa.JSON(), nullable=True),
        sa.Column('status', sa.Enum('CREATED', 'RUNNING', 'PASSED', 'FAILED', 'ERROR', name='teststatus'), nullable=True),
        sa.Column('result_summary', sa.JSON(), nullable=True),
        sa.Column('error_details', sa.Text(), nullable=True),
        sa.Column('messages_sent', sa.Integer(), nullable=True),
        sa.Column('messages_received', sa.Integer(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['protocol_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_protocol_tests_id'), 'protocol_tests', ['id'], unique=False)
    op.create_index(op.f('ix_protocol_tests_protocol_type'), 'protocol_tests', ['protocol_type'], unique=False)
    op.create_index(op.f('ix_protocol_tests_status'), 'protocol_tests', ['status'], unique=False)
    op.create_index(op.f('ix_protocol_tests_test_name'), 'protocol_tests', ['test_name'], unique=False)

    # Create protocol_messages table
    op.create_table(
        'protocol_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('protocol_type', sa.Enum('OUCH', 'ITCH', name='protocoltype'), nullable=False),
        sa.Column('message_type', sa.String(length=100), nullable=False),
        sa.Column('message_indicator', sa.Integer(), nullable=False),
        sa.Column('direction', sa.Enum('incoming', 'outgoing', name='messagedirection'), nullable=False),
        sa.Column('message_data', sa.JSON(), nullable=False),
        sa.Column('raw_bytes', sa.Text(), nullable=True),
        sa.Column('is_valid', sa.Integer(), nullable=True),
        sa.Column('validation_errors', sa.JSON(), nullable=True),
        sa.Column('sequence_number', sa.BigInteger(), nullable=True),
        sa.Column('session_id', sa.Integer(), nullable=True),
        sa.Column('test_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('received_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['protocol_sessions.id'], ),
        sa.ForeignKeyConstraint(['test_id'], ['protocol_tests.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_protocol_messages_direction'), 'protocol_messages', ['direction'], unique=False)
    op.create_index(op.f('ix_protocol_messages_id'), 'protocol_messages', ['id'], unique=False)
    op.create_index(op.f('ix_protocol_messages_message_type'), 'protocol_messages', ['message_type'], unique=False)
    op.create_index(op.f('ix_protocol_messages_protocol_type'), 'protocol_messages', ['protocol_type'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_protocol_messages_protocol_type'), table_name='protocol_messages')
    op.drop_index(op.f('ix_protocol_messages_message_type'), table_name='protocol_messages')
    op.drop_index(op.f('ix_protocol_messages_id'), table_name='protocol_messages')
    op.drop_index(op.f('ix_protocol_messages_direction'), table_name='protocol_messages')
    op.drop_table('protocol_messages')
    
    op.drop_index(op.f('ix_protocol_tests_test_name'), table_name='protocol_tests')
    op.drop_index(op.f('ix_protocol_tests_status'), table_name='protocol_tests')
    op.drop_index(op.f('ix_protocol_tests_protocol_type'), table_name='protocol_tests')
    op.drop_index(op.f('ix_protocol_tests_id'), table_name='protocol_tests')
    op.drop_table('protocol_tests')
    
    op.drop_index(op.f('ix_protocol_sessions_status'), table_name='protocol_sessions')
    op.drop_index(op.f('ix_protocol_sessions_protocol_type'), table_name='protocol_sessions')
    op.drop_index(op.f('ix_protocol_sessions_id'), table_name='protocol_sessions')
    op.drop_table('protocol_sessions')

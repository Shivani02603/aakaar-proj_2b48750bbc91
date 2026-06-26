"""Initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2023-10-11 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('hashed_password', sa.String, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text("now()"), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.text("now()"), nullable=False),
    )

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('user_id', sa.String, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('filename', sa.String, nullable=False),
        sa.Column('file_path', sa.String, nullable=False),
        sa.Column('file_size', sa.Integer, nullable=False),
        sa.Column('status', sa.String, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text("now()"), nullable=False),
        sa.Column('processed_at', sa.TIMESTAMP, nullable=True),
    )

    # Create document_chunks table
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('document_id', sa.String, sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('chunk_index', sa.Integer, nullable=False),
        sa.Column('content', sa.String, nullable=False),
        sa.Column('embedding', Vector(1536), nullable=False),
        sa.Column('metadata', sa.JSON, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text("now()"), nullable=False),
    )
    op.create_index(
        'ix_document_chunks_embedding',
        'document_chunks',
        ['embedding'],
        postgresql_using='hnsw'
    )

    # Create chat_sessions table
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('user_id', sa.String, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('document_id', sa.String, sa.ForeignKey('documents.id'), nullable=False),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text("now()"), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.text("now()"), nullable=False),
    )

    # Create chat_messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('session_id', sa.String, sa.ForeignKey('chat_sessions.id'), nullable=False),
        sa.Column('role', sa.String, nullable=False),
        sa.Column('content', sa.String, nullable=False),
        sa.Column('chunk_ids', sa.ARRAY(sa.String), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text("now()"), nullable=False),
    )


def downgrade():
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
    op.drop_table('document_chunks')
    op.drop_table('documents')
    op.drop_table('users')
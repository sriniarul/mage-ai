"""Add JWT blacklist table for secure logout

Revision ID: 20250712213_jwt_blacklist
Revises: e3593cc2191e
Create Date: 2025-07-12 21:33:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250712213_jwt_blacklist'
down_revision = 'e3593cc2191e'
branch_labels = None
depends_on = None


def upgrade():
    # Create JWT blacklist table
    op.create_table('jwt_blacklist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('token', sa.Text(), nullable=False),
        sa.Column('jti', sa.String(length=255), nullable=True),
        sa.Column('blacklisted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for efficient queries
    op.create_index('idx_jwt_blacklist_expires_at', 'jwt_blacklist', ['expires_at'], unique=False)
    op.create_index('idx_jwt_blacklist_token_expires', 'jwt_blacklist', ['token', 'expires_at'], unique=False)
    op.create_index(op.f('ix_jwt_blacklist_jti'), 'jwt_blacklist', ['jti'], unique=False)
    op.create_index(op.f('ix_jwt_blacklist_token'), 'jwt_blacklist', ['token'], unique=True)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_jwt_blacklist_token'), table_name='jwt_blacklist')
    op.drop_index(op.f('ix_jwt_blacklist_jti'), table_name='jwt_blacklist')
    op.drop_index('idx_jwt_blacklist_token_expires', table_name='jwt_blacklist')
    op.drop_index('idx_jwt_blacklist_expires_at', table_name='jwt_blacklist')
    
    # Drop table
    op.drop_table('jwt_blacklist')
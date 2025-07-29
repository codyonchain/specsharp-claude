"""Add OAuth fields to users table

Revision ID: add_oauth_fields
Revises: add_project_shares_table
Create Date: 2025-01-28

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_oauth_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add OAuth provider fields
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('oauth_provider', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('oauth_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('profile_picture', sa.String(), nullable=True))


def downgrade():
    # Remove OAuth columns
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('profile_picture')
        batch_op.drop_column('oauth_id')
        batch_op.drop_column('oauth_provider')
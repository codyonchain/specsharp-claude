"""add scenario name to projects

Revision ID: add_scenario_name
Revises: add_oauth_fields
Create Date: 2025-01-29

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_scenario_name'
down_revision = 'add_oauth_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add scenario_name column to projects table
    op.add_column('projects', sa.Column('scenario_name', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove scenario_name column from projects table
    op.drop_column('projects', 'scenario_name')
"""Add missing fields to projects table

Revision ID: add_project_fields
Revises: 
Create Date: 2025-07-27

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_project_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to projects table
    op.add_column('projects', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('projects', sa.Column('building_type', sa.String(), nullable=True))
    op.add_column('projects', sa.Column('occupancy_type', sa.String(), nullable=True))
    op.add_column('projects', sa.Column('cost_per_sqft', sa.Float(), nullable=True))
    op.add_column('projects', sa.Column('cost_data', sa.Text(), nullable=True))


def downgrade():
    # Remove the columns
    op.drop_column('projects', 'cost_data')
    op.drop_column('projects', 'cost_per_sqft')
    op.drop_column('projects', 'occupancy_type')
    op.drop_column('projects', 'building_type')
    op.drop_column('projects', 'description')
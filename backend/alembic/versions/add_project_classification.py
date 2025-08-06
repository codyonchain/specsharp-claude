"""Add project_classification to projects table

Revision ID: add_project_classification
Revises: 
Create Date: 2025-08-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'add_project_classification'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create the enum type first for PostgreSQL
    project_classification_enum = sa.Enum('ground_up', 'addition', 'renovation', name='project_classification_enum')
    project_classification_enum.create(op.get_bind(), checkfirst=True)
    
    # Add project_classification column with default value 'ground_up'
    op.add_column('projects', 
        sa.Column('project_classification', 
                  sa.String(),  # Use String instead of Enum for compatibility
                  nullable=False,
                  server_default='ground_up')
    )
    
    # Remove the server default after setting existing records
    op.alter_column('projects', 'project_classification', server_default=None)


def downgrade():
    # Remove the project_classification column
    op.drop_column('projects', 'project_classification')
    
    # Drop the enum type
    sa.Enum(name='project_classification_enum').drop(op.get_bind(), checkfirst=True)
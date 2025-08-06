"""Merge heads

Revision ID: 18e0ecea2473
Revises: 8326beeb3bf6, add_project_classification
Create Date: 2025-08-05 20:36:48.345497

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18e0ecea2473'
down_revision = ('8326beeb3bf6', 'add_project_classification')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
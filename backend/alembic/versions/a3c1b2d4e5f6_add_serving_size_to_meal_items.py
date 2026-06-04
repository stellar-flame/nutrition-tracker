"""add serving_size to meal_items

Revision ID: a3c1b2d4e5f6
Revises: f1a0a394db8a
Create Date: 2026-06-04 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'a3c1b2d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f1a0a394db8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('meal_items', sa.Column('serving_size', sa.Float(), nullable=False, server_default='1.0'))


def downgrade() -> None:
    op.drop_column('meal_items', 'serving_size')

"""drop serving_size from meals

Revision ID: b4d2e3f1a2b3
Revises: a3c1b2d4e5f6
Create Date: 2026-06-04 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'b4d2e3f1a2b3'
down_revision: Union[str, Sequence[str], None] = 'a3c1b2d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('meals', 'serving_size')


def downgrade() -> None:
    op.add_column('meals', sa.Column('serving_size', sa.Float(), nullable=False, server_default='1.0'))

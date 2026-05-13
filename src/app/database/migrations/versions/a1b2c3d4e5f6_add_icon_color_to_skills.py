"""add_icon_color_to_skills

Revision ID: a1b2c3d4e5f6
Revises: acc616ec7768
Create Date: 2026-05-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'acc616ec7768'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('skills', sa.Column('icon', sa.String(length=50), nullable=True))
    op.add_column('skills', sa.Column('color', sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column('skills', 'color')
    op.drop_column('skills', 'icon')

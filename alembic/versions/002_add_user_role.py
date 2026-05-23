"""Add user role column (artist | collector | enthusiast).

Revision ID: 002_add_user_role
Revises: 001_initial
Create Date: 2025-02-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002_add_user_role"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(32), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "role")

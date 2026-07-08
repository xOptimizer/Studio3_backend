"""Add phone to users.

Revision ID: 007_user_phone
Revises: 006_social
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "007_user_phone"
down_revision: Union[str, None] = "006_social"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(32), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "phone")

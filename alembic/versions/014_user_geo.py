"""Add latitude/longitude to users for "near me" seller discovery.

Revision ID: 014_user_geo
Revises: 013_orders
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "014_user_geo"
down_revision: Union[str, None] = "013_orders"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("users", sa.Column("longitude", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "longitude")
    op.drop_column("users", "latitude")

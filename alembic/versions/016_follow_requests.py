"""Instagram-style private accounts: follow requests need approval.

Revision ID: 016_follow_requests
Revises: 015_profile_seller_privacy
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "016_follow_requests"
down_revision: Union[str, None] = "015_profile_seller_privacy"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Existing rows are all pre-existing immediate follows — backfill to "accepted".
    op.add_column("follows", sa.Column("status", sa.String(16), server_default="accepted", nullable=False))


def downgrade() -> None:
    op.drop_column("follows", "status")

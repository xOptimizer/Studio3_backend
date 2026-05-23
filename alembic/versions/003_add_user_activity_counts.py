"""Add user_activity_counts table for role-from-activity.

Revision ID: 003_add_user_activity_counts
Revises: 002_add_user_role
Create Date: 2025-02-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003_add_user_activity_counts"
down_revision: Union[str, None] = "002_add_user_role"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_activity_counts",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("post_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("purchase_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("save_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )


def downgrade() -> None:
    op.drop_table("user_activity_counts")

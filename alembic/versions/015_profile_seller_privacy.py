"""Profile fields (pronouns, banner/magnum opus), privacy (message permission,
profile visibility), notification preferences, and blocked accounts.

Revision ID: 015_profile_seller_privacy
Revises: 014_user_geo
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "015_profile_seller_privacy"
down_revision: Union[str, None] = "014_user_geo"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("pronouns", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("banner_target_type", sa.String(16), nullable=True))
    op.add_column("users", sa.Column("banner_target_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("users", sa.Column("banner_auto_rule", sa.String(16), server_default="none", nullable=False))
    op.add_column("users", sa.Column("message_permission", sa.String(16), server_default="everyone", nullable=False))
    op.add_column("users", sa.Column("profile_visibility", sa.String(16), server_default="public", nullable=False))
    op.add_column("users", sa.Column("notification_preferences", postgresql.JSONB(), nullable=True))

    op.create_table(
        "blocks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("blocker_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("blocked_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["blocker_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["blocked_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("blocker_id", "blocked_id", name="uq_block"),
    )
    op.create_index(op.f("ix_blocks_blocker_id"), "blocks", ["blocker_id"], unique=False)
    op.create_index(op.f("ix_blocks_blocked_id"), "blocks", ["blocked_id"], unique=False)


def downgrade() -> None:
    op.drop_table("blocks")
    op.drop_column("users", "notification_preferences")
    op.drop_column("users", "profile_visibility")
    op.drop_column("users", "message_permission")
    op.drop_column("users", "banner_auto_rule")
    op.drop_column("users", "banner_target_id")
    op.drop_column("users", "banner_target_type")
    op.drop_column("users", "pronouns")

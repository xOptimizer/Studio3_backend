"""Username auth fields and username_history.

Revision ID: 004_username_auth
Revises: 003_add_user_activity_counts
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "004_username_auth"
down_revision: Union[str, None] = "003_add_user_activity_counts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(30), nullable=True))
    op.add_column("users", sa.Column("cover_photo_url", sa.String(512), nullable=True))
    op.add_column("users", sa.Column("bio", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("location", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("seller_enabled", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("users", sa.Column("onboarding_complete", sa.Boolean(), server_default="false", nullable=False))
    op.add_column("users", sa.Column("taste_preferences", postgresql.JSONB(), nullable=True))
    op.add_column("users", sa.Column("last_username_change_at", sa.DateTime(timezone=True), nullable=True))

    # Backfill username from email local-part for existing rows
    op.execute(
        """
        UPDATE users
        SET username = LOWER(REGEXP_REPLACE(SPLIT_PART(email, '@', 1), '[^a-z0-9._]', '_', 'g'))
        WHERE username IS NULL
        """
    )
    op.execute(
        """
        UPDATE users u
        SET username = u.username || '_' || SUBSTRING(REPLACE(u.id::text, '-', ''), 1, 6)
        FROM (
            SELECT id, username,
                   ROW_NUMBER() OVER (PARTITION BY username ORDER BY created_at) AS rn
            FROM users
        ) d
        WHERE u.id = d.id AND d.rn > 1
        """
    )
    op.alter_column("users", "username", nullable=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "username_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(30), nullable=False),
        sa.Column("reserved_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index(op.f("ix_username_history_user_id"), "username_history", ["user_id"], unique=False)
    op.create_index(op.f("ix_username_history_username"), "username_history", ["username"], unique=True)
    op.create_index(op.f("ix_username_history_reserved_until"), "username_history", ["reserved_until"], unique=False)


def downgrade() -> None:
    op.drop_table("username_history")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_column("users", "last_username_change_at")
    op.drop_column("users", "taste_preferences")
    op.drop_column("users", "onboarding_complete")
    op.drop_column("users", "seller_enabled")
    op.drop_column("users", "location")
    op.drop_column("users", "bio")
    op.drop_column("users", "cover_photo_url")
    op.drop_column("users", "username")

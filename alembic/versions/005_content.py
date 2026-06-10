"""Pieces and posts tables.

Revision ID: 005_content
Revises: 004_username_auth
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "005_content"
down_revision: Union[str, None] = "004_username_auth"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pieces",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("media_url", sa.String(1024), nullable=False),
        sa.Column("media_type", sa.String(32), nullable=False),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("medium", sa.String(100), nullable=True),
        sa.Column("materials", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("style_tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("ai_disclosed", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("alt_text", sa.Text(), nullable=True),
        sa.Column("is_for_sale", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("price_cents", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(3), server_default="USD", nullable=False),
        sa.Column("dimensions", postgresql.JSONB(), nullable=True),
        sa.Column("shipping_region", sa.String(64), nullable=True),
        sa.Column("status", sa.String(32), server_default="live", nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pieces_user_id"), "pieces", ["user_id"], unique=False)

    op.create_table(
        "posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("media_url", sa.String(1024), nullable=False),
        sa.Column("media_type", sa.String(32), nullable=False),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("is_process", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("linked_piece_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(32), server_default="live", nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["linked_piece_id"], ["pieces.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_posts_user_id"), "posts", ["user_id"], unique=False)
    op.create_index(op.f("ix_posts_linked_piece_id"), "posts", ["linked_piece_id"], unique=False)


def downgrade() -> None:
    op.drop_table("posts")
    op.drop_table("pieces")

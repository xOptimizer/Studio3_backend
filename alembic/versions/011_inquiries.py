"""Inquiries (structured piece-scoped chat) tables.

Revision ID: 011_inquiries
Revises: 010_notifications_devices
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "011_inquiries"
down_revision: Union[str, None] = "010_notifications_devices"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "inquiries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("piece_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("buyer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("seller_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(16), server_default="open", nullable=False),
        sa.Column("buyer_read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("seller_read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["piece_id"], ["pieces.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["buyer_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["seller_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inquiries_piece_id"), "inquiries", ["piece_id"], unique=False)
    op.create_index(op.f("ix_inquiries_buyer_id"), "inquiries", ["buyer_id"], unique=False)
    op.create_index(op.f("ix_inquiries_seller_id"), "inquiries", ["seller_id"], unique=False)
    op.create_index(
        "ix_inquiries_buyer_last_message", "inquiries", ["buyer_id", "last_message_at"], unique=False
    )
    op.create_index(
        "ix_inquiries_seller_last_message", "inquiries", ["seller_id", "last_message_at"], unique=False
    )

    op.create_table(
        "inquiry_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("inquiry_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sender_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["inquiry_id"], ["inquiries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inquiry_messages_inquiry_id"), "inquiry_messages", ["inquiry_id"], unique=False)
    op.create_index(op.f("ix_inquiry_messages_sender_id"), "inquiry_messages", ["sender_id"], unique=False)


def downgrade() -> None:
    op.drop_table("inquiry_messages")
    op.drop_table("inquiries")

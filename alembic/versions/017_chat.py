"""General-purpose 1:1 chat (conversations + chat_messages) tables.

Revision ID: 017_chat
Revises: 016_follow_requests
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "017_chat"
down_revision: Union[str, None] = "016_follow_requests"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("participant_one_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("participant_two_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(16), server_default="open", nullable=False),
        sa.Column("participant_one_read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("participant_two_read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["participant_one_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["participant_two_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("participant_one_id", "participant_two_id", name="uq_conversations_participants"),
    )
    op.create_index(op.f("ix_conversations_participant_one_id"), "conversations", ["participant_one_id"], unique=False)
    op.create_index(op.f("ix_conversations_participant_two_id"), "conversations", ["participant_two_id"], unique=False)

    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sender_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("body IS NOT NULL OR image_url IS NOT NULL", name="ck_chat_messages_body_or_image"),
    )
    op.create_index(op.f("ix_chat_messages_conversation_id"), "chat_messages", ["conversation_id"], unique=False)
    op.create_index(op.f("ix_chat_messages_sender_id"), "chat_messages", ["sender_id"], unique=False)


def downgrade() -> None:
    op.drop_table("chat_messages")
    op.drop_table("conversations")

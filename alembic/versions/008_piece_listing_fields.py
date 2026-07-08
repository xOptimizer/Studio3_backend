"""Add first-class listing fields to pieces.

Revision ID: 008_piece_listing_fields
Revises: 007_user_phone
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "008_piece_listing_fields"
down_revision: Union[str, None] = "007_user_phone"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("pieces", sa.Column("year_created", sa.Integer(), nullable=True))
    op.add_column("pieces", sa.Column("framing_mounting", sa.Text(), nullable=True))
    op.add_column("pieces", sa.Column("provenance", sa.Text(), nullable=True))
    op.add_column("pieces", sa.Column("handling_notes", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("pieces", "handling_notes")
    op.drop_column("pieces", "provenance")
    op.drop_column("pieces", "framing_mounting")
    op.drop_column("pieces", "year_created")

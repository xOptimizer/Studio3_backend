"""Order / OrderItem — checkout without real payment capture (see orders_controller.confirm)."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB

from src.shared.config.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    # Denormalized; v1 checkout is one piece at a time so an order always has a single seller.
    seller_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(24), default="pending_payment", nullable=False)  # pending_payment|paid|shipped|completed|cancelled
    shipping_method = Column(String(16), nullable=False)  # standard|express|overnight|free
    # Denormalized copy of the chosen Address's fields at order time — NOT a FK, so
    # later edits to the saved address never change historical orders.
    shipping_address_snapshot = Column(JSONB, nullable=False)
    artwork_cents = Column(Integer, nullable=False)
    shipping_cents = Column(Integer, nullable=False)
    tax_cents = Column(Integer, nullable=False)
    total_cents = Column(Integer, nullable=False)
    payment_provider = Column(String(32), nullable=True)  # null while unconfigured; e.g. "stripe" later
    payment_reference = Column(String(255), nullable=True)  # future PaymentIntent id
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    # RESTRICT (not CASCADE like elsewhere): pieces are only ever soft-deleted
    # (deleted_at) in this codebase, never hard-deleted, so this is defensive, not
    # something any current code path exercises.
    piece_id = Column(UUID(as_uuid=True), ForeignKey("pieces.id", ondelete="RESTRICT"), nullable=False, index=True)
    price_cents = Column(Integer, nullable=False)  # snapshot at order time
    quantity = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)

"""Orders DAO."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session

from src.shared.models.order import Order, OrderItem
from src.shared.models.piece import Piece

# Orders in these statuses represent a completed sale/purchase — excludes
# pending_payment (not yet paid) and cancelled.
COMPLETED_STATUSES = ("paid", "shipped", "completed")


def create_order(
    db: Session,
    buyer_id: uuid.UUID,
    seller_id: uuid.UUID,
    piece: Piece,
    shipping_method: str,
    address_snapshot: dict,
    artwork_cents: int,
    shipping_cents: int,
    tax_cents: int,
    total_cents: int,
) -> Order:
    order = Order(
        id=uuid.uuid4(),
        buyer_id=buyer_id,
        seller_id=seller_id,
        shipping_method=shipping_method,
        shipping_address_snapshot=address_snapshot,
        artwork_cents=artwork_cents,
        shipping_cents=shipping_cents,
        tax_cents=tax_cents,
        total_cents=total_cents,
    )
    db.add(order)
    db.flush()
    db.add(OrderItem(id=uuid.uuid4(), order_id=order.id, piece_id=piece.id, price_cents=artwork_cents))
    piece.status = "reserved"
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: uuid.UUID) -> Optional[Order]:
    return db.get(Order, order_id)


def list_items(db: Session, order_id: uuid.UUID) -> list[OrderItem]:
    return list(db.execute(select(OrderItem).where(OrderItem.order_id == order_id)).scalars().all())


def list_buyer_orders(
    db: Session, buyer_id: uuid.UUID, limit: int = 20, before: Optional[datetime] = None
) -> list[Order]:
    q = select(Order).where(Order.buyer_id == buyer_id)
    if before:
        q = q.where(Order.created_at < before)
    return list(db.execute(q.order_by(Order.created_at.desc()).limit(limit)).scalars().all())


def list_seller_orders(
    db: Session, seller_id: uuid.UUID, limit: int = 20, before: Optional[datetime] = None
) -> list[Order]:
    q = select(Order).where(Order.seller_id == seller_id)
    if before:
        q = q.where(Order.created_at < before)
    return list(db.execute(q.order_by(Order.created_at.desc()).limit(limit)).scalars().all())


def count_buyer_collected(db: Session, buyer_id: uuid.UUID) -> int:
    """Number of pieces a buyer has successfully purchased (paid/shipped/completed orders)."""
    return db.execute(
        select(func.count(Order.id)).where(
            Order.buyer_id == buyer_id, Order.status.in_(COMPLETED_STATUSES)
        )
    ).scalar_one()


def count_seller_sales(db: Session, seller_id: uuid.UUID) -> int:
    """Number of completed sales for a seller (paid/shipped/completed orders)."""
    return db.execute(
        select(func.count(Order.id)).where(
            Order.seller_id == seller_id, Order.status.in_(COMPLETED_STATUSES)
        )
    ).scalar_one()


def order_to_dict(db: Session, order: Order) -> dict:
    items = list_items(db, order.id)
    return {
        "id": str(order.id),
        "buyerId": str(order.buyer_id),
        "sellerId": str(order.seller_id),
        "status": order.status,
        "shippingMethod": order.shipping_method,
        "shippingAddress": order.shipping_address_snapshot,
        "artworkCents": order.artwork_cents,
        "shippingCents": order.shipping_cents,
        "taxCents": order.tax_cents,
        "totalCents": order.total_cents,
        "paymentProvider": order.payment_provider,
        "items": [
            {"pieceId": str(i.piece_id), "priceCents": i.price_cents, "quantity": i.quantity} for i in items
        ],
        "createdAt": order.created_at.isoformat(),
        "updatedAt": order.updated_at.isoformat(),
    }

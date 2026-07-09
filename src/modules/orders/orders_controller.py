"""Orders controller — checkout lifecycle without real payment capture."""
import os
import uuid
from datetime import datetime

from flask import request, g

from src.shared.config.database import SessionLocal
from src.shared.utils.app_error import AppError
from src.modules.user.user_dao import get_user_by_id
from src.modules.pieces.pieces_dao import get_piece
from src.modules.addresses import addresses_dao
from src.modules.orders import orders_dao
from src.modules.orders.shipping import SHIPPING_RATES_CENTS, FLAT_TAX_RATE
from src.modules.notifications import notifications_dao

VALID_TRANSITIONS = {
    "paid": {"shipped", "cancelled"},
    "shipped": {"completed"},
    "pending_payment": {"cancelled"},
}


def get_shipping_quote(piece_id: str):
    db = SessionLocal()
    try:
        piece = get_piece(db, uuid.UUID(piece_id))
        if not piece:
            raise AppError("Piece not found.", 404)
        methods = [{"id": method, "cents": cents} for method, cents in SHIPPING_RATES_CENTS.items()]
        return {"methods": methods}, 200
    finally:
        db.close()


def collect(piece_id: str):
    body = request.get_json() or {}
    address_id = body.get("addressId")
    shipping_method = (body.get("shippingMethod") or "").strip().lower()
    if not address_id:
        raise AppError("addressId is required.", 400)
    if shipping_method not in SHIPPING_RATES_CENTS:
        raise AppError(f"shippingMethod must be one of: {', '.join(SHIPPING_RATES_CENTS)}", 400)
    db = SessionLocal()
    try:
        buyer = get_user_by_id(db, uuid.UUID(g.user["id"]))
        piece = get_piece(db, uuid.UUID(piece_id))
        if not piece:
            raise AppError("Piece not found.", 404)
        if piece.user_id == buyer.id:
            raise AppError("Cannot purchase your own piece.", 400)
        if not piece.is_for_sale or piece.status != "live":
            raise AppError("This piece is no longer available.", 409)
        if not piece.price_cents:
            raise AppError("This piece has no price set.", 400)

        address = addresses_dao.get_address(db, uuid.UUID(address_id))
        if not address or address.user_id != buyer.id:
            raise AppError("Address not found.", 404)

        artwork_cents = piece.price_cents
        shipping_cents = SHIPPING_RATES_CENTS[shipping_method]
        tax_cents = round(artwork_cents * FLAT_TAX_RATE)
        total_cents = artwork_cents + shipping_cents + tax_cents

        order = orders_dao.create_order(
            db,
            buyer_id=buyer.id,
            seller_id=piece.user_id,
            piece=piece,
            shipping_method=shipping_method,
            address_snapshot=addresses_dao.address_snapshot(address),
            artwork_cents=artwork_cents,
            shipping_cents=shipping_cents,
            tax_cents=tax_cents,
            total_cents=total_cents,
        )
        result = orders_dao.order_to_dict(db, order)
        result["clientSecret"] = None  # placeholder — populated once a payment provider is wired up
        return result, 201
    finally:
        db.close()


def confirm(order_id: str):
    db = SessionLocal()
    try:
        buyer_id = uuid.UUID(g.user["id"])
        order = orders_dao.get_order(db, uuid.UUID(order_id))
        if not order or order.buyer_id != buyer_id:
            raise AppError("Order not found.", 404)
        if order.status != "pending_payment":
            raise AppError("This order has already been processed.", 409)

        if not os.getenv("STRIPE_SECRET_KEY"):
            # Dev mode: no payment provider configured — auto-succeed so the rest of the
            # order lifecycle (inventory lock, history, notifications) is testable today.
            order.status = "paid"
            items = orders_dao.list_items(db, order.id)
            for item in items:
                piece = get_piece(db, item.piece_id)
                if piece:
                    piece.status = "sold"
            db.commit()
            db.refresh(order)

            buyer = get_user_by_id(db, order.buyer_id)
            seller = get_user_by_id(db, order.seller_id)
            piece_title = None
            if items:
                piece = get_piece(db, items[0].piece_id)
                piece_title = piece.title if piece else None
            notifications_dao.create_and_push(
                db,
                user_id=order.seller_id,
                type="purchase",
                actor_id=order.buyer_id,
                target_type="order",
                target_id=order.id,
                payload={"pieceTitle": piece_title, "totalCents": order.total_cents},
                title="You made a sale!",
                body=f"{buyer.name} purchased '{piece_title}'" if piece_title else f"{buyer.name} completed a purchase",
            )
            notifications_dao.create_and_push(
                db,
                user_id=order.buyer_id,
                type="purchase",
                actor_id=order.seller_id,
                target_type="order",
                target_id=order.id,
                payload={"pieceTitle": piece_title},
                title="Order confirmed",
                body=f"Your order for '{piece_title}' is confirmed" if piece_title else "Your order is confirmed",
            )
            result = orders_dao.order_to_dict(db, order)
            result["devMode"] = True
            return result, 200

        raise AppError("Payment provider not yet implemented.", 501)
    finally:
        db.close()


def _require_participant(order, user_id):
    if not order or (order.buyer_id != user_id and order.seller_id != user_id):
        raise AppError("Order not found.", 404)


def get_detail(order_id: str):
    db = SessionLocal()
    try:
        user_id = uuid.UUID(g.user["id"])
        order = orders_dao.get_order(db, uuid.UUID(order_id))
        _require_participant(order, user_id)
        return orders_dao.order_to_dict(db, order), 200
    finally:
        db.close()


def patch(order_id: str):
    body = request.get_json() or {}
    new_status = (body.get("status") or "").strip().lower()
    if not new_status:
        raise AppError("status is required.", 400)
    db = SessionLocal()
    try:
        user_id = uuid.UUID(g.user["id"])
        order = orders_dao.get_order(db, uuid.UUID(order_id))
        _require_participant(order, user_id)

        if new_status == "cancelled":
            if order.status not in ("pending_payment", "paid"):
                raise AppError(f"Cannot cancel an order in status '{order.status}'.", 400)
        else:
            if order.seller_id != user_id:
                raise AppError("Only the seller can update shipment status.", 403)
            allowed = VALID_TRANSITIONS.get(order.status, set())
            if new_status not in allowed:
                raise AppError(f"Cannot transition order from '{order.status}' to '{new_status}'.", 400)

        order.status = new_status
        if new_status == "cancelled":
            for item in orders_dao.list_items(db, order.id):
                piece = get_piece(db, item.piece_id)
                if piece and piece.status in ("reserved", "sold"):
                    piece.status = "live"
        db.commit()
        db.refresh(order)
        return orders_dao.order_to_dict(db, order), 200
    finally:
        db.close()


def list_my_orders():
    cursor = request.args.get("cursor")
    limit = min(int(request.args.get("limit", 20)), 50)
    db = SessionLocal()
    try:
        user_id = uuid.UUID(g.user["id"])
        before = datetime.fromisoformat(cursor) if cursor else None
        orders = orders_dao.list_buyer_orders(db, user_id, limit=limit + 1, before=before)
        has_more = len(orders) > limit
        orders = orders[:limit]
        items = [orders_dao.order_to_dict(db, o) for o in orders]
        next_cursor = orders[-1].created_at.isoformat() if has_more and orders else None
        return {"items": items, "nextCursor": next_cursor}, 200
    finally:
        db.close()


def list_my_sales():
    cursor = request.args.get("cursor")
    limit = min(int(request.args.get("limit", 20)), 50)
    db = SessionLocal()
    try:
        user_id = uuid.UUID(g.user["id"])
        before = datetime.fromisoformat(cursor) if cursor else None
        orders = orders_dao.list_seller_orders(db, user_id, limit=limit + 1, before=before)
        has_more = len(orders) > limit
        orders = orders[:limit]
        items = [orders_dao.order_to_dict(db, o) for o in orders]
        next_cursor = orders[-1].created_at.isoformat() if has_more and orders else None
        return {"items": items, "nextCursor": next_cursor}, 200
    finally:
        db.close()

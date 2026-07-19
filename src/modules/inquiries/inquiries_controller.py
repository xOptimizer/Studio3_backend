"""Inquiries controller."""
import base64
import uuid
from datetime import datetime

from flask import request, g
from sqlalchemy import select

from src.shared.config.database import SessionLocal
from src.shared.models.user import User
from src.shared.utils.app_error import AppError
from src.modules.user.user_dao import get_user_by_id
from src.modules.pieces.pieces_dao import get_piece
from src.modules.inquiries import inquiries_dao
from src.modules.notifications import notifications_dao
from src.modules.social import social_dao
from src.modules.social import block_dao


def _encode_cursor(created_at, item_id) -> str:
    raw = f"{created_at.isoformat()}|{item_id}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def _decode_cursor(cursor: str):
    try:
        raw = base64.urlsafe_b64decode(cursor.encode()).decode()
        ts_str, id_str = raw.split("|", 1)
        return datetime.fromisoformat(ts_str), uuid.UUID(id_str)
    except Exception:
        return None


def list_inbox():
    cursor = request.args.get("cursor")
    limit = min(int(request.args.get("limit", 20)), 50)
    db = SessionLocal()
    try:
        me_id = uuid.UUID(g.user["id"])
        before = _decode_cursor(cursor) if cursor else None
        inquiries = inquiries_dao.list_inbox(db, me_id, limit=limit + 1, before=before)
        has_more = len(inquiries) > limit
        inquiries = inquiries[:limit]
        items = []
        for inquiry in inquiries:
            piece = get_piece(db, inquiry.piece_id)
            other_id = inquiry.seller_id if inquiry.buyer_id == me_id else inquiry.buyer_id
            other_user = get_user_by_id(db, other_id)
            last_msg = inquiries_dao.list_messages(db, inquiry.id, limit=1)
            preview = last_msg[0].body[:140] if last_msg else None
            items.append(inquiries_dao.inquiry_to_inbox_dict(inquiry, me_id, piece, other_user, preview))
        next_cursor = (
            _encode_cursor(inquiries[-1].last_message_at, inquiries[-1].id)
            if has_more and inquiries
            else None
        )
        return {"items": items, "nextCursor": next_cursor}, 200
    finally:
        db.close()


def list_requests():
    cursor = request.args.get("cursor")
    limit = min(int(request.args.get("limit", 20)), 50)
    db = SessionLocal()
    try:
        me_id = uuid.UUID(g.user["id"])
        before = _decode_cursor(cursor) if cursor else None
        inquiries = inquiries_dao.list_requests(db, me_id, limit=limit + 1, before=before)
        has_more = len(inquiries) > limit
        inquiries = inquiries[:limit]
        items = []
        for inquiry in inquiries:
            piece = get_piece(db, inquiry.piece_id)
            buyer = get_user_by_id(db, inquiry.buyer_id)
            last_msg = inquiries_dao.list_messages(db, inquiry.id, limit=1)
            preview = last_msg[0].body[:140] if last_msg else None
            items.append(inquiries_dao.inquiry_to_inbox_dict(inquiry, me_id, piece, buyer, preview))
        next_cursor = (
            _encode_cursor(inquiries[-1].last_message_at, inquiries[-1].id)
            if has_more and inquiries
            else None
        )
        return {"items": items, "nextCursor": next_cursor}, 200
    finally:
        db.close()


def _require_participant(inquiry, user_id):
    if not inquiry or (inquiry.buyer_id != user_id and inquiry.seller_id != user_id):
        raise AppError("Inquiry not found.", 404)


def get_thread(inquiry_id: str):
    cursor = request.args.get("cursor")
    limit = min(int(request.args.get("limit", 50)), 100)
    db = SessionLocal()
    try:
        me_id = uuid.UUID(g.user["id"])
        inquiry = inquiries_dao.get_inquiry(db, uuid.UUID(inquiry_id))
        _require_participant(inquiry, me_id)
        before = datetime.fromisoformat(cursor) if cursor else None
        messages = inquiries_dao.list_messages(db, inquiry.id, limit=limit + 1, before=before)
        has_more = len(messages) > limit
        messages = messages[:limit]
        sender_ids = {m.sender_id for m in messages}
        senders = {}
        if sender_ids:
            senders = {u.id: u for u in db.execute(select(User).where(User.id.in_(sender_ids))).scalars()}
        items = [inquiries_dao.message_to_dict(m, senders.get(m.sender_id)) for m in messages]
        next_cursor = messages[-1].created_at.isoformat() if has_more and messages else None
        inquiries_dao.mark_read(db, inquiry, me_id)
        piece = get_piece(db, inquiry.piece_id)
        other_id = inquiry.seller_id if inquiry.buyer_id == me_id else inquiry.buyer_id
        other_user = get_user_by_id(db, other_id)
        return {
            "id": str(inquiry.id),
            "piece": {"id": str(piece.id), "title": piece.title, "thumbnailUrl": piece.media_url} if piece else None,
            "otherParty": {"username": other_user.username, "name": other_user.name, "profilePhotoUrl": other_user.image} if other_user else None,
            "status": inquiry.status,
            "messages": {"items": items, "nextCursor": next_cursor},
        }, 200
    finally:
        db.close()


def create_inquiry():
    body = request.get_json() or {}
    piece_id = body.get("pieceId")
    message_text = (body.get("message") or "").strip()
    if not piece_id or not message_text:
        raise AppError("pieceId and message are required.", 400)
    db = SessionLocal()
    try:
        me = get_user_by_id(db, uuid.UUID(g.user["id"]))
        piece = get_piece(db, uuid.UUID(piece_id))
        if not piece:
            raise AppError("Piece not found.", 404)
        if piece.user_id == me.id:
            raise AppError("Cannot inquire on your own piece.", 400)
        if block_dao.is_blocked_either_way(db, me.id, piece.user_id):
            raise AppError("Piece not found.", 404)

        seller = get_user_by_id(db, piece.user_id)
        seller_follows_buyer = social_dao.user_follows(db, seller.id, me.id)

        if seller.message_permission == "no_one":
            raise AppError("This seller isn't accepting messages right now.", 403)
        if seller.message_permission == "following" and not seller_follows_buyer:
            raise AppError("This seller only accepts messages from people they follow.", 403)

        existing = inquiries_dao.find_open_inquiry(db, piece.id, me.id)
        if existing:
            return {"id": str(existing.id), "reused": True}, 200

        # Instagram-style requests: if the seller doesn't already follow the buyer,
        # the thread starts "pending" (seller's Requests folder) until they accept or reply.
        initial_status = "open" if seller_follows_buyer else "pending"
        inquiry = inquiries_dao.create_inquiry(db, piece.id, me.id, piece.user_id, status=initial_status)
        inquiries_dao.create_message(db, inquiry, me.id, message_text[:2000])
        notifications_dao.create_and_push(
            db,
            user_id=piece.user_id,
            type="inquiry",
            actor_id=me.id,
            target_type="inquiry",
            target_id=inquiry.id,
            payload={"pieceTitle": piece.title, "message": message_text[:140]},
            title="New message request" if initial_status == "pending" else "New inquiry",
            body=f"{me.name} asked about '{piece.title}'",
        )
        return {"id": str(inquiry.id), "reused": False, "status": initial_status}, 201
    finally:
        db.close()


def reply(inquiry_id: str):
    body = request.get_json() or {}
    text = (body.get("body") or "").strip()
    if not text:
        raise AppError("Message body is required.", 400)
    db = SessionLocal()
    try:
        me_id = uuid.UUID(g.user["id"])
        inquiry = inquiries_dao.get_inquiry(db, uuid.UUID(inquiry_id))
        _require_participant(inquiry, me_id)
        if inquiry.status == "closed":
            raise AppError("This inquiry is closed.", 400)
        if inquiry.status == "pending" and inquiry.seller_id == me_id:
            # Replying to a pending request implicitly accepts it (matches Instagram).
            inquiries_dao.accept_inquiry(db, inquiry)
        message = inquiries_dao.create_message(db, inquiry, me_id, text[:2000])
        other_id = inquiry.seller_id if inquiry.buyer_id == me_id else inquiry.buyer_id
        sender = get_user_by_id(db, me_id)
        notifications_dao.create_and_push(
            db,
            user_id=other_id,
            type="inquiry",
            actor_id=me_id,
            target_type="inquiry",
            target_id=inquiry.id,
            payload={"message": text[:140]},
            title="New message",
            body=f"{sender.name}: {text[:100]}",
        )
        return inquiries_dao.message_to_dict(message, sender), 201
    finally:
        db.close()


def accept(inquiry_id: str):
    db = SessionLocal()
    try:
        me_id = uuid.UUID(g.user["id"])
        inquiry = inquiries_dao.get_inquiry(db, uuid.UUID(inquiry_id))
        _require_participant(inquiry, me_id)
        if inquiry.seller_id != me_id:
            raise AppError("Only the seller can accept a request.", 403)
        if inquiry.status != "pending":
            raise AppError(f"Cannot accept an inquiry in status '{inquiry.status}'.", 400)
        inquiries_dao.accept_inquiry(db, inquiry)
        return {"status": "open"}, 200
    finally:
        db.close()


def decline(inquiry_id: str):
    db = SessionLocal()
    try:
        me_id = uuid.UUID(g.user["id"])
        inquiry = inquiries_dao.get_inquiry(db, uuid.UUID(inquiry_id))
        _require_participant(inquiry, me_id)
        if inquiry.seller_id != me_id:
            raise AppError("Only the seller can decline a request.", 403)
        if inquiry.status != "pending":
            raise AppError(f"Cannot decline an inquiry in status '{inquiry.status}'.", 400)
        inquiries_dao.decline_inquiry(db, inquiry)
        return {"status": "closed"}, 200
    finally:
        db.close()


def mark_read(inquiry_id: str):
    db = SessionLocal()
    try:
        me_id = uuid.UUID(g.user["id"])
        inquiry = inquiries_dao.get_inquiry(db, uuid.UUID(inquiry_id))
        _require_participant(inquiry, me_id)
        inquiries_dao.mark_read(db, inquiry, me_id)
        return {"read": True}, 200
    finally:
        db.close()

"""Inquiries DAO."""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, or_, and_, tuple_, func
from sqlalchemy.orm import Session

from src.shared.models.inquiry import Inquiry, InquiryMessage
from src.shared.models.piece import Piece
from src.shared.models.user import User


def utc_now():
    return datetime.now(timezone.utc)


def count_seller_inquiries(db: Session, seller_id: uuid.UUID) -> int:
    """Number of inquiry threads received by a seller."""
    return db.execute(
        select(func.count(Inquiry.id)).where(Inquiry.seller_id == seller_id)
    ).scalar_one()


def create_inquiry(
    db: Session, piece_id: uuid.UUID, buyer_id: uuid.UUID, seller_id: uuid.UUID, status: str = "open"
) -> Inquiry:
    inquiry = Inquiry(id=uuid.uuid4(), piece_id=piece_id, buyer_id=buyer_id, seller_id=seller_id, status=status)
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)
    return inquiry


def find_open_inquiry(db: Session, piece_id: uuid.UUID, buyer_id: uuid.UUID) -> Optional[Inquiry]:
    """An existing non-closed thread (open or pending) — reused instead of creating a duplicate."""
    return db.execute(
        select(Inquiry).where(
            Inquiry.piece_id == piece_id,
            Inquiry.buyer_id == buyer_id,
            Inquiry.status.in_(("open", "pending")),
        )
    ).scalar_one_or_none()


def get_inquiry(db: Session, inquiry_id: uuid.UUID) -> Optional[Inquiry]:
    return db.get(Inquiry, inquiry_id)


def list_inbox(
    db: Session, user_id: uuid.UUID, limit: int = 20, before: Optional[tuple] = None
) -> list[Inquiry]:
    """Primary inbox: the caller's own outgoing threads (any status — a buyer always sees
    their own request, pending or not) plus threads where the caller is the seller AND
    already accepted (status="open"). Pending seller-side threads live in list_requests()
    instead, matching the Instagram-style "message requests" split."""
    q = select(Inquiry).where(
        or_(
            Inquiry.buyer_id == user_id,
            and_(Inquiry.seller_id == user_id, Inquiry.status == "open"),
        )
    )
    if before:
        before_ts, before_id = before
        q = q.where(tuple_(Inquiry.last_message_at, Inquiry.id) < tuple_(before_ts, before_id))
    return list(
        db.execute(
            q.order_by(Inquiry.last_message_at.desc(), Inquiry.id.desc()).limit(limit)
        ).scalars().all()
    )


def list_requests(
    db: Session, seller_id: uuid.UUID, limit: int = 20, before: Optional[tuple] = None
) -> list[Inquiry]:
    """Seller-only "requests" folder: pending threads awaiting accept/decline."""
    q = select(Inquiry).where(Inquiry.seller_id == seller_id, Inquiry.status == "pending")
    if before:
        before_ts, before_id = before
        q = q.where(tuple_(Inquiry.last_message_at, Inquiry.id) < tuple_(before_ts, before_id))
    return list(
        db.execute(
            q.order_by(Inquiry.last_message_at.desc(), Inquiry.id.desc()).limit(limit)
        ).scalars().all()
    )


def accept_inquiry(db: Session, inquiry: Inquiry) -> None:
    inquiry.status = "open"
    db.commit()


def decline_inquiry(db: Session, inquiry: Inquiry) -> None:
    inquiry.status = "closed"
    db.commit()


def create_message(db: Session, inquiry: Inquiry, sender_id: uuid.UUID, body: str) -> InquiryMessage:
    message = InquiryMessage(id=uuid.uuid4(), inquiry_id=inquiry.id, sender_id=sender_id, body=body)
    db.add(message)
    inquiry.last_message_at = utc_now()
    db.commit()
    db.refresh(message)
    return message


def list_messages(
    db: Session, inquiry_id: uuid.UUID, limit: int = 50, before: Optional[datetime] = None
) -> list[InquiryMessage]:
    q = select(InquiryMessage).where(InquiryMessage.inquiry_id == inquiry_id)
    if before:
        q = q.where(InquiryMessage.created_at < before)
    return list(
        db.execute(q.order_by(InquiryMessage.created_at.desc()).limit(limit)).scalars().all()
    )


def mark_read(db: Session, inquiry: Inquiry, reader_id: uuid.UUID) -> None:
    now = utc_now()
    if inquiry.buyer_id == reader_id:
        inquiry.buyer_read_at = now
    elif inquiry.seller_id == reader_id:
        inquiry.seller_read_at = now
    db.commit()


def is_unread_for(inquiry: Inquiry, viewer_id: uuid.UUID) -> bool:
    my_read_at = inquiry.buyer_read_at if inquiry.buyer_id == viewer_id else inquiry.seller_read_at
    if my_read_at is None:
        return True
    return inquiry.last_message_at > my_read_at


def inquiry_to_inbox_dict(inquiry: Inquiry, viewer_id: uuid.UUID, piece: Optional[Piece], other_user: Optional[User], preview: Optional[str]) -> dict:
    return {
        "id": str(inquiry.id),
        "piece": (
            {"id": str(piece.id), "title": piece.title, "thumbnailUrl": piece.media_url} if piece else None
        ),
        "otherParty": (
            {"username": other_user.username, "name": other_user.name, "profilePhotoUrl": other_user.image}
            if other_user
            else None
        ),
        "preview": preview,
        "updatedAt": inquiry.last_message_at.isoformat(),
        "unread": is_unread_for(inquiry, viewer_id),
        "status": inquiry.status,
    }


def message_to_dict(message: InquiryMessage, sender: Optional[User]) -> dict:
    return {
        "id": str(message.id),
        "body": message.body,
        "sender": (
            {"username": sender.username, "name": sender.name, "profilePhotoUrl": sender.image}
            if sender
            else None
        ),
        "createdAt": message.created_at.isoformat(),
    }

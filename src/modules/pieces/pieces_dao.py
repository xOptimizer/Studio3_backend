"""Pieces DAO and serializers."""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.shared.models.piece import Piece


def create_piece(db: Session, **kwargs) -> Piece:
    piece = Piece(id=uuid.uuid4(), **kwargs)
    db.add(piece)
    db.commit()
    db.refresh(piece)
    return piece


def get_piece(db: Session, piece_id: uuid.UUID) -> Optional[Piece]:
    return db.execute(
        select(Piece).where(Piece.id == piece_id, Piece.deleted_at.is_(None))
    ).scalar_one_or_none()


def list_user_pieces(db: Session, user_id: uuid.UUID, for_sale_only: bool = False) -> list[Piece]:
    q = select(Piece).where(Piece.user_id == user_id, Piece.deleted_at.is_(None), Piece.status != "draft")
    if for_sale_only:
        q = q.where(Piece.is_for_sale == True, Piece.status == "live")
    return list(db.execute(q.order_by(Piece.created_at.desc())).scalars().all())


def piece_to_dict(piece: Piece) -> dict:
    return {
        "id": str(piece.id),
        "userId": str(piece.user_id),
        "title": piece.title,
        "mediaUrl": piece.media_url,
        "mediaType": piece.media_type,
        "caption": piece.caption,
        "medium": piece.medium,
        "materials": piece.materials or [],
        "styleTags": piece.style_tags or [],
        "aiDisclosed": piece.ai_disclosed,
        "altText": piece.alt_text,
        "isForSale": piece.is_for_sale,
        "priceCents": piece.price_cents,
        "currency": piece.currency,
        "dimensions": piece.dimensions,
        "shippingRegion": piece.shipping_region,
        "status": piece.status,
        "createdAt": piece.created_at.isoformat(),
    }

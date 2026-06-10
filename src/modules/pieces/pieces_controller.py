"""Pieces controller."""
import uuid

from flask import request, g

from src.shared.config.database import SessionLocal
from src.shared.storage.s3_service import validate_user_media_url
from src.shared.utils.app_error import AppError
from src.modules.auth.auth_dao import find_user_by_username
from src.modules.user.user_dao import get_user_by_id
from src.modules.pieces.pieces_dao import create_piece, get_piece, list_user_pieces, piece_to_dict


def _validate_sale_fields(body, seller_enabled: bool):
    if not body.get("isForSale"):
        return
    if not seller_enabled:
        raise AppError("Enable seller mode before listing for sale.", 403)
    price = body.get("priceCents")
    if not price or int(price) < 100:
        raise AppError("Price must be at least $1.00 (100 cents).", 400)
    if not body.get("medium"):
        raise AppError("Medium is required for sale listings.", 400)
    if not body.get("dimensions"):
        raise AppError("Dimensions are required for sale listings.", 400)
    if not body.get("shippingRegion"):
        raise AppError("Shipping region is required for sale listings.", 400)


def create():
    body = request.get_json() or {}
    db = SessionLocal()
    try:
        user = get_user_by_id(db, uuid.UUID(g.user["id"]))
        media_url = body.get("mediaUrl")
        if not media_url:
            raise AppError("mediaUrl is required.", 400)
        validate_user_media_url(user.username, media_url)
        _validate_sale_fields(body, user.seller_enabled)
        piece = create_piece(
            db,
            user_id=user.id,
            title=(body.get("title") or "Untitled")[:200],
            media_url=media_url,
            media_type=body.get("mediaType", "image"),
            caption=body.get("caption"),
            medium=body.get("medium"),
            materials=body.get("materials"),
            style_tags=body.get("styleTags"),
            ai_disclosed=bool(body.get("aiDisclosed", False)),
            alt_text=body.get("altText"),
            is_for_sale=bool(body.get("isForSale", False)),
            price_cents=body.get("priceCents"),
            currency=body.get("currency", "USD"),
            dimensions=body.get("dimensions"),
            shipping_region=body.get("shippingRegion"),
            status="live",
        )
        return piece_to_dict(piece), 201
    finally:
        db.close()


def get_detail(piece_id: str):
    db = SessionLocal()
    try:
        piece = get_piece(db, uuid.UUID(piece_id))
        if not piece:
            raise AppError("Piece not found.", 404)
        return piece_to_dict(piece), 200
    finally:
        db.close()


def patch(piece_id: str):
    body = request.get_json() or {}
    db = SessionLocal()
    try:
        user = get_user_by_id(db, uuid.UUID(g.user["id"]))
        piece = get_piece(db, uuid.UUID(piece_id))
        if not piece or piece.user_id != user.id:
            raise AppError("Piece not found.", 404)
        if "mediaUrl" in body and body["mediaUrl"]:
            validate_user_media_url(user.username, body["mediaUrl"])
            piece.media_url = body["mediaUrl"]
        for attr, key in [
            ("title", "title"), ("caption", "caption"), ("medium", "medium"),
            ("alt_text", "altText"), ("shipping_region", "shippingRegion"),
        ]:
            if key in body:
                setattr(piece, attr, body[key])
        if "materials" in body:
            piece.materials = body["materials"]
        if "styleTags" in body:
            piece.style_tags = body["styleTags"]
        if "isForSale" in body:
            _validate_sale_fields({**piece_to_dict(piece), **body, "isForSale": body["isForSale"]}, user.seller_enabled)
            piece.is_for_sale = bool(body["isForSale"])
        if "priceCents" in body:
            piece.price_cents = body["priceCents"]
        if "dimensions" in body:
            piece.dimensions = body["dimensions"]
        if "status" in body:
            piece.status = body["status"]
        db.commit()
        db.refresh(piece)
        return piece_to_dict(piece), 200
    finally:
        db.close()


def list_for_user(username: str, for_sale_only: bool = False):
    db = SessionLocal()
    try:
        user = find_user_by_username(db, username.lower())
        if not user:
            raise AppError("User not found.", 404)
        pieces = list_user_pieces(db, user.id, for_sale_only=for_sale_only)
        return [piece_to_dict(p) for p in pieces], 200
    finally:
        db.close()

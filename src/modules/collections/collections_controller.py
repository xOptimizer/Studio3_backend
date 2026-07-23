"""Collections controller."""
import uuid

from flask import request, g

from src.shared.config.database import SessionLocal
from src.shared.utils.app_error import AppError
from src.modules.user.user_dao import get_user_by_id
from src.modules.pieces.pieces_dao import get_piece
from src.modules.posts.posts_dao import get_post
from src.modules.collections import collections_dao

_VALID_TARGET_TYPES = ("piece", "post")


def _get_target(db, target_type: str, target_id: uuid.UUID):
    if target_type == "piece":
        return get_piece(db, target_id)
    if target_type == "post":
        return get_post(db, target_id)
    return None


def _cover_dict(db, item) -> dict | None:
    if item is None:
        return None
    target = _get_target(db, item.target_type, item.target_id)
    if not target:
        return None
    return {
        "targetType": item.target_type,
        "targetId": str(item.target_id),
        "mediaUrl": target.media_url,
    }


def _collection_summary_dict(db, collection) -> dict:
    return {
        "id": str(collection.id),
        "name": collection.name,
        "createdAt": collection.created_at.isoformat(),
        "itemCount": collections_dao.count_items(db, collection.id),
        "cover": _cover_dict(db, collections_dao.most_recent_item(db, collection.id)),
    }


def _require_owned_collection(db, collection_id: uuid.UUID, user_id: uuid.UUID):
    collection = collections_dao.get_collection(db, collection_id)
    if not collection or collection.user_id != user_id:
        raise AppError("Collection not found.", 404)
    return collection


def list_for_me():
    db = SessionLocal()
    try:
        user_id = uuid.UUID(g.user["id"])
        collections = collections_dao.list_user_collections(db, user_id)
        return [_collection_summary_dict(db, c) for c in collections], 200
    finally:
        db.close()


def create():
    body = request.get_json() or {}
    name = (body.get("name") or "").strip()
    if not name:
        raise AppError("Collection name is required.", 400)
    db = SessionLocal()
    try:
        user = get_user_by_id(db, uuid.UUID(g.user["id"]))
        collection = collections_dao.create_collection(db, user.id, name[:120])
        return _collection_summary_dict(db, collection), 201
    finally:
        db.close()


def rename(collection_id: str):
    body = request.get_json() or {}
    name = (body.get("name") or "").strip()
    if not name:
        raise AppError("Collection name is required.", 400)
    db = SessionLocal()
    try:
        user_id = uuid.UUID(g.user["id"])
        collection = _require_owned_collection(db, uuid.UUID(collection_id), user_id)
        collections_dao.rename_collection(db, collection, name[:120])
        return _collection_summary_dict(db, collection), 200
    finally:
        db.close()


def delete(collection_id: str):
    db = SessionLocal()
    try:
        user_id = uuid.UUID(g.user["id"])
        collection = _require_owned_collection(db, uuid.UUID(collection_id), user_id)
        collections_dao.delete_collection(db, collection)
        return {"deleted": True}, 200
    finally:
        db.close()


def get_detail(collection_id: str):
    from src.modules.pieces.pieces_controller import enrich_piece_dict
    from src.modules.posts.posts_controller import enrich_post_dict

    db = SessionLocal()
    try:
        viewer_id = uuid.UUID(g.user["id"])
        collection = _require_owned_collection(db, uuid.UUID(collection_id), viewer_id)
        items = collections_dao.list_items(db, collection.id)
        enriched = []
        for item in items:
            target = _get_target(db, item.target_type, item.target_id)
            if not target:
                continue
            if item.target_type == "piece":
                target_dict = enrich_piece_dict(db, target, viewer_id)
            else:
                target_dict = enrich_post_dict(db, target, viewer_id)
            target_dict["targetType"] = item.target_type
            enriched.append(target_dict)
        return {
            "id": str(collection.id),
            "name": collection.name,
            "createdAt": collection.created_at.isoformat(),
            "itemCount": len(enriched),
            "items": enriched,
        }, 200
    finally:
        db.close()


def add_item(collection_id: str):
    body = request.get_json() or {}
    target_type = body.get("targetType")
    target_id = body.get("targetId")
    if target_type not in _VALID_TARGET_TYPES:
        raise AppError("targetType must be 'piece' or 'post'.", 400)
    if not target_id:
        raise AppError("targetId is required.", 400)
    db = SessionLocal()
    try:
        user_id = uuid.UUID(g.user["id"])
        collection = _require_owned_collection(db, uuid.UUID(collection_id), user_id)
        tid = uuid.UUID(target_id)
        if not _get_target(db, target_type, tid):
            raise AppError(f"{target_type.capitalize()} not found.", 404)
        collections_dao.add_item(db, collection.id, target_type, tid)
        return {"added": True, "itemCount": collections_dao.count_items(db, collection.id)}, 200
    finally:
        db.close()


def remove_item(collection_id: str, target_type: str, target_id: str):
    if target_type not in _VALID_TARGET_TYPES:
        raise AppError("targetType must be 'piece' or 'post'.", 400)
    db = SessionLocal()
    try:
        user_id = uuid.UUID(g.user["id"])
        collection = _require_owned_collection(db, uuid.UUID(collection_id), user_id)
        collections_dao.remove_item(db, collection.id, target_type, uuid.UUID(target_id))
        return {"removed": True, "itemCount": collections_dao.count_items(db, collection.id)}, 200
    finally:
        db.close()

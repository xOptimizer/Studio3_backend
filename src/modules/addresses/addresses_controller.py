"""Addresses controller."""
import uuid

from flask import request, g

from src.shared.config.database import SessionLocal
from src.shared.utils.app_error import AppError
from src.modules.addresses import addresses_dao

REQUIRED_FIELDS = ("firstName", "lastName", "phone", "line1", "city", "state", "zip")

_FIELD_MAP = {
    "label": "label",
    "firstName": "first_name",
    "lastName": "last_name",
    "phone": "phone",
    "line1": "line1",
    "line2": "line2",
    "city": "city",
    "state": "state",
    "zip": "zip",
    "country": "country",
    "latitude": "latitude",
    "longitude": "longitude",
    "isDefault": "is_default",
}


def _extract_fields(body: dict, require: bool) -> dict:
    if require:
        missing = [f for f in REQUIRED_FIELDS if not body.get(f)]
        if missing:
            raise AppError(f"Missing required fields: {', '.join(missing)}", 400)
    fields = {}
    for key, attr in _FIELD_MAP.items():
        if key in body:
            fields[attr] = body[key]
    return fields


def _require_owned(db, address_id: str, user_id: uuid.UUID):
    address = addresses_dao.get_address(db, uuid.UUID(address_id))
    if not address or address.user_id != user_id:
        raise AppError("Address not found.", 404)
    return address


def list_for_me():
    db = SessionLocal()
    try:
        user_id = uuid.UUID(g.user["id"])
        addresses = addresses_dao.list_addresses(db, user_id)
        return [addresses_dao.address_to_dict(a) for a in addresses], 200
    finally:
        db.close()


def create():
    body = request.get_json() or {}
    fields = _extract_fields(body, require=True)
    db = SessionLocal()
    try:
        user_id = uuid.UUID(g.user["id"])
        address = addresses_dao.create_address(db, user_id, **fields)
        return addresses_dao.address_to_dict(address), 201
    finally:
        db.close()


def patch(address_id: str):
    body = request.get_json() or {}
    fields = _extract_fields(body, require=False)
    db = SessionLocal()
    try:
        user_id = uuid.UUID(g.user["id"])
        address = _require_owned(db, address_id, user_id)
        address = addresses_dao.update_address(db, address, **fields)
        return addresses_dao.address_to_dict(address), 200
    finally:
        db.close()


def delete(address_id: str):
    db = SessionLocal()
    try:
        user_id = uuid.UUID(g.user["id"])
        address = _require_owned(db, address_id, user_id)
        addresses_dao.delete_address(db, address)
        return {"deleted": True}, 200
    finally:
        db.close()


def set_default(address_id: str):
    db = SessionLocal()
    try:
        user_id = uuid.UUID(g.user["id"])
        address = _require_owned(db, address_id, user_id)
        addresses_dao.set_default(db, address)
        return addresses_dao.address_to_dict(address), 200
    finally:
        db.close()

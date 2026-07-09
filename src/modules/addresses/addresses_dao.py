"""Addresses DAO."""
import uuid
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.shared.models.address import Address


def create_address(db: Session, user_id: uuid.UUID, **fields) -> Address:
    is_first = count_addresses(db, user_id) == 0
    if is_first:
        fields["is_default"] = True
    elif fields.get("is_default"):
        clear_default(db, user_id)
    address = Address(id=uuid.uuid4(), user_id=user_id, **fields)
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


def count_addresses(db: Session, user_id: uuid.UUID) -> int:
    return len(list(db.execute(select(Address.id).where(Address.user_id == user_id)).scalars().all()))


def list_addresses(db: Session, user_id: uuid.UUID) -> list[Address]:
    return list(
        db.execute(
            select(Address)
            .where(Address.user_id == user_id)
            .order_by(Address.is_default.desc(), Address.created_at.desc())
        ).scalars().all()
    )


def get_address(db: Session, address_id: uuid.UUID) -> Optional[Address]:
    return db.get(Address, address_id)


def clear_default(db: Session, user_id: uuid.UUID) -> None:
    db.execute(
        update(Address).where(Address.user_id == user_id, Address.is_default.is_(True)).values(is_default=False)
    )
    db.commit()


def set_default(db: Session, address: Address) -> None:
    clear_default(db, address.user_id)
    address.is_default = True
    db.commit()
    db.refresh(address)


def update_address(db: Session, address: Address, **fields) -> Address:
    if fields.get("is_default"):
        clear_default(db, address.user_id)
    for key, value in fields.items():
        setattr(address, key, value)
    db.commit()
    db.refresh(address)
    return address


def delete_address(db: Session, address: Address) -> None:
    db.delete(address)
    db.commit()


def address_to_dict(address: Address) -> dict:
    return {
        "id": str(address.id),
        "label": address.label,
        "firstName": address.first_name,
        "lastName": address.last_name,
        "phone": address.phone,
        "line1": address.line1,
        "line2": address.line2,
        "city": address.city,
        "state": address.state,
        "zip": address.zip,
        "country": address.country,
        "latitude": address.latitude,
        "longitude": address.longitude,
        "isDefault": address.is_default,
        "createdAt": address.created_at.isoformat(),
    }


def address_snapshot(address: Address) -> dict:
    """Denormalized copy for embedding in an Order — independent of later Address edits."""
    return address_to_dict(address)

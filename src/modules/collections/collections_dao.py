"""Collections DAO — Instagram-style saved folders (a named grouping of
saved pieces/posts, distinct from the flat quick-`Save` bookmark)."""
import uuid
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.shared.models.social import Collection, CollectionItem


def create_collection(db: Session, user_id: uuid.UUID, name: str) -> Collection:
    collection = Collection(id=uuid.uuid4(), user_id=user_id, name=name)
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return collection


def get_collection(db: Session, collection_id: uuid.UUID) -> Optional[Collection]:
    return db.get(Collection, collection_id)


def list_user_collections(db: Session, user_id: uuid.UUID) -> list[Collection]:
    return list(
        db.execute(
            select(Collection)
            .where(Collection.user_id == user_id)
            .order_by(Collection.created_at.desc())
        ).scalars().all()
    )


def count_items(db: Session, collection_id: uuid.UUID) -> int:
    return db.execute(
        select(func.count(CollectionItem.id)).where(CollectionItem.collection_id == collection_id)
    ).scalar_one()


def get_item(
    db: Session, collection_id: uuid.UUID, target_type: str, target_id: uuid.UUID
) -> Optional[CollectionItem]:
    return db.execute(
        select(CollectionItem).where(
            CollectionItem.collection_id == collection_id,
            CollectionItem.target_type == target_type,
            CollectionItem.target_id == target_id,
        )
    ).scalar_one_or_none()


def add_item(
    db: Session, collection_id: uuid.UUID, target_type: str, target_id: uuid.UUID
) -> CollectionItem:
    """Idempotent — re-adding an already-present item is a no-op."""
    existing = get_item(db, collection_id, target_type, target_id)
    if existing:
        return existing
    item = CollectionItem(
        id=uuid.uuid4(),
        collection_id=collection_id,
        target_type=target_type,
        target_id=target_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def remove_item(
    db: Session, collection_id: uuid.UUID, target_type: str, target_id: uuid.UUID
) -> None:
    db.query(CollectionItem).filter_by(
        collection_id=collection_id, target_type=target_type, target_id=target_id
    ).delete()
    db.commit()


def list_items(db: Session, collection_id: uuid.UUID) -> list[CollectionItem]:
    """Most-recently-added first, matching the client's folder ordering."""
    return list(
        db.execute(
            select(CollectionItem)
            .where(CollectionItem.collection_id == collection_id)
            .order_by(CollectionItem.created_at.desc())
        ).scalars().all()
    )


def most_recent_item(db: Session, collection_id: uuid.UUID) -> Optional[CollectionItem]:
    return db.execute(
        select(CollectionItem)
        .where(CollectionItem.collection_id == collection_id)
        .order_by(CollectionItem.created_at.desc())
        .limit(1)
    ).scalar_one_or_none()

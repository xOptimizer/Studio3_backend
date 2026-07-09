"""User API serializers."""
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from src.shared.models.user import User
from src.shared.username.constants import USERNAME_CHANGE_COOLDOWN_DAYS


def can_change_username(user: User) -> bool:
    if not user.last_username_change_at:
        return True
    next_allowed = user.last_username_change_at + timedelta(days=USERNAME_CHANGE_COOLDOWN_DAYS)
    return datetime.now(timezone.utc) >= next_allowed


def user_to_dict(
    db: Session, user: User, include_private: bool = True, viewer_id: Optional[uuid.UUID] = None
) -> dict:
    from src.modules.social import social_dao
    from src.modules.pieces.pieces_dao import list_user_pieces, list_saved_pieces, piece_to_dict
    from src.modules.orders import orders_dao

    data = {
        "username": user.username,
        "name": user.name,
        "profilePhotoUrl": user.image,
        "coverPhotoUrl": user.cover_photo_url,
        "bio": user.bio,
        "location": user.location,
        "role": user.role,
        "sellerEnabled": user.seller_enabled,
        "onboardingComplete": user.onboarding_complete,
    }

    data["followersCount"] = social_dao.count_followers(db, user.id)
    data["followingCount"] = social_dao.count_following(db, user.id)
    data["piecesCount"] = len(list_user_pieces(db, user.id))
    data["savesCount"] = social_dao.count_user_saves(db, user.id)
    data["collectedCount"] = orders_dao.count_buyer_collected(db, user.id)
    data["isFollowing"] = social_dao.user_follows(db, viewer_id, user.id) if viewer_id else False

    # Flutter client documented fallback aliases (see BACKEND_API_README.md)
    data["following"] = data["followingCount"]
    data["followers"] = data["followersCount"]
    data["pieces"] = data["piecesCount"]
    data["saves"] = data["savesCount"]
    data["collected"] = data["collectedCount"]
    data["isSeller"] = data["sellerEnabled"]

    if include_private:
        saved_pieces = [piece_to_dict(p) for p in list_saved_pieces(db, user.id)[:20]]
        data.update(
            {
                "email": user.email,
                "phone": user.phone,
                "emailVerified": user.email_verified,
                "lastUsernameChangeAt": user.last_username_change_at.isoformat() if user.last_username_change_at else None,
                "canChangeUsername": can_change_username(user),
                "tastePreferences": user.taste_preferences,
                "savedPieces": saved_pieces,
            }
        )
        data["saved"] = saved_pieces
    return data

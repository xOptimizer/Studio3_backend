"""User API serializers."""
from datetime import datetime, timezone, timedelta

from src.shared.models.user import User
from src.shared.username.constants import USERNAME_CHANGE_COOLDOWN_DAYS


def can_change_username(user: User) -> bool:
    if not user.last_username_change_at:
        return True
    next_allowed = user.last_username_change_at + timedelta(days=USERNAME_CHANGE_COOLDOWN_DAYS)
    return datetime.now(timezone.utc) >= next_allowed


def user_to_dict(user: User, include_private: bool = True) -> dict:
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
    if include_private:
        data.update(
            {
                "email": user.email,
                "emailVerified": user.email_verified,
                "lastUsernameChangeAt": user.last_username_change_at.isoformat() if user.last_username_change_at else None,
                "canChangeUsername": can_change_username(user),
                "tastePreferences": user.taste_preferences,
            }
        )
    return data

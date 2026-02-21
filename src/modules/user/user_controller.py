"""User controller: request/response; calls DAO; returns (data, status)."""
from src.shared.config.database import SessionLocal
from src.shared.utils.api_response import success_response
from src.shared.utils.messages import USERS_FETCHED
from src.modules.user.user_dao import get_all, count


def getall():
    """Protected: return { users, count }."""
    db = SessionLocal()
    try:
        users = get_all(db)
        total = count(db)
        user_list = [
            {
                "id": str(u.id),
                "email": u.email,
                "name": u.name,
                "image": u.image,
                "email_verified": u.email_verified,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ]
        data = {"users": user_list, "count": total}
        return data, 200
    finally:
        db.close()

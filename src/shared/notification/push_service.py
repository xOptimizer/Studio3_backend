"""Send push via Firebase Cloud Messaging (iOS/Android/Web). Mirrors email_service.py's fail-open pattern."""
import json
import os
import uuid
from typing import Optional

from src.shared.config.database import SessionLocal
from src.shared.models.device import Device
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "")
FIREBASE_SERVICE_ACCOUNT_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "")

_firebase_app = None  # lazy-initialized singleton
_init_attempted = False


def _get_app():
    global _firebase_app, _init_attempted
    if _firebase_app is not None:
        return _firebase_app
    if _init_attempted:
        return None
    _init_attempted = True
    if not FIREBASE_SERVICE_ACCOUNT_PATH and not FIREBASE_SERVICE_ACCOUNT_JSON:
        return None
    try:
        import firebase_admin
        from firebase_admin import credentials

        if FIREBASE_SERVICE_ACCOUNT_PATH:
            cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_PATH)
        else:
            cred = credentials.Certificate(json.loads(FIREBASE_SERVICE_ACCOUNT_JSON))
        _firebase_app = firebase_admin.initialize_app(cred)
        return _firebase_app
    except Exception as e:
        logger.exception("Failed to initialize Firebase app: %s", e)
        return None


def send_push(user_id: uuid.UUID, title: str, body: str, data: Optional[dict] = None) -> bool:
    """Send a push notification to all of a user's registered devices.

    Fails open like send_email: never raises, logs and returns False on any problem
    (unconfigured Firebase, no devices, or a send error for any individual token).
    """
    app = _get_app()
    if app is None:
        logger.warning("Firebase not configured; skipping push to user %s", user_id)
        return False
    db = SessionLocal()
    try:
        devices = db.query(Device).filter_by(user_id=user_id).all()
        if not devices:
            return False
        from firebase_admin import messaging

        ok_any = False
        for device in devices:
            try:
                msg = messaging.Message(
                    notification=messaging.Notification(title=title, body=body),
                    data={k: str(v) for k, v in (data or {}).items()},
                    token=device.push_token,
                )
                messaging.send(msg, app=app)
                ok_any = True
            except Exception as e:
                logger.warning("Push failed for device %s: %s", device.id, e)
        return ok_any
    except Exception as e:
        logger.exception("send_push failed for user %s: %s", user_id, e)
        return False
    finally:
        db.close()

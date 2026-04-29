import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

_initialized = False
_available = False


def _init() -> bool:
    global _initialized, _available
    if _initialized:
        return _available
    _initialized = True

    try:
        import firebase_admin
        from firebase_admin import credentials

        try:
            firebase_admin.get_app()
            _available = True
            return _available
        except ValueError:
            pass

        # Option 1: inline JSON in env var (preferred for hosted environments)
        json_str = os.getenv("FIREBASE_CREDENTIALS_JSON", "")
        if json_str:
            import json
            cred = credentials.Certificate(json.loads(json_str))
        else:
            # Option 2: path to a local file (local development only)
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
            if not os.path.exists(cred_path):
                logger.info("Firebase credentials not configured; push notifications disabled")
                return False
            cred = credentials.Certificate(cred_path)

        firebase_admin.initialize_app(cred)
        _available = True
        logger.info("Firebase push notifications enabled")
    except Exception as exc:
        logger.warning("Firebase init failed: %s", exc)

    return _available


def send_push(token: Optional[str], title: str, body: str) -> None:
    if not token or not _init():
        return
    try:
        from firebase_admin import messaging
        messaging.send(messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            android=messaging.AndroidConfig(priority="high"),
            token=token,
        ))
    except Exception as exc:
        logger.warning("Push notification failed: %s", exc)

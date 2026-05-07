from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from models import Notification


def save_notification(db: Session, user_id: int, title: str, body: str) -> None:
    """Persist a notification and purge that user's entries older than 7 days.

    Must be called before db.commit() so the insert and cleanup are atomic.
    """
    db.add(Notification(user_id=user_id, title=title, body=body))
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.created_at < cutoff,
    ).delete(synchronize_session=False)

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import get_current_user_id
from database import get_db
from models import Notification
from schemas import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])

_WINDOW = timedelta(days=7)


@router.get("/mine", response_model=list[NotificationResponse])
def get_my_notifications(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    cutoff = datetime.now(timezone.utc) - _WINDOW
    notifs = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.created_at >= cutoff)
        .order_by(Notification.created_at.desc())
        .all()
    )
    for n in notifs:
        if not n.is_read:
            n.is_read = True
    db.commit()
    return notifs


@router.get("/mine/unread-count")
def get_unread_count(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    cutoff = datetime.now(timezone.utc) - _WINDOW
    count = (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.created_at >= cutoff,
        )
        .count()
    )
    return {"count": count}

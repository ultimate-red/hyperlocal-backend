from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from auth import get_current_user_id
from database import get_db
from models import AppLog

router = APIRouter(prefix="/app-logs", tags=["app-logs"])


class AppLogCreate(BaseModel):
    level:   str
    message: str
    screen:  Optional[str] = None


@router.post("/", status_code=204)
def create_log(
    body: AppLogCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    db.add(AppLog(
        user_id=user_id,
        level=body.level,
        message=body.message,
        screen=body.screen,
    ))
    db.commit()

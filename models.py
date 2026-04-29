from datetime import datetime, timezone
import enum

def _now():
    return datetime.now(timezone.utc)

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    google_id       = Column(String, unique=True, index=True, nullable=True)
    email           = Column(String, unique=True, index=True, nullable=True)
    name            = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    bio             = Column(String, nullable=True)
    location        = Column(String, nullable=True)
    phone           = Column(String, unique=True, index=True, nullable=True)
    fcm_token       = Column(String, nullable=True)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=_now)
    updated_at      = Column(DateTime, default=_now, onupdate=_now)

    created_tasks  = relationship("Task", foreign_keys="Task.created_by",  back_populates="creator")
    accepted_tasks = relationship("Task", foreign_keys="Task.accepted_by", back_populates="acceptor")


class TaskStatus(str, enum.Enum):
    OPEN      = "open"
    ACCEPTED  = "accepted"
    COMPLETED = "completed"
    ABORTED   = "aborted"


class Task(Base):
    __tablename__ = "tasks"

    id                   = Column(Integer, primary_key=True, index=True)
    title                = Column(String, nullable=False)
    description          = Column(String, nullable=True)
    reward               = Column(Float, nullable=True)
    status               = Column(String, default=TaskStatus.OPEN.value)
    created_by           = Column(Integer, ForeignKey("users.id"), nullable=False)
    accepted_by          = Column(Integer, ForeignKey("users.id"), nullable=True)
    abort_reason         = Column(String, nullable=True)
    hidden_from_creator  = Column(Boolean, default=False, nullable=False)
    hidden_from_acceptor = Column(Boolean, default=False, nullable=False)
    created_at           = Column(DateTime, default=_now)
    updated_at           = Column(DateTime, default=_now, onupdate=_now)

    creator  = relationship("User", foreign_keys=[created_by],  back_populates="created_tasks")
    acceptor = relationship("User", foreign_keys=[accepted_by], back_populates="accepted_tasks")

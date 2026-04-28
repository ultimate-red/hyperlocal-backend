from datetime import datetime
import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    google_id       = Column(String, unique=True, index=True, nullable=True)
    email           = Column(String, unique=True, index=True, nullable=True)
    name            = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)   # URL from Google
    bio             = Column(String, nullable=True)
    location        = Column(String, nullable=True)   # free text; lat/lng in Phase 1
    phone           = Column(String, unique=True, index=True, nullable=True)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_tasks  = relationship("Task", foreign_keys="Task.created_by", back_populates="creator")
    accepted_tasks = relationship("Task", foreign_keys="Task.accepted_by", back_populates="acceptor")


class TaskStatus(str, enum.Enum):
    OPEN      = "open"
    ACCEPTED  = "accepted"
    COMPLETED = "completed"


class Task(Base):
    __tablename__ = "tasks"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String, nullable=False)
    description = Column(String, nullable=False)
    reward      = Column(Float, nullable=True)
    status      = Column(Enum(TaskStatus), default=TaskStatus.OPEN)
    created_by  = Column(Integer, ForeignKey("users.id"), nullable=False)
    accepted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator  = relationship("User", foreign_keys=[created_by],  back_populates="created_tasks")
    acceptor = relationship("User", foreign_keys=[accepted_by], back_populates="accepted_tasks")

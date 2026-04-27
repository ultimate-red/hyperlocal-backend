from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    otp = Column(String, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    is_verified = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    created_tasks = relationship("Task", foreign_keys="Task.created_by", back_populates="creator")
    accepted_tasks = relationship("Task", foreign_keys="Task.accepted_by", back_populates="acceptor")

class TaskStatus(str, enum.Enum):
    OPEN = "open"
    ACCEPTED = "accepted"
    COMPLETED = "completed"

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    reward = Column(Float, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.OPEN)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    accepted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_tasks")
    acceptor = relationship("User", foreign_keys=[accepted_by], back_populates="accepted_tasks")

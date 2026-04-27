from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ── User ──────────────────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    id:              int
    email:           Optional[str] = None
    name:            Optional[str] = None
    profile_picture: Optional[str] = None
    bio:             Optional[str] = None
    location:        Optional[str] = None
    phone:           Optional[str] = None
    is_active:       bool
    created_at:      datetime

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    name:     Optional[str] = None
    bio:      Optional[str] = None
    location: Optional[str] = None
    phone:    Optional[str] = None


# ── Auth ──────────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type:   str
    user:         UserResponse


class GoogleAuthURL(BaseModel):
    url: str


# ── Tasks ─────────────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title:       str
    description: Optional[str]   = None
    reward:      Optional[float] = None


class TaskUpdate(BaseModel):
    title:       Optional[str]   = None
    description: Optional[str]   = None
    reward:      Optional[float] = None


class TaskResponse(BaseModel):
    id:            int
    title:         str
    description:   Optional[str]   = None
    reward:        Optional[float] = None
    status:        str
    created_by:    int
    accepted_by:   Optional[int]   = None
    created_at:    datetime
    updated_at:    datetime
    creator_name:  Optional[str]   = None
    acceptor_name: Optional[str]   = None

    class Config:
        from_attributes = True

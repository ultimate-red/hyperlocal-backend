from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ── User ──────────────────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    id:              int
    email:           Optional[str]   = None
    name:            Optional[str]   = None
    profile_picture: Optional[str]   = None
    bio:             Optional[str]   = None
    location:        Optional[str]   = None
    phone:           Optional[str]   = None
    is_active:       bool
    created_at:      datetime
    average_rating:  Optional[float] = None
    review_count:    int             = 0

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
    task_type:   str             = "request"


class TaskUpdate(BaseModel):
    title:       Optional[str]   = None
    description: Optional[str]   = None
    reward:      Optional[float] = None


class TaskResponse(BaseModel):
    id:                   int
    title:                str
    description:          Optional[str]   = None
    reward:               Optional[float] = None
    status:               str
    created_by:           int
    accepted_by:          Optional[int]   = None
    abort_reason:         Optional[str]   = None
    hidden_from_creator:  bool            = False
    hidden_from_acceptor: bool            = False
    task_type:            str             = "request"
    created_at:           datetime
    updated_at:           datetime
    creator_name:         Optional[str]   = None
    acceptor_name:        Optional[str]   = None
    creator_rating:       Optional[float] = None
    acceptor_rating:      Optional[float] = None

    class Config:
        from_attributes = True


class TaskAbort(BaseModel):
    reason: str


class FCMTokenUpdate(BaseModel):
    token: str


# ── Feedback ──────────────────────────────────────────────────────────────────

class FeedbackCreate(BaseModel):
    category: str
    message:  str


class FeedbackResponse(BaseModel):
    id:         int
    user_id:    int
    category:   str
    message:    str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Reviews ───────────────────────────────────────────────────────────────────

class ReviewCreate(BaseModel):
    rating:  int
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    id:            int
    task_id:       int
    reviewer_id:   int
    reviewee_id:   int
    rating:        int
    comment:       Optional[str] = None
    reviewer_name: Optional[str] = None
    created_at:    datetime

    class Config:
        from_attributes = True

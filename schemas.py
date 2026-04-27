from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# User Schemas
class UserCreate(BaseModel):
    phone: str

class OTPVerify(BaseModel):
    phone: str
    otp: str

class UserResponse(BaseModel):
    id: int
    phone: str
    name: Optional[str] = None
    is_verified: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Task Schemas
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    reward: Optional[float] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    reward: Optional[float] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    reward: Optional[float] = None
    status: str
    created_by: int
    accepted_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    creator_name: Optional[str] = None
    acceptor_name: Optional[str] = None
    
    class Config:
        from_attributes = True

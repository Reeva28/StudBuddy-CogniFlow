"""
User-related schemas for API validation
"""
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, EmailStr, Field

from app.schemas.study_session import StudySession

class UserBase(BaseModel):
    """Base user model"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    """User creation model"""
    email: EmailStr
    username: str
    password: str

class UserUpdate(UserBase):
    """User update model"""
    password: Optional[str] = None

class UserInDBBase(UserBase):
    """User in DB base model"""
    id: Optional[int] = None

    class Config:
        from_attributes = True

class User(UserInDBBase):
    """User response model"""
    pass

class UserInDB(UserInDBBase):
    """User in DB model"""
    hashed_password: str

class Token(BaseModel):
    """OAuth token model"""
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    """Token payload model"""
    sub: Optional[int] = None
    
class UserStats(BaseModel):
    """User statistics model"""
    total_study_time: int
    session_count: int
    subject_distribution: Dict[str, int]
    recent_sessions: List[StudySession]
    
    class Config:
        from_attributes = True
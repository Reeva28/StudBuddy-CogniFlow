"""
Note schemas for API validation
"""
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field

class NoteBase(BaseModel):
    """Base note model"""
    content: str
    type: Optional[str] = "general"

class NoteCreate(NoteBase):
    """Note creation model"""
    session_id: Optional[int] = None

class NoteUpdate(NoteBase):
    """Note update model"""
    content: Optional[str] = None
    type: Optional[str] = None

class NoteInDBBase(NoteBase):
    """Note in DB base model"""
    id: int
    user_id: int
    session_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Note(NoteInDBBase):
    """Note response model"""
    pass
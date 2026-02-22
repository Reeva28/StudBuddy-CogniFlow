"""
Study plan schemas for API validation
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field

class StudyPlanBase(BaseModel):
    """Base study plan model"""
    goal: Optional[str] = None
    subject: Optional[str] = None
    duration_minutes: Optional[int] = 0
    difficulty_level: Optional[int] = 3
    content: Optional[str] = None

class StudyPlanCreate(StudyPlanBase):
    """Study plan creation model"""
    goal: str = Field(..., min_length=1, max_length=255)
    subject: str = Field(..., min_length=1, max_length=100)
    duration_minutes: int = Field(..., gt=0)
    difficulty_level: int = Field(3, ge=1, le=5)

class StudyPlanUpdate(StudyPlanBase):
    """Study plan update model"""
    plan_data: Optional[Dict[str, Any]] = None

class StudyPlanInDBBase(StudyPlanBase):
    """Study plan in DB base model"""
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class StudyPlan(StudyPlanInDBBase):
    """Study plan response model"""
    pass

class StudyPlanGenerateRequest(BaseModel):
    """Request model for generating a study plan"""
    goal: str = Field(..., min_length=1, max_length=255)
    subject: str = Field(..., min_length=1, max_length=100)
    duration_minutes: int = Field(..., gt=0)
    difficulty: int = Field(3, ge=1, le=5)
    document_ids: Optional[List[int]] = None
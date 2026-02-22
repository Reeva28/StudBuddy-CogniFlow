"""
Study session schemas for API validation
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field

class StudySessionBase(BaseModel):
    """Base study session model"""
    title: Optional[str] = None
    goal: Optional[str] = None
    subject: Optional[str] = None
    total_duration_minutes: Optional[int] = 0
    status: Optional[str] = "planned"

class StudySessionCreate(StudySessionBase):
    """Study session creation model"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    goal: Optional[str] = Field(None, min_length=1, max_length=255)
    subject: Optional[str] = Field(None, min_length=1, max_length=100)
    total_duration_minutes: Optional[int] = Field(None, gt=0)
    duration_minutes: Optional[int] = Field(None, gt=0)
    study_plan_id: Optional[int] = None

class StudySessionUpdate(StudySessionBase):
    """Study session update model"""
    actual_duration_minutes: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    focus_rating: Optional[int] = Field(None, ge=1, le=5)
    productivity_rating: Optional[int] = Field(None, ge=1, le=5)
    mood_before: Optional[str] = None
    mood_after: Optional[str] = None
    reflection: Optional[str] = None
    status: Optional[str] = None

class StudySessionInDBBase(StudySessionBase):
    """Study session in DB base model"""
    id: int
    user_id: int
    study_plan_id: Optional[int] = None
    actual_duration_minutes: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    focus_rating: Optional[int] = None
    productivity_rating: Optional[int] = None
    mood_before: Optional[str] = None
    mood_after: Optional[str] = None
    reflection: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class StudySession(StudySessionInDBBase):
    """Study session response model"""
    pass

class PomodoroBase(BaseModel):
    """Base pomodoro model"""
    duration_minutes: int = 25
    break_duration_minutes: int = 5

class PomodoroCreate(PomodoroBase):
    """Pomodoro creation model"""
    session_id: int

class PomodoroUpdate(PomodoroBase):
    """Pomodoro update model"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    completed: Optional[bool] = None

class PomodoroInDBBase(PomodoroBase):
    """Pomodoro in DB base model"""
    id: int
    session_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    completed: bool = False

    class Config:
        from_attributes = True

class Pomodoro(PomodoroInDBBase):
    """Pomodoro response model"""
    pass
"""
Mood schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MoodBase(BaseModel):
    mood_type: str = Field(..., description="Type of mood: happy, focused, stressed, tired, energized, frustrated, motivated")
    intensity: int = Field(..., ge=1, le=5, description="Mood intensity from 1-5")
    is_before_session: bool = Field(..., description="True if recorded before session, False if after")
    notes: Optional[str] = Field(None, description="Optional notes about the mood")


class MoodCreate(MoodBase):
    study_session_id: Optional[int] = Field(None, description="Optional study session ID")


class MoodUpdate(BaseModel):
    mood_type: Optional[str] = None
    intensity: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class Mood(MoodBase):
    id: int
    user_id: int
    study_session_id: Optional[int]
    recorded_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class MoodTrend(BaseModel):
    """Mood trend data for analytics"""
    date: str
    avg_before_intensity: Optional[float]
    avg_after_intensity: Optional[float]
    most_common_mood: Optional[str]
    session_count: int


class MoodStats(BaseModel):
    """Overall mood statistics"""
    total_moods: int
    avg_intensity: float
    most_common_mood: str
    mood_improvement_rate: float  # Percentage of sessions where mood improved
    recent_trend: str  # "improving", "declining", "stable"

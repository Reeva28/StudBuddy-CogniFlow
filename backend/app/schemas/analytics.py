"""
Analytics schemas
"""
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel


class SessionStats(BaseModel):
    """Statistics about study sessions"""
    total_sessions: int
    completed_sessions: int
    total_study_minutes: int
    average_session_minutes: float
    completion_rate: float
    current_streak_days: int
    longest_streak_days: int


class NoteStats(BaseModel):
    """Statistics about notes"""
    total_notes: int
    notes_by_type: Dict[str, int]
    average_notes_per_session: float


class ProductivityStats(BaseModel):
    """Productivity related statistics"""
    average_focus_rating: Optional[float]
    average_productivity_rating: Optional[float]
    most_productive_hour: Optional[int]
    total_break_minutes: int


class RecentSession(BaseModel):
    """Recent session summary"""
    id: int
    title: str
    subject: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    actual_duration_minutes: Optional[int]
    status: str
    focus_rating: Optional[int]
    notes_count: int
    
    class Config:
        from_attributes = True


class TimeDistribution(BaseModel):
    """Study time distribution by hour"""
    hour: int
    minutes: int
    session_count: int


class DailyActivity(BaseModel):
    """Daily activity summary"""
    date: str
    total_minutes: int
    session_count: int
    notes_count: int
    average_focus: Optional[float]


class AnalyticsDashboard(BaseModel):
    """Complete analytics dashboard data"""
    session_stats: SessionStats
    note_stats: NoteStats
    productivity_stats: ProductivityStats
    recent_sessions: List[RecentSession]
    time_distribution: List[TimeDistribution]
    daily_activity: List[DailyActivity]
    weekly_summary: Dict[str, int]
    monthly_summary: Dict[str, int]

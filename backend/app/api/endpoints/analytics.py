"""
Analytics endpoints
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.db import models
from app.schemas import analytics
from app.services import analytics as analytics_service

router = APIRouter()


@router.get("/dashboard", response_model=analytics.AnalyticsDashboard)
def get_analytics_dashboard(
    days: int = 30,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Get complete analytics dashboard for the current user
    """
    return analytics_service.get_analytics_dashboard(db, current_user.id, days)


@router.get("/sessions", response_model=analytics.SessionStats)
def get_session_statistics(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Get session statistics
    """
    return analytics_service.get_session_stats(db, current_user.id)


@router.get("/notes", response_model=analytics.NoteStats)
def get_note_statistics(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Get note statistics
    """
    return analytics_service.get_note_stats(db, current_user.id)


@router.get("/productivity", response_model=analytics.ProductivityStats)
def get_productivity_statistics(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Get productivity statistics
    """
    return analytics_service.get_productivity_stats(db, current_user.id)


@router.get("/recent-sessions", response_model=List[analytics.RecentSession])
def get_recent_study_sessions(
    limit: int = 10,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Get recent study sessions
    """
    return analytics_service.get_recent_sessions(db, current_user.id, limit)


@router.get("/time-distribution", response_model=List[analytics.TimeDistribution])
def get_time_distribution_data(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Get study time distribution by hour of day
    """
    return analytics_service.get_time_distribution(db, current_user.id)


@router.get("/daily-activity", response_model=List[analytics.DailyActivity])
def get_daily_activity_data(
    days: int = 30,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Get daily activity for the last N days
    """
    return analytics_service.get_daily_activity(db, current_user.id, days)

"""
Analytics service for generating user insights
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.db import models
from app.schemas import analytics


def get_session_stats(db: Session, user_id: int) -> analytics.SessionStats:
    """Calculate session statistics"""
    sessions = db.query(models.StudySession).filter(
        models.StudySession.user_id == user_id
    ).all()
    
    total_sessions = len(sessions)
    completed_sessions = sum(1 for s in sessions if s.status == "completed")
    total_study_minutes = sum(s.actual_duration_minutes or 0 for s in sessions)
    
    completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    average_minutes = total_study_minutes / total_sessions if total_sessions > 0 else 0
    
    # Calculate streak
    current_streak, longest_streak = calculate_study_streaks(sessions)
    
    return analytics.SessionStats(
        total_sessions=total_sessions,
        completed_sessions=completed_sessions,
        total_study_minutes=total_study_minutes,
        average_session_minutes=round(average_minutes, 1),
        completion_rate=round(completion_rate, 1),
        current_streak_days=current_streak,
        longest_streak_days=longest_streak
    )


def get_note_stats(db: Session, user_id: int) -> analytics.NoteStats:
    """Calculate note statistics"""
    notes = db.query(models.Note).filter(
        models.Note.user_id == user_id
    ).all()
    
    total_notes = len(notes)
    
    # Count by type
    notes_by_type = defaultdict(int)
    for note in notes:
        notes_by_type[note.type] += 1
    
    # Calculate average notes per session
    session_count = db.query(models.StudySession).filter(
        models.StudySession.user_id == user_id
    ).count()
    
    avg_per_session = total_notes / session_count if session_count > 0 else 0
    
    return analytics.NoteStats(
        total_notes=total_notes,
        notes_by_type=dict(notes_by_type),
        average_notes_per_session=round(avg_per_session, 1)
    )


def get_productivity_stats(db: Session, user_id: int) -> analytics.ProductivityStats:
    """Calculate productivity statistics"""
    sessions = db.query(models.StudySession).filter(
        models.StudySession.user_id == user_id,
        models.StudySession.status == "completed"
    ).all()
    
    # Average ratings
    focus_ratings = [s.focus_rating for s in sessions if s.focus_rating is not None]
    productivity_ratings = [s.productivity_rating for s in sessions if s.productivity_rating is not None]
    
    avg_focus = sum(focus_ratings) / len(focus_ratings) if focus_ratings else None
    avg_productivity = sum(productivity_ratings) / len(productivity_ratings) if productivity_ratings else None
    
    # Most productive hour
    productive_hour = find_most_productive_hour(sessions)
    
    # Total break time
    pomodoros = db.query(models.Pomodoro).join(
        models.StudySession
    ).filter(
        models.StudySession.user_id == user_id
    ).all()
    
    total_break_minutes = sum(p.break_duration_minutes or 5 for p in pomodoros)
    
    return analytics.ProductivityStats(
        average_focus_rating=round(avg_focus, 1) if avg_focus else None,
        average_productivity_rating=round(avg_productivity, 1) if avg_productivity else None,
        most_productive_hour=productive_hour,
        total_break_minutes=total_break_minutes
    )


def get_recent_sessions(
    db: Session, user_id: int, limit: int = 10
) -> List[analytics.RecentSession]:
    """Get recent sessions with note counts"""
    sessions = db.query(models.StudySession).filter(
        models.StudySession.user_id == user_id
    ).order_by(
        models.StudySession.created_at.desc()
    ).limit(limit).all()
    
    result = []
    for session in sessions:
        notes_count = db.query(models.Note).filter(
            models.Note.session_id == session.id
        ).count()
        
        result.append(analytics.RecentSession(
            id=session.id,
            title=session.title,
            subject=session.subject or "General",
            start_time=session.start_time,
            end_time=session.end_time,
            actual_duration_minutes=session.actual_duration_minutes,
            status=session.status,
            focus_rating=session.focus_rating,
            notes_count=notes_count
        ))
    
    return result


def get_time_distribution(db: Session, user_id: int) -> List[analytics.TimeDistribution]:
    """Get study time distribution by hour of day"""
    sessions = db.query(models.StudySession).filter(
        models.StudySession.user_id == user_id,
        models.StudySession.start_time.isnot(None)
    ).all()
    
    # Group by hour
    hour_data = defaultdict(lambda: {"minutes": 0, "count": 0})
    
    for session in sessions:
        if session.start_time and session.actual_duration_minutes:
            hour = session.start_time.hour
            hour_data[hour]["minutes"] += session.actual_duration_minutes
            hour_data[hour]["count"] += 1
    
    result = []
    for hour in range(24):
        data = hour_data.get(hour, {"minutes": 0, "count": 0})
        result.append(analytics.TimeDistribution(
            hour=hour,
            minutes=data["minutes"],
            session_count=data["count"]
        ))
    
    return result


def get_daily_activity(
    db: Session, user_id: int, days: int = 30
) -> List[analytics.DailyActivity]:
    """Get daily activity for the last N days"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    sessions = db.query(models.StudySession).filter(
        models.StudySession.user_id == user_id,
        models.StudySession.created_at >= start_date
    ).all()
    
    # Group by date
    daily_data = defaultdict(lambda: {
        "minutes": 0,
        "sessions": 0,
        "notes": 0,
        "focus_ratings": []
    })
    
    for session in sessions:
        date_key = session.created_at.strftime("%Y-%m-%d")
        daily_data[date_key]["minutes"] += session.actual_duration_minutes or 0
        daily_data[date_key]["sessions"] += 1
        
        if session.focus_rating:
            daily_data[date_key]["focus_ratings"].append(session.focus_rating)
        
        # Count notes for this session
        notes_count = db.query(models.Note).filter(
            models.Note.session_id == session.id
        ).count()
        daily_data[date_key]["notes"] += notes_count
    
    # Create result for all days in range
    result = []
    current_date = start_date
    while current_date <= end_date:
        date_key = current_date.strftime("%Y-%m-%d")
        data = daily_data.get(date_key, {
            "minutes": 0,
            "sessions": 0,
            "notes": 0,
            "focus_ratings": []
        })
        
        avg_focus = None
        if data["focus_ratings"]:
            avg_focus = sum(data["focus_ratings"]) / len(data["focus_ratings"])
        
        result.append(analytics.DailyActivity(
            date=date_key,
            total_minutes=data["minutes"],
            session_count=data["sessions"],
            notes_count=data["notes"],
            average_focus=round(avg_focus, 1) if avg_focus else None
        ))
        
        current_date += timedelta(days=1)
    
    return result


def get_weekly_summary(db: Session, user_id: int) -> Dict[str, int]:
    """Get summary for the current week"""
    now = datetime.utcnow()
    week_start = now - timedelta(days=now.weekday())
    
    sessions = db.query(models.StudySession).filter(
        models.StudySession.user_id == user_id,
        models.StudySession.created_at >= week_start
    ).all()
    
    total_minutes = sum(s.actual_duration_minutes or 0 for s in sessions)
    completed = sum(1 for s in sessions if s.status == "completed")
    
    return {
        "total_sessions": len(sessions),
        "completed_sessions": completed,
        "total_minutes": total_minutes,
        "average_minutes": total_minutes // len(sessions) if sessions else 0
    }


def get_monthly_summary(db: Session, user_id: int) -> Dict[str, int]:
    """Get summary for the current month"""
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    sessions = db.query(models.StudySession).filter(
        models.StudySession.user_id == user_id,
        models.StudySession.created_at >= month_start
    ).all()
    
    total_minutes = sum(s.actual_duration_minutes or 0 for s in sessions)
    completed = sum(1 for s in sessions if s.status == "completed")
    
    return {
        "total_sessions": len(sessions),
        "completed_sessions": completed,
        "total_minutes": total_minutes,
        "average_minutes": total_minutes // len(sessions) if sessions else 0
    }


def get_analytics_dashboard(db: Session, user_id: int, days: int = 30) -> analytics.AnalyticsDashboard:
    """Get complete analytics dashboard"""
    return analytics.AnalyticsDashboard(
        session_stats=get_session_stats(db, user_id),
        note_stats=get_note_stats(db, user_id),
        productivity_stats=get_productivity_stats(db, user_id),
        recent_sessions=get_recent_sessions(db, user_id),
        time_distribution=get_time_distribution(db, user_id),
        daily_activity=get_daily_activity(db, user_id, days=days),
        weekly_summary=get_weekly_summary(db, user_id),
        monthly_summary=get_monthly_summary(db, user_id)
    )


# Helper functions

def calculate_study_streaks(sessions: List[models.StudySession]) -> tuple[int, int]:
    """Calculate current and longest study streaks"""
    if not sessions:
        return 0, 0
    
    # Get unique dates with completed sessions
    dates = set()
    for session in sessions:
        if session.status == "completed" and session.created_at:
            dates.add(session.created_at.date())
    
    if not dates:
        return 0, 0
    
    sorted_dates = sorted(dates, reverse=True)
    
    # Calculate current streak
    current_streak = 0
    today = datetime.utcnow().date()
    check_date = today
    
    for date in sorted_dates:
        if date == check_date or date == check_date - timedelta(days=1):
            current_streak += 1
            check_date = date - timedelta(days=1)
        else:
            break
    
    # Calculate longest streak
    longest_streak = 1
    temp_streak = 1
    sorted_dates_asc = sorted(dates)
    
    for i in range(1, len(sorted_dates_asc)):
        if (sorted_dates_asc[i] - sorted_dates_asc[i-1]).days == 1:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 1
    
    return current_streak, longest_streak


def find_most_productive_hour(sessions: List[models.StudySession]) -> Optional[int]:
    """Find the hour with highest productivity rating"""
    if not sessions:
        return None
    
    hour_productivity = defaultdict(list)
    
    for session in sessions:
        if session.start_time and session.productivity_rating:
            hour = session.start_time.hour
            hour_productivity[hour].append(session.productivity_rating)
    
    if not hour_productivity:
        return None
    
    # Find hour with highest average productivity
    best_hour = None
    best_avg = 0
    
    for hour, ratings in hour_productivity.items():
        avg = sum(ratings) / len(ratings)
        if avg > best_avg:
            best_avg = avg
            best_hour = hour
    
    return best_hour

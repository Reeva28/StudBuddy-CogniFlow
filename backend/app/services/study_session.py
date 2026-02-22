"""
Study session service
"""
from typing import Optional, List
from datetime import datetime

from sqlalchemy.orm import Session

from app import schemas
from app.db import models

def get_study_session_by_id(db: Session, session_id: int) -> Optional[models.StudySession]:
    """
    Get a study session by ID
    """
    return db.query(models.StudySession).filter(models.StudySession.id == session_id).first()

def get_study_sessions_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[models.StudySession]:
    """
    Get study sessions for a user
    """
    return db.query(models.StudySession)\
        .filter(models.StudySession.user_id == user_id)\
        .order_by(models.StudySession.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def create_study_session(
    db: Session, user_id: int, session_in: schemas.StudySessionCreate
) -> models.StudySession:
    """
    Create a new study session
    """
    db_session = models.StudySession(
        user_id=user_id,
        title=session_in.title,
        goal=session_in.goal,
        subject=session_in.subject,
        total_duration_minutes=session_in.total_duration_minutes,
        study_plan_id=session_in.study_plan_id,
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def update_study_session(
    db: Session, session: models.StudySession, session_in: schemas.StudySessionUpdate
) -> models.StudySession:
    """
    Update a study session
    """
    update_data = session_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(session, field, value)
    
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def delete_study_session(db: Session, session_id: int) -> None:
    """
    Delete a study session
    """
    session = get_study_session_by_id(db, session_id=session_id)
    if session:
        # Delete related pomodoros
        db.query(models.Pomodoro).filter(models.Pomodoro.session_id == session_id).delete()
        
        # Delete related notes
        db.query(models.Note).filter(models.Note.session_id == session_id).delete()
        
        # Delete the session
        db.delete(session)
        db.commit()

def create_pomodoro(
    db: Session, session_id: int, pomodoro_in: schemas.PomodoroCreate
) -> models.Pomodoro:
    """
    Create a new pomodoro
    """
    db_pomodoro = models.Pomodoro(
        session_id=session_id,
        duration_minutes=pomodoro_in.duration_minutes,
        break_duration_minutes=pomodoro_in.break_duration_minutes,
        start_time=datetime.utcnow(),
    )
    db.add(db_pomodoro)
    db.commit()
    db.refresh(db_pomodoro)
    return db_pomodoro

def update_pomodoro(
    db: Session, pomodoro_id: int, pomodoro_in: schemas.PomodoroUpdate
) -> Optional[models.Pomodoro]:
    """
    Update a pomodoro
    """
    pomodoro = db.query(models.Pomodoro).filter(models.Pomodoro.id == pomodoro_id).first()
    if not pomodoro:
        return None
    
    update_data = pomodoro_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(pomodoro, field, value)
    
    db.add(pomodoro)
    db.commit()
    db.refresh(pomodoro)
    return pomodoro
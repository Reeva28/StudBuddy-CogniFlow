"""
Study session endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.db import models
from app import schemas
from app.services.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.StudySession)
async def create_study_session(
    session: schemas.StudySessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new study session
    """
    # Use duration_minutes if provided, otherwise use total_duration_minutes
    duration = session.duration_minutes or session.total_duration_minutes or 25
    
    # Provide defaults for quick pomodoro sessions
    title = session.title or f"{duration}-minute study session"
    goal = session.goal or "Quick study session"
    
    # Create study session in database
    db_session = models.StudySession(
        title=title,
        goal=goal,
        subject=session.subject,
        total_duration_minutes=duration,
        user_id=current_user.id,
        study_plan_id=session.study_plan_id
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/", response_model=List[schemas.StudySession])
async def get_user_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get all user's study sessions
    """
    sessions = db.query(models.StudySession).filter(
        models.StudySession.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return sessions

@router.get("/{session_id}", response_model=schemas.StudySession)
async def get_study_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get a specific study session by ID
    """
    session = db.query(models.StudySession).filter(
        models.StudySession.id == session_id,
        models.StudySession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study session with ID {session_id} not found"
        )
    
    return session

@router.put("/{session_id}", response_model=schemas.StudySession)
async def update_study_session(
    session_id: int,
    session_update: schemas.StudySessionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update a study session
    """
    # Find the session
    db_session = db.query(models.StudySession).filter(
        models.StudySession.id == session_id,
        models.StudySession.user_id == current_user.id
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study session with ID {session_id} not found"
        )
    
    # Update fields
    for field, value in session_update.dict(exclude_unset=True).items():
        setattr(db_session, field, value)
    
    db.commit()
    db.refresh(db_session)
    return db_session

@router.put("/{session_id}/complete", response_model=schemas.StudySession)
async def complete_study_session(
    session_id: int,
    completion_data: schemas.StudySessionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Complete a study session with notes and rating
    """
    # Find the session
    db_session = db.query(models.StudySession).filter(
        models.StudySession.id == session_id,
        models.StudySession.user_id == current_user.id
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study session with ID {session_id} not found"
        )
    
    # Mark as completed and update fields
    db_session.status = "completed"
    for field, value in completion_data.dict(exclude_unset=True).items():
        setattr(db_session, field, value)
    
    db.commit()
    db.refresh(db_session)
    return db_session
"""
User endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.db.session import get_db
from app.db import models
from app import schemas
from app.services.auth import get_current_user, get_password_hash

router = APIRouter()

@router.post("/", response_model=schemas.User)
async def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user
    """
    # Check if user with this email already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username is already taken
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/me", response_model=schemas.User)
async def get_current_user_info(
    current_user: models.User = Depends(get_current_user)
):
    """
    Get information about the currently authenticated user
    """
    return current_user

@router.get("/me/stats", response_model=schemas.UserStats)
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get user's study statistics
    """
    # Calculate total study time
    total_study_time_query = db.query(
        models.StudySession.actual_duration_minutes
    ).filter(
        models.StudySession.user_id == current_user.id,
        models.StudySession.status == "completed"
    )
    
    total_study_time = sum([session[0] for session in total_study_time_query]) if total_study_time_query.count() > 0 else 0
    
    # Get subject distribution
    subject_distribution = {}
    subject_query = db.query(
        models.StudySession.subject, 
        models.StudySession.actual_duration_minutes
    ).filter(
        models.StudySession.user_id == current_user.id,
        models.StudySession.status == "completed"
    ).all()
    
    for subject, duration in subject_query:
        if subject not in subject_distribution:
            subject_distribution[subject] = 0
        subject_distribution[subject] += duration
    
    # Get recent sessions
    recent_sessions = db.query(models.StudySession).filter(
        models.StudySession.user_id == current_user.id
    ).order_by(models.StudySession.created_at.desc()).limit(5).all()
    
    return {
        "total_study_time": total_study_time,
        "session_count": total_study_time_query.count(),
        "subject_distribution": subject_distribution,
        "recent_sessions": recent_sessions
    }

@router.put("/me", response_model=schemas.User)
async def update_user_profile(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update the current user's profile
    """
    # Check email uniqueness if being updated
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(models.User).filter(
            models.User.email == user_update.email
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        current_user.email = user_update.email
    
    # Check username uniqueness if being updated
    if user_update.username and user_update.username != current_user.username:
        existing_user = db.query(models.User).filter(
            models.User.username == user_update.username
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        current_user.username = user_update.username
    
    # Update other fields
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.password:
        current_user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    return current_user
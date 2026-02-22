"""
Mood tracking endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.services.auth import get_current_user
from app.db import models
from app.schemas import mood as mood_schema
from app.services.mood import MoodService

router = APIRouter()


@router.post("", response_model=mood_schema.Mood)
def create_mood(
    mood_data: mood_schema.MoodCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new mood entry"""
    # Verify session ownership if session_id provided
    if mood_data.study_session_id:
        session = db.query(models.StudySession).filter(
            models.StudySession.id == mood_data.study_session_id,
            models.StudySession.user_id == current_user.id
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Study session not found")
    
    return MoodService.create_mood(db, current_user.id, mood_data)


@router.get("", response_model=List[mood_schema.Mood])
def get_user_moods(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all mood entries for the current user"""
    return MoodService.get_user_moods(db, current_user.id, skip, limit)


@router.get("/trends", response_model=List[mood_schema.MoodTrend])
def get_mood_trends(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get mood trends over time"""
    return MoodService.get_mood_trends(db, current_user.id, days)


@router.get("/stats", response_model=mood_schema.MoodStats)
def get_mood_stats(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get overall mood statistics"""
    return MoodService.get_mood_stats(db, current_user.id, days)


@router.get("/session/{session_id}", response_model=List[mood_schema.Mood])
def get_session_moods(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all mood entries for a specific study session"""
    # Verify session ownership
    session = db.query(models.StudySession).filter(
        models.StudySession.id == session_id,
        models.StudySession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Study session not found")
    
    return MoodService.get_session_moods(db, current_user.id, session_id)


@router.get("/{mood_id}", response_model=mood_schema.Mood)
def get_mood(
    mood_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific mood entry"""
    mood = MoodService.get_mood_by_id(db, mood_id, current_user.id)
    if not mood:
        raise HTTPException(status_code=404, detail="Mood not found")
    return mood


@router.put("/{mood_id}", response_model=mood_schema.Mood)
def update_mood(
    mood_id: int,
    mood_update: mood_schema.MoodUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update a mood entry"""
    mood = MoodService.update_mood(db, mood_id, current_user.id, mood_update)
    if not mood:
        raise HTTPException(status_code=404, detail="Mood not found")
    return mood


@router.delete("/{mood_id}")
def delete_mood(
    mood_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a mood entry"""
    success = MoodService.delete_mood(db, mood_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Mood not found")
    return {"message": "Mood deleted successfully"}

"""
API endpoints for study sessions
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.db import models
from app.db.deps import get_db
from app.services.study_session import (
    create_study_session,
    get_study_session_by_id,
    get_study_sessions_by_user,
    update_study_session,
    delete_study_session
)

router = APIRouter()

@router.get("/", response_model=List[schemas.StudySession])
def list_study_sessions(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve study sessions for current user
    """
    sessions = get_study_sessions_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return sessions

@router.post("/", response_model=schemas.StudySession)
def create_session(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
    session_in: schemas.StudySessionCreate,
) -> Any:
    """
    Create new study session
    """
    session = create_study_session(db, user_id=current_user.id, session_in=session_in)
    return session

@router.get("/{session_id}", response_model=schemas.StudySession)
def read_session(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
    session_id: int,
) -> Any:
    """
    Get study session by ID
    """
    session = get_study_session_by_id(db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Study session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return session

@router.put("/{session_id}", response_model=schemas.StudySession)
def update_session(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
    session_id: int,
    session_in: schemas.StudySessionUpdate,
) -> Any:
    """
    Update a study session
    """
    session = get_study_session_by_id(db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Study session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session = update_study_session(db, session=session, session_in=session_in)
    return session

@router.delete("/{session_id}", response_model=schemas.Message)
def delete_session(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
    session_id: int,
) -> Any:
    """
    Delete a study session
    """
    session = get_study_session_by_id(db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Study session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    delete_study_session(db, session_id=session_id)
    return {"message": "Study session deleted successfully"}
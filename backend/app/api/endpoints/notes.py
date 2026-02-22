"""
Note endpoints for managing study notes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.db import models
from app import schemas
from app.services.auth import get_current_user
from app.services import note as note_service

router = APIRouter()

@router.post("/", response_model=schemas.Note, status_code=status.HTTP_201_CREATED)
async def create_note(
    note: schemas.NoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new note
    """
    db_note = note_service.create_note(
        db=db,
        user_id=current_user.id,
        note_in=note
    )
    return db_note

@router.get("/", response_model=List[schemas.Note])
async def get_user_notes(
    skip: int = 0,
    limit: int = 100,
    session_id: Optional[int] = Query(None, description="Filter by session ID"),
    note_type: Optional[str] = Query(None, description="Filter by note type"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get all notes for the current user, optionally filtered by session or type
    """
    if session_id:
        notes = note_service.get_notes_by_session(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
    else:
        notes = note_service.get_notes_by_user(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=limit
        )
    
    # Filter by type if specified
    if note_type and notes:
        notes = [n for n in notes if n.type == note_type]
    
    return notes

@router.get("/{note_id}", response_model=schemas.Note)
async def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get a specific note by ID
    """
    note = note_service.get_note_by_id(db=db, note_id=note_id)
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found"
        )
    
    # Verify ownership
    if note.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this note"
        )
    
    return note

@router.put("/{note_id}", response_model=schemas.Note)
async def update_note(
    note_id: int,
    note_update: schemas.NoteUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update a note
    """
    # Get existing note
    db_note = note_service.get_note_by_id(db=db, note_id=note_id)
    
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found"
        )
    
    # Verify ownership
    if db_note.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this note"
        )
    
    # Update note
    updated_note = note_service.update_note(
        db=db,
        note_id=note_id,
        note=note_update
    )
    
    return updated_note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete a note
    """
    # Get existing note
    db_note = note_service.get_note_by_id(db=db, note_id=note_id)
    
    if not db_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with ID {note_id} not found"
        )
    
    # Verify ownership
    if db_note.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this note"
        )
    
    # Delete note
    note_service.delete_note(db=db, note_id=note_id)
    
    return None

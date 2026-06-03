"""
Note service
"""
from typing import Optional, List
from datetime import datetime

from sqlalchemy.orm import Session

from app import schemas
from app.db import models

def get_note_by_id(db: Session, note_id: int) -> Optional[models.Note]:
    """
    Get a note by ID
    """
    return db.query(models.Note).filter(models.Note.id == note_id).first()

def get_notes_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[models.Note]:
    """
    Get notes for a user
    """
    return db.query(models.Note)\
        .filter(models.Note.user_id == user_id)\
        .order_by(models.Note.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def get_notes_by_session(
    db: Session, session_id: int, user_id: int, skip: int = 0, limit: int = 100
) -> List[models.Note]:
    """
    Get notes for a study session (filtered by user for security)
    """
    return db.query(models.Note)\
        .filter(
            models.Note.session_id == session_id,
            models.Note.user_id == user_id
        )\
        .order_by(models.Note.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def create_note(
    db: Session, user_id: int, note_in: schemas.NoteCreate
) -> models.Note:
    """
    Create a new note
    """
    db_note = models.Note(
        user_id=user_id,
        content=note_in.content,
        type=note_in.type,
        session_id=note_in.session_id,
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def update_note(
    db: Session, note: models.Note, note_in: schemas.NoteUpdate
) -> models.Note:
    """
    Update a note
    """
    update_data = note_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(note, field, value)
    
    note.updated_at = datetime.utcnow()
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

def delete_note(db: Session, note_id: int) -> None:
    """
    Delete a note
    """
    note = get_note_by_id(db, note_id=note_id)
    if note:
        db.delete(note)
        db.commit()
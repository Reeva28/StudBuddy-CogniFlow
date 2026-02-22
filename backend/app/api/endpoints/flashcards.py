"""
Flashcard endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.db import models
from app.schemas import document as schemas
from app.services import flashcard as flashcard_service

router = APIRouter()


@router.post("/generate/{document_id}", response_model=List[schemas.Flashcard])
async def generate_flashcards_from_document(
    document_id: int,
    num_cards: int = 10,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Generate flashcards from a document using AI
    """
    # Check if document exists and belongs to user
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not document.content:
        raise HTTPException(status_code=400, detail="Document has no content to generate flashcards from")
    
    try:
        flashcards = await flashcard_service.generate_flashcards_for_document(
            db, document_id, num_cards
        )
        return flashcards
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate flashcards: {str(e)}")


@router.get("/document/{document_id}", response_model=List[schemas.Flashcard])
def get_flashcards_for_document(
    document_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Get all flashcards for a specific document
    """
    # Verify document belongs to user
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return flashcard_service.get_flashcards_by_document(db, document_id, skip, limit)


@router.get("/", response_model=List[schemas.Flashcard])
def get_all_flashcards(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Get all flashcards for the current user
    """
    return flashcard_service.get_flashcards_by_user(db, current_user.id, skip, limit)


@router.get("/due", response_model=List[schemas.Flashcard])
def get_due_flashcards(
    limit: int = 20,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Get flashcards that are due for review
    """
    return flashcard_service.get_flashcards_due_for_review(db, current_user.id, limit)


@router.get("/{flashcard_id}", response_model=schemas.Flashcard)
def get_flashcard(
    flashcard_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Get a specific flashcard
    """
    flashcard = flashcard_service.get_flashcard_by_id(db, flashcard_id)
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    # Verify flashcard belongs to user
    document = db.query(models.Document).filter(
        models.Document.id == flashcard.document_id
    ).first()
    
    if not document or document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this flashcard")
    
    return flashcard


@router.post("/", response_model=schemas.Flashcard, status_code=status.HTTP_201_CREATED)
def create_flashcard(
    flashcard: schemas.FlashcardCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Create a new flashcard manually
    """
    # Verify document belongs to user
    document = db.query(models.Document).filter(
        models.Document.id == flashcard.document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return flashcard_service.create_flashcard(db, flashcard.document_id, flashcard)


@router.put("/{flashcard_id}", response_model=schemas.Flashcard)
def update_flashcard(
    flashcard_id: int,
    flashcard: schemas.FlashcardUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Update a flashcard
    """
    db_flashcard = flashcard_service.get_flashcard_by_id(db, flashcard_id)
    if not db_flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    # Verify flashcard belongs to user
    document = db.query(models.Document).filter(
        models.Document.id == db_flashcard.document_id
    ).first()
    
    if not document or document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this flashcard")
    
    updated_flashcard = flashcard_service.update_flashcard(db, flashcard_id, flashcard)
    if not updated_flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    return updated_flashcard


@router.post("/{flashcard_id}/review", response_model=schemas.Flashcard)
def review_flashcard(
    flashcard_id: int,
    quality: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Record a flashcard review
    
    Quality scale (1-5):
    - 1: Complete blackout
    - 2: Incorrect but recognized
    - 3: Correct but difficult
    - 4: Correct with hesitation
    - 5: Perfect recall
    """
    if not 1 <= quality <= 5:
        raise HTTPException(status_code=400, detail="Quality must be between 1 and 5")
    
    db_flashcard = flashcard_service.get_flashcard_by_id(db, flashcard_id)
    if not db_flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    # Verify flashcard belongs to user
    document = db.query(models.Document).filter(
        models.Document.id == db_flashcard.document_id
    ).first()
    
    if not document or document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to review this flashcard")
    
    updated_flashcard = flashcard_service.record_flashcard_review(db, flashcard_id, quality)
    return updated_flashcard


@router.delete("/{flashcard_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flashcard(
    flashcard_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Delete a flashcard
    """
    db_flashcard = flashcard_service.get_flashcard_by_id(db, flashcard_id)
    if not db_flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    # Verify flashcard belongs to user
    document = db.query(models.Document).filter(
        models.Document.id == db_flashcard.document_id
    ).first()
    
    if not document or document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this flashcard")
    
    flashcard_service.delete_flashcard(db, flashcard_id)
    return None

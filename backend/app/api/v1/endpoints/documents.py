"""
API endpoints for documents
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.db import models
from app.db.deps import get_db
from app.services.document import (
    create_document,
    get_document_by_id,
    get_documents_by_user,
    process_document,
    get_document_summary,
    get_flashcards_for_document,
    delete_document
)

router = APIRouter()

@router.get("/", response_model=List[schemas.Document])
def list_documents(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve documents for current user
    """
    documents = get_documents_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return documents

@router.post("/upload", response_model=schemas.Document)
async def upload_document(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
    file: UploadFile = File(...),
    session_id: int = Form(None),
) -> Any:
    """
    Upload a new document
    """
    document = create_document(db, user_id=current_user.id, file=file, session_id=session_id)
    # Start background processing
    process_document(db, document_id=document.id)
    return document

@router.get("/{document_id}", response_model=schemas.Document)
def read_document(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
    document_id: int,
) -> Any:
    """
    Get document by ID
    """
    document = get_document_by_id(db, document_id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return document

@router.get("/{document_id}/summary", response_model=schemas.DocumentSummary)
def read_document_summary(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
    document_id: int,
) -> Any:
    """
    Get summary for a document
    """
    document = get_document_by_id(db, document_id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    summary = get_document_summary(db, document_id=document_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary

@router.get("/{document_id}/flashcards", response_model=List[schemas.Flashcard])
def read_document_flashcards(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
    document_id: int,
) -> Any:
    """
    Get flashcards for a document
    """
    document = get_document_by_id(db, document_id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    flashcards = get_flashcards_for_document(db, document_id=document_id)
    return flashcards

@router.delete("/{document_id}", response_model=schemas.Message)
def delete_document_endpoint(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
    document_id: int,
) -> Any:
    """
    Delete a document
    """
    document = get_document_by_id(db, document_id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    delete_document(db, document_id=document_id)
    return {"message": "Document deleted successfully"}
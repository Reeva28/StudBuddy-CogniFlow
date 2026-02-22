"""
Document processing endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.db import models
from app import schemas
from app.services.auth import get_current_user
from app.services.file_processor.document_processor import process_document, get_document_text
from app.services.summarizer.summarizer import generate_summary, generate_key_points, generate_flashcards, generate_quiz

router = APIRouter()

@router.get("/", response_model=List[schemas.Document])
async def list_documents(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    List all documents for the current user
    """
    documents = db.query(models.Document).filter(
        models.Document.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return documents

@router.post("/upload", response_model=schemas.Document)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Upload a document (PDF, DOCX, or TXT) for processing
    """
    # Check file extension
    allowed_extensions = ["pdf", "docx", "txt"]
    file_extension = file.filename.split(".")[-1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type .{file_extension} not allowed. Only PDF, DOCX, and TXT files are allowed."
        )
    
    # Save file content
    content = await file.read()
    
    # Create document record in database
    db_document = models.Document(
        filename=file.filename,
        file_type=file_extension,
        file_size=len(content),
        user_id=current_user.id,
        session_id=session_id,
        status="processing"
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Schedule background processing
    background_tasks.add_task(
        process_document,
        db=db,
        document_id=db_document.id,
        content=content,
        file_type=file_extension
    )
    
    return db_document

@router.get("/{document_id}", response_model=schemas.Document)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get document details by ID
    """
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    return document

@router.get("/{document_id}/summary", response_model=schemas.DocumentSummary)
async def get_document_summary(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get document summary
    """
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )
    
    # Check if document is processed
    if document.status != "processed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document is not processed yet. Current status: {document.status}"
        )
    
    # Get document summary from database
    summary = db.query(models.DocumentSummary).filter(
        models.DocumentSummary.document_id == document_id
    ).first()
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Summary for document with ID {document_id} not found"
        )
    
    return summary

@router.post("/{document_id}/flashcards", response_model=List[schemas.Flashcard])
async def create_flashcards(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Generate flashcards for a document
    """
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document or document.status != "processed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document not found or not fully processed"
        )
    
    # Get document text
    document_text = get_document_text(document_id, db)
    
    # Generate flashcards
    flashcards_data = generate_flashcards(document_text)
    
    # Save flashcards to database
    flashcards = []
    for fc_data in flashcards_data:
        flashcard = models.Flashcard(
            document_id=document_id,
            question=fc_data["question"],
            answer=fc_data["answer"]
        )
        db.add(flashcard)
        flashcards.append(flashcard)
    
    db.commit()
    
    return flashcards
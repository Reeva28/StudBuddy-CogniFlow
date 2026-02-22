"""
Document service
"""
from typing import Optional, List, Dict, Any
import os
import shutil
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app import schemas
from app.db import models
from app.services.ai import generate_document_summary, generate_flashcards

# Define allowed file types
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}

def get_document_by_id(db: Session, document_id: int) -> Optional[models.Document]:
    """
    Get a document by ID
    """
    return db.query(models.Document).filter(models.Document.id == document_id).first()

def get_documents_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[models.Document]:
    """
    Get documents for a user
    """
    return db.query(models.Document)\
        .filter(models.Document.user_id == user_id)\
        .order_by(models.Document.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def create_document(
    db: Session, user_id: int, file: UploadFile, session_id: Optional[int] = None
) -> models.Document:
    """
    Create a new document from an uploaded file
    """
    # Validate file type
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
    
    # Create document in database
    db_document = models.Document(
        user_id=user_id,
        session_id=session_id,
        filename=file.filename,
        file_type=file_extension,
        status="pending",
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Save file to disk
    upload_dir = Path(f"uploads/documents/{user_id}")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / f"{db_document.id}_{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update document with path
    db_document.file_path = str(file_path)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document

def process_document(db: Session, document_id: int) -> None:
    """
    Process a document (extract text, generate summary, etc.)
    This would typically be done in a background task
    """
    document = get_document_by_id(db, document_id)
    if not document:
        return
    
    try:
        # Update status
        document.status = "processing"
        db.add(document)
        db.commit()
        
        # Extract text from document
        content = extract_text_from_document(document)
        document.content = content
        db.add(document)
        db.commit()
        
        # Generate summary
        summary = generate_document_summary(content)
        db_summary = models.DocumentSummary(
            document_id=document.id,
            summary=summary["summary"],
            key_points=summary["key_points"],
        )
        db.add(db_summary)
        
        # Generate flashcards
        flashcards = generate_flashcards(content)
        for card in flashcards:
            db_flashcard = models.Flashcard(
                document_id=document.id,
                question=card["question"],
                answer=card["answer"],
                difficulty=card["difficulty"],
            )
            db.add(db_flashcard)
        
        # Update status to processed
        document.status = "processed"
        db.add(document)
        db.commit()
        
    except Exception as e:
        document.status = "error"
        document.error_message = str(e)
        db.add(document)
        db.commit()

def extract_text_from_document(document: models.Document) -> str:
    """
    Extract text from a document file
    This is a placeholder for actual extraction logic
    """
    # In a real implementation, this would use PyPDF2 for PDFs,
    # python-docx for DOCX files, etc.
    
    # For simplicity, we'll just return a placeholder
    return f"Extracted content from {document.filename}"

def get_document_summary(db: Session, document_id: int) -> Optional[models.DocumentSummary]:
    """
    Get summary for a document
    """
    return db.query(models.DocumentSummary).filter(
        models.DocumentSummary.document_id == document_id
    ).first()

def get_flashcards_for_document(db: Session, document_id: int) -> List[models.Flashcard]:
    """
    Get flashcards for a document
    """
    return db.query(models.Flashcard).filter(
        models.Flashcard.document_id == document_id
    ).all()

def delete_document(db: Session, document_id: int) -> None:
    """
    Delete a document
    """
    document = get_document_by_id(db, document_id)
    if document:
        # Delete related summary
        db.query(models.DocumentSummary).filter(
            models.DocumentSummary.document_id == document_id
        ).delete()
        
        # Delete related flashcards
        db.query(models.Flashcard).filter(
            models.Flashcard.document_id == document_id
        ).delete()
        
        # Delete the file if it exists
        if hasattr(document, 'file_path') and document.file_path:
            try:
                os.remove(document.file_path)
            except (FileNotFoundError, PermissionError):
                pass
        
        # Delete the document
        db.delete(document)
        db.commit()
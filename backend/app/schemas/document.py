"""
Document schemas for API validation
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field

class DocumentBase(BaseModel):
    """Base document model"""
    filename: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = 0
    status: Optional[str] = "pending"

class DocumentCreate(DocumentBase):
    """Document creation model - handled by the upload endpoint"""
    pass

class DocumentUpdate(DocumentBase):
    """Document update model"""
    status: Optional[str] = None
    error_message: Optional[str] = None

class DocumentInDBBase(DocumentBase):
    """Document in DB base model"""
    id: int
    user_id: int
    session_id: Optional[int] = None
    content: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Document(DocumentInDBBase):
    """Document response model"""
    pass

class DocumentSummaryBase(BaseModel):
    """Base document summary model"""
    summary: str
    key_points: Optional[List[str]] = None

class DocumentSummaryCreate(DocumentSummaryBase):
    """Document summary creation model"""
    document_id: int

class DocumentSummaryInDBBase(DocumentSummaryBase):
    """Document summary in DB base model"""
    id: int
    document_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentSummary(DocumentSummaryInDBBase):
    """Document summary response model"""
    pass

class FlashcardBase(BaseModel):
    """Base flashcard model"""
    question: str
    answer: str
    difficulty: int = 1

class FlashcardCreate(FlashcardBase):
    """Flashcard creation model"""
    document_id: int

class FlashcardUpdate(FlashcardBase):
    """Flashcard update model"""
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None

class FlashcardInDBBase(FlashcardBase):
    """Flashcard in DB base model"""
    id: int
    document_id: int
    created_at: datetime
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None

    class Config:
        from_attributes = True

class Flashcard(FlashcardInDBBase):
    """Flashcard response model"""
    pass
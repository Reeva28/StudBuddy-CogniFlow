"""
Document file processor for extracting text from various file formats
"""
import os
import tempfile
from typing import Dict, Any, BinaryIO, Optional
from sqlalchemy.orm import Session
import PyPDF2
from docx import Document
import traceback

from app.db import models

def extract_text_from_pdf(content: bytes) -> str:
    """
    Extract text from PDF file
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        text = ""
        with open(temp_file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        traceback.print_exc()
        return f"Error processing PDF: {str(e)}"

def extract_text_from_docx(content: bytes) -> str:
    """
    Extract text from DOCX file
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        doc = Document(temp_file_path)
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX: {str(e)}")
        return f"Error processing DOCX: {str(e)}"

def extract_text_from_txt(content: bytes) -> str:
    """
    Extract text from TXT file
    """
    try:
        return content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            return content.decode('latin-1')
        except Exception as e:
            print(f"Error extracting text from TXT: {str(e)}")
            return f"Error processing TXT: {str(e)}"

def process_document(db: Session, document_id: int, content: bytes, file_type: str) -> None:
    """
    Process document and extract text
    """
    try:
        # Get document from database
        document = db.query(models.Document).filter(models.Document.id == document_id).first()
        
        if not document:
            print(f"Document with ID {document_id} not found")
            return
        
        # Extract text based on file type
        if file_type == "pdf":
            text = extract_text_from_pdf(content)
        elif file_type == "docx":
            text = extract_text_from_docx(content)
        elif file_type == "txt":
            text = extract_text_from_txt(content)
        else:
            text = f"Unsupported file type: {file_type}"
        
        # Update document with extracted text
        document.content = text
        document.status = "processed"
        db.commit()
        
        # Generate AI-powered summary using Gemini
        from app.services.ai.gemini_client import GeminiClient
        
        gemini_client = GeminiClient()
        
        try:
            # Try AI-powered summary first (now synchronous)
            summary_data = gemini_client.generate_summary(text)
            summary = summary_data.get("summary", "Summary not available")
            key_points = summary_data.get("key_points", [])
        except Exception as e:
            print(f"AI summary failed, using TF-IDF fallback: {str(e)}")
            # Fallback to TF-IDF
            from app.services.summarizer.summarizer import generate_summary, generate_key_points
            summary = generate_summary(text)
            key_points = generate_key_points(text)
        
        # Save summary and key points to database
        db_summary = models.DocumentSummary(
            document_id=document_id,
            summary=summary,
            key_points=key_points
        )
        db.add(db_summary)
        db.commit()
        
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        traceback.print_exc()
        
        # Update document status to error
        document = db.query(models.Document).filter(models.Document.id == document_id).first()
        if document:
            document.status = "error"
            document.error_message = str(e)
            db.commit()

def get_document_text(document_id: int, db: Session) -> str:
    """
    Get the extracted text for a document
    """
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    
    if not document:
        return ""
    
    return document.content
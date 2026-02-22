"""
Endpoints for session summaries, concept maps, and quizzes
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.deps import get_db
from app.services.ai.concept_mapper import ConceptMapGenerator
from app.services.ai.openai_client import OpenAIClient
from app.core.exceptions import AIProcessingError

router = APIRouter()

@router.post("/sessions/{session_id}/summary")
async def generate_session_summary(
    session_id: int,
    output_format: str = "text",  # "text" or "concept_map"
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    concept_mapper: ConceptMapGenerator = Depends(lambda: ConceptMapGenerator(OpenAIClient()))
) -> Dict[str, Any]:
    """
    Generate a summary or concept map for a study session
    """
    # Retrieve session content from database
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user["id"]
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    try:
        # Get session content and user notes
        session_content = {
            "materials": session.materials,
            "topics": session.topics,
            "objectives": session.objectives,
            "progress": session.progress
        }
        
        # Generate summary or concept map
        result = await concept_mapper.generate_session_summary(
            session_content,
            session.notes,
            output_format
        )
        
        return result
    except AIProcessingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generating summary")

@router.post("/sessions/{session_id}/quiz")
async def generate_session_quiz(
    session_id: int,
    difficulty: int = 3,
    question_count: int = 5,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    concept_mapper: ConceptMapGenerator = Depends(lambda: ConceptMapGenerator(OpenAIClient()))
) -> List[Dict[str, Any]]:
    """
    Generate quiz questions based on session content
    """
    # Retrieve session
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user["id"]
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    try:
        # First analyze concepts
        session_content = {
            "materials": session.materials,
            "topics": session.topics,
            "objectives": session.objectives
        }
        
        concept_analysis = await concept_mapper._analyze_concepts(
            session_content,
            session.notes
        )
        
        # Generate quiz questions
        questions = await concept_mapper.generate_quiz_from_concepts(
            concept_analysis,
            difficulty,
            question_count
        )
        
        return questions
    except AIProcessingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generating quiz")
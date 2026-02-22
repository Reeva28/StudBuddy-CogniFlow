"""
Concept mapping endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.db import models
from app.schemas import concept as schemas
from app.services import concept_mapper

router = APIRouter()


@router.post("/generate/{document_id}", response_model=schemas.ConceptGraph)
async def generate_concept_map_for_document(
    document_id: int,
    request: schemas.ConceptExtractionRequest = schemas.ConceptExtractionRequest(),
    regenerate: bool = False,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Generate concept map from a document using  AI
    """
    # Check if document exists and belongs to user
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not document.content:
        raise HTTPException(
            status_code=400,
            detail="Document has no content to extract concepts from"
        )
    
    try:
        concept_graph = await concept_mapper.generate_concept_map(
            db, document_id, request.max_concepts, regenerate
        )
        return concept_graph
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate concept map: {str(e)}"
        )


@router.get("/{document_id}", response_model=schemas.ConceptGraph)
def get_concept_map(
    document_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Get existing concept map for a document
    """
    # Check if document exists and belongs to user
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    concept_graph = concept_mapper.get_concept_graph(db, document_id)
    return concept_graph


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_concept_map(
    document_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """
    Delete concept map for a document
    """
    # Check if document exists and belongs to user
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    concept_mapper.delete_concept_map(db, document_id)
    return None

"""
Study plan endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.db import models
from app import schemas
from app.services.auth import get_current_user
from app.services.planner.study_planner import generate_study_plan
from app.services.ai.gemini_client import GeminiClient

router = APIRouter()

@router.get("/", response_model=List[schemas.StudyPlan])
async def list_study_plans(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    List all study plans for the current user
    """
    plans = db.query(models.StudyPlan).filter(
        models.StudyPlan.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return plans

@router.post("/", response_model=schemas.StudyPlan)
async def create_study_plan(
    plan_request: schemas.StudyPlanCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Generate a personalized study plan based on user's goal and preferences
    """
    # Get user's past study sessions to analyze patterns
    past_sessions = db.query(models.StudySession).filter(
        models.StudySession.user_id == current_user.id,
        models.StudySession.status == "completed"
    ).order_by(models.StudySession.created_at.desc()).limit(10).all()
    
    # Try AI-powered study plan generation first
    gemini_client = GeminiClient()
    
    try:
        # Synchronous call now
        plan_data = gemini_client.generate_study_plan(
            goal=plan_request.goal,
            subject=plan_request.subject,
            duration_minutes=plan_request.duration_minutes,
            difficulty=plan_request.difficulty_level,
            prior_knowledge=None,
            learning_style=None
        )
        content = plan_data.get('plan', '')
    except Exception as e:
        print(f"AI plan generation failed, using rule-based fallback: {str(e)}")
        # Fallback to rule-based planner
        plan_data = generate_study_plan(
            goal=plan_request.goal,
            total_duration=plan_request.duration_minutes,
            subject=plan_request.subject,
            user_id=current_user.id,
            past_sessions=past_sessions
        )
        content = str(plan_data)
    
    # Create study plan in database
    db_plan = models.StudyPlan(
        user_id=current_user.id,
        goal=plan_request.goal,
        subject=plan_request.subject,
        duration_minutes=plan_request.duration_minutes,
        difficulty_level=plan_request.difficulty_level,
        content=content,
        plan_data=plan_data
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    
    return db_plan

@router.get("/", response_model=List[schemas.StudyPlan])
async def get_user_plans(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get all user's study plans
    """
    plans = db.query(models.StudyPlan).filter(
        models.StudyPlan.user_id == current_user.id
    ).order_by(models.StudyPlan.created_at.desc()).offset(skip).limit(limit).all()
    
    return plans

@router.get("/{plan_id}", response_model=schemas.StudyPlan)
async def get_study_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get a specific study plan by ID
    """
    plan = db.query(models.StudyPlan).filter(
        models.StudyPlan.id == plan_id,
        models.StudyPlan.user_id == current_user.id
    ).first()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study plan with ID {plan_id} not found"
        )
    
    return plan
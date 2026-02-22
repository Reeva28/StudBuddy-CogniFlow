"""
API endpoints for study plans
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.db import models
from app.db.deps import get_db
from app.services.study_plan import (
    create_study_plan,
    get_study_plan_by_id,
    get_study_plans_by_user,
    update_study_plan,
    delete_study_plan,
    generate_study_plan
)

router = APIRouter()

@router.get("/", response_model=List[schemas.StudyPlan])
def list_study_plans(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve study plans for current user
    """
    plans = get_study_plans_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return plans

@router.post("/", response_model=schemas.StudyPlan)
def create_plan(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
    plan_in: schemas.StudyPlanCreate,
) -> Any:
    """
    Create new study plan
    """
    plan = create_study_plan(db, user_id=current_user.id, plan_in=plan_in)
    return plan

@router.post("/generate", response_model=schemas.StudyPlan)
def generate_plan(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
    request: schemas.StudyPlanGenerateRequest,
) -> Any:
    """
    Generate a new study plan using AI
    """
    plan = generate_study_plan(
        db, 
        user_id=current_user.id,
        goal=request.goal,
        subject=request.subject,
        duration_minutes=request.duration_minutes,
        difficulty=request.difficulty,
        document_ids=request.document_ids
    )
    return plan

@router.get("/{plan_id}", response_model=schemas.StudyPlan)
def read_plan(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
    plan_id: int,
) -> Any:
    """
    Get study plan by ID
    """
    plan = get_study_plan_by_id(db, plan_id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    if plan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return plan

@router.put("/{plan_id}", response_model=schemas.StudyPlan)
def update_plan(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
    plan_id: int,
    plan_in: schemas.StudyPlanUpdate,
) -> Any:
    """
    Update a study plan
    """
    plan = get_study_plan_by_id(db, plan_id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    if plan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    plan = update_study_plan(db, plan=plan, plan_in=plan_in)
    return plan

@router.delete("/{plan_id}", response_model=schemas.Message)
def delete_plan(
    *,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_user),
    plan_id: int,
) -> Any:
    """
    Delete a study plan
    """
    plan = get_study_plan_by_id(db, plan_id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    if plan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    delete_study_plan(db, plan_id=plan_id)
    return {"message": "Study plan deleted successfully"}
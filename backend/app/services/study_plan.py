"""
Study plan service
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app import schemas
from app.db import models
from app.services.ai import generate_ai_study_plan

def get_study_plan_by_id(db: Session, plan_id: int) -> Optional[models.StudyPlan]:
    """
    Get a study plan by ID
    """
    return db.query(models.StudyPlan).filter(models.StudyPlan.id == plan_id).first()

def get_study_plans_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[models.StudyPlan]:
    """
    Get study plans for a user
    """
    return db.query(models.StudyPlan)\
        .filter(models.StudyPlan.user_id == user_id)\
        .order_by(models.StudyPlan.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()

def create_study_plan(
    db: Session, user_id: int, plan_in: schemas.StudyPlanCreate
) -> models.StudyPlan:
    """
    Create a new study plan
    """
    db_plan = models.StudyPlan(
        user_id=user_id,
        goal=plan_in.goal,
        subject=plan_in.subject,
        total_duration_minutes=plan_in.total_duration_minutes,
        plan_data=plan_in.plan_data,
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def update_study_plan(
    db: Session, plan: models.StudyPlan, plan_in: schemas.StudyPlanUpdate
) -> models.StudyPlan:
    """
    Update a study plan
    """
    update_data = plan_in.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(plan, field, value)
    
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

def delete_study_plan(db: Session, plan_id: int) -> None:
    """
    Delete a study plan
    """
    plan = get_study_plan_by_id(db, plan_id=plan_id)
    if plan:
        # Update related sessions to remove link
        db.query(models.StudySession).filter(
            models.StudySession.study_plan_id == plan_id
        ).update({"study_plan_id": None})
        
        # Delete the plan
        db.delete(plan)
        db.commit()

def generate_study_plan(
    db: Session, 
    user_id: int,
    goal: str,
    subject: str,
    duration_minutes: int,
    difficulty: int = 3,
    document_ids: Optional[List[int]] = None
) -> models.StudyPlan:
    """
    Generate a study plan using AI
    """
    # Gather document content for context if provided
    document_contents = []
    if document_ids:
        for doc_id in document_ids:
            doc = db.query(models.Document).filter(
                models.Document.id == doc_id, 
                models.Document.user_id == user_id
            ).first()
            if doc and doc.content:
                document_contents.append(doc.content)
    
    # Generate plan with AI
    ai_plan = generate_ai_study_plan(
        goal=goal,
        subject=subject,
        duration_minutes=duration_minutes,
        difficulty=difficulty,
        documents=document_contents
    )
    
    # Create plan in database
    db_plan = models.StudyPlan(
        user_id=user_id,
        goal=goal,
        subject=subject,
        total_duration_minutes=duration_minutes,
        plan_data=ai_plan,
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    
    # Create study sessions from plan
    if "sessions" in ai_plan:
        for session_data in ai_plan["sessions"]:
            db_session = models.StudySession(
                user_id=user_id,
                study_plan_id=db_plan.id,
                title=session_data.get("title", "Study Session"),
                goal=session_data.get("goal", goal),
                subject=subject,
                total_duration_minutes=session_data.get("duration_minutes", 25),
                status="planned"
            )
            db.add(db_session)
    
    db.commit()
    return db_plan
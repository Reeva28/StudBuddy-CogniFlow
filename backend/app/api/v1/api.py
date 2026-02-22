"""
API Router for v1 endpoints
"""
from fastapi import APIRouter

from app.api.v1.endpoints import users, study_sessions, documents, study_plans

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(study_sessions.router, prefix="/sessions", tags=["study sessions"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(study_plans.router, prefix="/study-plans", tags=["study plans"])
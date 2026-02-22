"""
API router for all endpoints
"""
from fastapi import APIRouter

from app.api.endpoints import users, sessions, documents, auth, study_plan, notes, analytics, flashcards, concept_map, mood

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(sessions.router, prefix="/study-sessions", tags=["study sessions"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(study_plan.router, prefix="/study-plans", tags=["study plans"])
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(flashcards.router, prefix="/flashcards", tags=["flashcards"])
api_router.include_router(concept_map.router, prefix="/concept-map", tags=["concept mapping"])
api_router.include_router(mood.router, prefix="/mood", tags=["mood tracking"])
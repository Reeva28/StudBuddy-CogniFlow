"""
Enhanced AI service with caching and rate limiting
"""
from typing import Dict, List, Any, Optional
from fastapi import HTTPException, Depends
from redis import Redis

from app.core.config import settings
from app.core.redis import get_redis
from app.core.rate_limit import RateLimiter
from app.services.ai.openai_client import OpenAIClient
from app.core.security import get_current_user

class AIService:
    def __init__(
        self,
        openai_client: OpenAIClient,
        redis: Redis = Depends(get_redis),
        rate_limiter: RateLimiter = Depends(),
        current_user: Dict = Depends(get_current_user)
    ):
        self.openai_client = openai_client
        self.redis = redis
        self.rate_limiter = rate_limiter
        self.current_user = current_user
    
    async def generate_document_summary(self, document_content: str) -> Dict[str, Any]:
        """Generate an AI-powered document summary with caching"""
        # Check rate limit
        await self.rate_limiter.check_limit("summary_generation", self.current_user["id"])
        
        # Check cache first
        cache_key = f"summary:{hash(document_content)}"
        if cached := self.redis.get(cache_key):
            return cached
            
        # Generate new summary
        try:
            summary = await self.openai_client.generate_summary(document_content)
            
            # Cache the result
            self.redis.setex(
                cache_key,
                settings.CACHE_EXPIRE_SECONDS,
                summary
            )
            
            return summary
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating summary: {str(e)}"
            )
    
    async def generate_study_plan(
        self,
        goal: str,
        subject: str,
        duration_minutes: int,
        difficulty: int = 3,
        prior_knowledge: Optional[str] = None,
        learning_style: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a personalized study plan with caching"""
        # Check rate limit
        await self.rate_limiter.check_limit("plan_generation", self.current_user["id"])
        
        # Generate cache key from input parameters
        cache_key = f"plan:{hash((goal, subject, duration_minutes, difficulty, prior_knowledge, learning_style))}"
        if cached := self.redis.get(cache_key):
            return cached
            
        try:
            plan = await self.openai_client.generate_study_plan(
                goal,
                subject,
                duration_minutes,
                difficulty,
                prior_knowledge,
                learning_style
            )
            
            # Cache the result
            self.redis.setex(
                cache_key,
                settings.CACHE_EXPIRE_SECONDS,
                plan
            )
            
            return plan
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating study plan: {str(e)}"
            )
    
    async def generate_practice_questions(
        self,
        content: str,
        difficulty: int = 3,
        question_count: int = 5,
        question_types: List[str] = ["multiple_choice", "open_ended"]
    ) -> List[Dict[str, Any]]:
        """Generate practice questions with caching"""
        # Check rate limit
        await self.rate_limiter.check_limit("question_generation", self.current_user["id"])
        
        # Check cache
        cache_key = f"questions:{hash((content, difficulty, question_count, tuple(question_types)))}"
        if cached := self.redis.get(cache_key):
            return cached
            
        try:
            questions = await self.openai_client.generate_practice_questions(
                content,
                difficulty,
                question_count,
                question_types
            )
            
            # Cache the result
            self.redis.setex(
                cache_key,
                settings.CACHE_EXPIRE_SECONDS,
                questions
            )
            
            return questions
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating questions: {str(e)}"
            )
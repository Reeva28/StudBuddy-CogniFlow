"""
Rate limiting implementation using Redis
"""
from fastapi import HTTPException, Depends
from redis import Redis
import time
from typing import Optional

from app.core.redis import get_redis
from app.core.config import settings

class RateLimiter:
    def __init__(self, redis: Redis = Depends(get_redis)):
        self.redis = redis
        self.rate_limits = {
            "summary_generation": {"requests": 10, "period": 3600},  # 10 requests per hour
            "plan_generation": {"requests": 20, "period": 3600},     # 20 requests per hour
            "question_generation": {"requests": 50, "period": 3600}, # 50 requests per hour
            "default": {"requests": 100, "period": 3600}            # 100 requests per hour
        }
    
    async def check_limit(self, action: str, user_id: int) -> None:
        """
        Check if the user has exceeded their rate limit for the given action
        
        Args:
            action: The action being rate limited
            user_id: The ID of the user performing the action
            
        Raises:
            HTTPException: If the rate limit has been exceeded
        """
        limit = self.rate_limits.get(action, self.rate_limits["default"])
        key = f"rate_limit:{action}:{user_id}"
        
        # Get current count and timestamp
        current = self.redis.get(key)
        now = int(time.time())
        
        if current is None:
            # First request
            self.redis.setex(key, limit["period"], 1)
        else:
            count = int(current)
            if count >= limit["requests"]:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded for {action}. Try again later."
                )
            self.redis.incr(key)
    
    async def get_remaining_requests(self, action: str, user_id: int) -> dict:
        """Get remaining requests and reset time for rate limit"""
        limit = self.rate_limits.get(action, self.rate_limits["default"])
        key = f"rate_limit:{action}:{user_id}"
        
        current = self.redis.get(key)
        ttl = self.redis.ttl(key)
        
        if current is None:
            return {
                "remaining": limit["requests"],
                "reset_in_seconds": limit["period"]
            }
        
        return {
            "remaining": limit["requests"] - int(current),
            "reset_in_seconds": ttl
        }
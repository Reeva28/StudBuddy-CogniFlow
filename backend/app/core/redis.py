"""
Redis configuration and connection management
"""
from redis import Redis
from fastapi import Depends

from app.core.config import settings

_redis_client: Redis = None

def get_redis() -> Redis:
    """
    Get Redis connection instance
    Returns:
        Redis: Redis connection instance
    """
    global _redis_client
    
    if _redis_client is None:
        _redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
    
    return _redis_client

def init_redis():
    """Initialize Redis connection"""
    global _redis_client
    
    try:
        redis = get_redis()
        redis.ping()  # Test connection
        return redis
    except Exception as e:
        raise Exception(f"Could not connect to Redis: {str(e)}")

def close_redis():
    """Close Redis connection"""
    global _redis_client
    
    if _redis_client is not None:
        _redis_client.close()
        _redis_client = None
"""
Base schemas for API validation
"""
from typing import Any, Dict, Optional

from pydantic import BaseModel

class Message(BaseModel):
    """Simple message response model"""
    message: str
"""
API dependencies
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.deps import get_db
from app.db import models

# Import the working authentication function
from app.services.auth import get_current_user
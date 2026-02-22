"""
User service
"""
from typing import Optional, List

from sqlalchemy.orm import Session

from app import schemas
from app.core.security import get_password_hash, verify_password
from app.db import models

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """
    Get a user by email
    """
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """
    Get a user by username
    """
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[models.User]:
    """
    Get a user by ID
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """
    Get all users
    """
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user_in: schemas.UserCreate) -> models.User:
    """
    Create a new user
    """
    # Check if user already exists
    user = get_user_by_email(db, email=user_in.email)
    if user:
        raise ValueError("Email already registered")
    
    user = get_user_by_username(db, username=user_in.username)
    if user:
        raise ValueError("Username already taken")
    
    # Create new user
    db_user = models.User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """
    Authenticate a user
    """
    user = get_user_by_username(db, username=username)
    if not user:
        user = get_user_by_email(db, email=username)
        if not user:
            return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user

def update_user(db: Session, user: models.User, user_in: schemas.UserUpdate) -> models.User:
    """
    Update a user
    """
    update_data = user_in.dict(exclude_unset=True)
    
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
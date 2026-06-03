"""
Script to create a test user in the database
"""
from sqlalchemy.orm import Session
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.db import models
from app.services.auth import get_password_hash

def create_user():
    # Create a session
    db = SessionLocal()
    
    # Check if user already exists
    user = db.query(models.User).filter(models.User.email == "test@example.com").first()
    if user:
        print("User already exists")
        db.close()
        return
        
    # Create user
    hashed_password = get_password_hash("testpassword")
    user = models.User(
        email="test@example.com", 
        username="testuser", 
        full_name="Test User",
        hashed_password=hashed_password
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    
    print("Test user created successfully")
    print("Email: test@example.com")
    print("Password: testpassword")

if __name__ == "__main__":
    create_user()
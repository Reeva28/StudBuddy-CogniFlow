"""
Script to create a test user in the database
"""
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.db.models import Base, User

# Create password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create a test user
    db = SessionLocal()
    
    # Check if user already exists
    user = db.query(User).filter(User.email == "test@example.com").first()
    if user:
        print("User already exists")
        db.close()
        return
        
    # Create user
    hashed_password = pwd_context.hash("testpassword")
    user = User(
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
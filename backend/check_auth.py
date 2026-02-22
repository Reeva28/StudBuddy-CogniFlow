"""
Debug authentication issue
"""
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.db.models import Base, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def check_users():
    db = SessionLocal()
    
    users = db.query(User).all()
    print(f"\nFound {len(users)} users in database:")
    
    for user in users:
        print(f"\nUser ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Full Name: {user.full_name}")
        print(f"Hashed Password: {user.hashed_password[:50]}...")
        
        # Test password verification
        test_password = "testpassword"
        is_valid = pwd_context.verify(test_password, user.hashed_password)
        print(f"Password 'testpassword' valid: {is_valid}")
    
    db.close()

if __name__ == "__main__":
    check_users()

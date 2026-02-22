"""
Database connection and session management
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get the database URL from environment variables or use a default SQLite URL
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./app.db")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency
def get_db():
    """
    Dependency for FastAPI endpoints that need a database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
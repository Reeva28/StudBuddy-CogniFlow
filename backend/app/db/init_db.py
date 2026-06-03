"""
Database initialization script
"""
from app.db.session import Base, engine
from app.db import models

def init_db():
    """
    Initialize the database tables
    """
    # Create tables
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully.")
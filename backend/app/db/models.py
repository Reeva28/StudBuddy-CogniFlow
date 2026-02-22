"""
Database models for CogniFlow
"""
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, JSON, Float
from sqlalchemy.orm import relationship

from app.db.session import Base

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    full_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = relationship("StudySession", back_populates="user")
    study_plans = relationship("StudyPlan", back_populates="user")
    documents = relationship("Document", back_populates="user")
    notes = relationship("Note", back_populates="user")
    moods = relationship("Mood", back_populates="user")

class StudyPlan(Base):
    """Study Plan model"""
    __tablename__ = "study_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    goal = Column(String(255), nullable=False)
    subject = Column(String(100))
    duration_minutes = Column(Integer, default=0)
    difficulty_level = Column(Integer, default=3)
    content = Column(Text, nullable=True)
    plan_data = Column(JSON)  # Stores sessions, recommendations, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="study_plans")
    sessions = relationship("StudySession", back_populates="study_plan")

class StudySession(Base):
    """Study Session model"""
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    study_plan_id = Column(Integer, ForeignKey("study_plans.id"), nullable=True)
    title = Column(String(100))
    goal = Column(String(255))
    subject = Column(String(100))
    
    # Duration and timing
    total_duration_minutes = Column(Integer, default=0)
    actual_duration_minutes = Column(Integer, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    
    # Status tracking
    status = Column(String(20), default="planned")  # planned, active, completed, abandoned
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Analytics
    focus_rating = Column(Integer, nullable=True)
    productivity_rating = Column(Integer, nullable=True)
    mood_before = Column(String(50), nullable=True)
    mood_after = Column(String(50), nullable=True)
    reflection = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    study_plan = relationship("StudyPlan", back_populates="sessions")
    documents = relationship("Document", back_populates="session")
    pomodoros = relationship("Pomodoro", back_populates="session")
    notes = relationship("Note", back_populates="session")
    moods = relationship("Mood", back_populates="study_session")

class Pomodoro(Base):
    """Pomodoro session model"""
    __tablename__ = "pomodoros"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("study_sessions.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, default=25)
    break_duration_minutes = Column(Integer, default=5)
    completed = Column(Boolean, default=False)
    
    # Relationships
    session = relationship("StudySession", back_populates="pomodoros")

class Document(Base):
    """Document model"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(Integer, ForeignKey("study_sessions.id"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # pdf, docx, txt
    file_size = Column(Integer, default=0)  # file size in bytes
    content = Column(Text, nullable=True)
    status = Column(String(20), default="pending")  # pending, processing, processed, error
    error_message = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    session = relationship("StudySession", back_populates="documents")
    summary = relationship("DocumentSummary", back_populates="document", uselist=False)
    flashcards = relationship("Flashcard", back_populates="document")

class DocumentSummary(Base):
    """Document summary model"""
    __tablename__ = "document_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), unique=True)
    summary = Column(Text, nullable=False)
    key_points = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="summary")

class Flashcard(Base):
    """Flashcard model"""
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    difficulty = Column(Integer, default=1)  # 1-5 difficulty rating
    created_at = Column(DateTime, default=datetime.utcnow)
    last_reviewed = Column(DateTime, nullable=True)
    next_review = Column(DateTime, nullable=True)
    
    # Relationships
    document = relationship("Document", back_populates="flashcards")

class Note(Base):
    """Note model"""
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(Integer, ForeignKey("study_sessions.id"), nullable=True)
    content = Column(Text, nullable=False)
    type = Column(String(20), default="general")  # general, question, distraction, insight
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notes")
    session = relationship("StudySession", back_populates="notes")

class ConceptNode(Base):
    """Concept Node model for knowledge graph"""
    __tablename__ = "concept_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    importance = Column(Float, default=0.5)  # 0.0-1.0
    type = Column(String(50), default="concept")  # concept, definition, example, principle
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document")
    outgoing_edges = relationship("ConceptRelationship", foreign_keys="ConceptRelationship.source_id", back_populates="source")
    incoming_edges = relationship("ConceptRelationship", foreign_keys="ConceptRelationship.target_id", back_populates="target")

class ConceptRelationship(Base):
    """Concept Relationship model for knowledge graph edges"""
    __tablename__ = "concept_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("concept_nodes.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("concept_nodes.id"), nullable=False)
    relationship_type = Column(String(50), default="relates_to")  # relates_to, depends_on, is_example_of, contradicts
    strength = Column(Float, default=0.5)  # 0.0-1.0
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    source = relationship("ConceptNode", foreign_keys=[source_id], back_populates="outgoing_edges")
    target = relationship("ConceptNode", foreign_keys=[target_id], back_populates="incoming_edges")

class Mood(Base):
    """Mood tracking model"""
    __tablename__ = "moods"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    study_session_id = Column(Integer, ForeignKey("study_sessions.id"), nullable=True)
    mood_type = Column(String(50), nullable=False)  # happy, focused, stressed, tired, energized, frustrated, motivated
    intensity = Column(Integer, nullable=False)  # 1-5 scale
    recorded_at = Column(DateTime, default=datetime.utcnow)
    is_before_session = Column(Boolean, nullable=False)  # True if recorded before session, False if after
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="moods")
    study_session = relationship("StudySession", back_populates="moods")
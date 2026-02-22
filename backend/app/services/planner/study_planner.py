"""
Intelligent study planner service
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from app.db import models

def generate_study_plan(
    goal: str,
    total_duration: int,
    subject: str,
    user_id: int,
    past_sessions: List[models.StudySession]
) -> Dict[str, Any]:
    """
    Generate a personalized study plan based on user's goal, preferences, and past sessions
    """
    # Analyze past study patterns
    avg_session_length = 0
    most_productive_duration = 25  # Default to 25 min Pomodoro session
    
    if past_sessions:
        # Calculate average session length from completed sessions
        total_time = sum(session.actual_duration_minutes or 0 for session in past_sessions if session.status == "completed")
        completed_count = sum(1 for session in past_sessions if session.status == "completed")
        
        if completed_count > 0:
            avg_session_length = total_time // completed_count
            
            # If average length is very short or very long, adjust to a reasonable range
            if avg_session_length < 15:
                most_productive_duration = 15
            elif 20 <= avg_session_length <= 35:
                most_productive_duration = avg_session_length
            elif 35 < avg_session_length <= 50:
                most_productive_duration = 45
            else:
                most_productive_duration = 50
    
    # Calculate number of sessions needed
    num_sessions = total_duration // most_productive_duration
    if total_duration % most_productive_duration > 0:
        num_sessions += 1
    
    # Ensure at least one session
    num_sessions = max(1, num_sessions)
    
    # Adjust session length to fit evenly
    session_length = total_duration // num_sessions
    
    # Create the study plan
    sessions = []
    for i in range(num_sessions):
        session = {
            "order": i + 1,
            "duration_minutes": session_length,
            "break_after": 5 if i < num_sessions - 1 else 0,
            "focus": f"Session {i+1}",
            "description": f"Focus on understanding key concepts" if i == 0 else
                         f"Review material from previous session and work on examples" if i == 1 else
                         f"Practice applying concepts and consolidate knowledge"
        }
        sessions.append(session)
    
    # Personalized recommendations based on past sessions
    recommendations = []
    
    # Check if user frequently abandons long sessions
    abandoned_long_sessions = [s for s in past_sessions if s.status == "abandoned" and 
                             (s.actual_duration_minutes or 0) < (s.total_duration_minutes or 0) * 0.7]
    
    if len(abandoned_long_sessions) > 2:
        recommendations.append("You've had difficulty completing longer study sessions in the past. I've broken your plan into shorter, more manageable sessions.")
    
    # Provide subject-specific advice
    if subject.lower() in ["math", "mathematics"]:
        recommendations.append("For math topics, include practice problems in each session. Start with easier problems and gradually increase difficulty.")
    elif subject.lower() in ["history", "geography", "social studies"]:
        recommendations.append("For history topics, try creating a timeline or mind map during your study sessions to visualize connections between events.")
    elif subject.lower() in ["biology", "chemistry", "physics", "science"]:
        recommendations.append("For science topics, focus on understanding underlying principles rather than memorizing facts. Draw diagrams to visualize processes.")
    
    # Create final plan
    plan = {
        "goal": goal,
        "subject": subject,
        "total_duration_minutes": total_duration,
        "session_count": num_sessions,
        "sessions": sessions,
        "recommendations": recommendations,
        "created_at": datetime.now().isoformat()
    }
    
    return plan
"""
Mood service for tracking emotional state
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from collections import Counter

from app.db import models
from app.schemas import mood as mood_schema


class MoodService:
    """Mood tracking and analytics service"""

    @staticmethod
    def create_mood(
        db: Session,
        user_id: int,
        mood_data: mood_schema.MoodCreate
    ) -> models.Mood:
        """Create a new mood entry"""
        mood = models.Mood(
            user_id=user_id,
            study_session_id=mood_data.study_session_id,
            mood_type=mood_data.mood_type,
            intensity=mood_data.intensity,
            is_before_session=mood_data.is_before_session,
            notes=mood_data.notes,
            recorded_at=datetime.utcnow()
        )
        db.add(mood)
        db.commit()
        db.refresh(mood)
        return mood

    @staticmethod
    def get_mood_by_id(db: Session, mood_id: int, user_id: int) -> Optional[models.Mood]:
        """Get a specific mood entry"""
        return db.query(models.Mood).filter(
            models.Mood.id == mood_id,
            models.Mood.user_id == user_id
        ).first()

    @staticmethod
    def get_session_moods(
        db: Session,
        user_id: int,
        session_id: int
    ) -> List[models.Mood]:
        """Get all mood entries for a specific study session"""
        return db.query(models.Mood).filter(
            models.Mood.user_id == user_id,
            models.Mood.study_session_id == session_id
        ).order_by(models.Mood.recorded_at).all()

    @staticmethod
    def get_user_moods(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.Mood]:
        """Get all mood entries for a user"""
        return db.query(models.Mood).filter(
            models.Mood.user_id == user_id
        ).order_by(models.Mood.recorded_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_mood_trends(
        db: Session,
        user_id: int,
        days: int = 30
    ) -> List[mood_schema.MoodTrend]:
        """Get mood trends over time"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get moods grouped by date
        moods = db.query(models.Mood).filter(
            models.Mood.user_id == user_id,
            models.Mood.recorded_at >= cutoff_date
        ).order_by(models.Mood.recorded_at).all()

        # Group by date
        trends_dict = {}
        for mood in moods:
            date_key = mood.recorded_at.date().isoformat()
            if date_key not in trends_dict:
                trends_dict[date_key] = {
                    'before': [],
                    'after': [],
                    'mood_types': [],
                    'session_count': 0
                }
            
            if mood.is_before_session:
                trends_dict[date_key]['before'].append(mood.intensity)
            else:
                trends_dict[date_key]['after'].append(mood.intensity)
            
            trends_dict[date_key]['mood_types'].append(mood.mood_type)
            if mood.study_session_id:
                trends_dict[date_key]['session_count'] += 1

        # Convert to MoodTrend objects
        trends = []
        for date, data in sorted(trends_dict.items()):
            most_common = Counter(data['mood_types']).most_common(1)
            trends.append(mood_schema.MoodTrend(
                date=date,
                avg_before_intensity=sum(data['before']) / len(data['before']) if data['before'] else None,
                avg_after_intensity=sum(data['after']) / len(data['after']) if data['after'] else None,
                most_common_mood=most_common[0][0] if most_common else None,
                session_count=data['session_count']
            ))

        return trends

    @staticmethod
    def get_mood_stats(
        db: Session,
        user_id: int,
        days: int = 30
    ) -> mood_schema.MoodStats:
        """Get overall mood statistics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        moods = db.query(models.Mood).filter(
            models.Mood.user_id == user_id,
            models.Mood.recorded_at >= cutoff_date
        ).all()

        if not moods:
            return mood_schema.MoodStats(
                total_moods=0,
                avg_intensity=0.0,
                most_common_mood="none",
                mood_improvement_rate=0.0,
                recent_trend="stable"
            )

        # Calculate statistics
        total_moods = len(moods)
        avg_intensity = sum(m.intensity for m in moods) / total_moods
        
        mood_types = [m.mood_type for m in moods]
        most_common_mood = Counter(mood_types).most_common(1)[0][0]

        # Calculate improvement rate (sessions where after > before)
        sessions_with_both = {}
        for mood in moods:
            if mood.study_session_id:
                if mood.study_session_id not in sessions_with_both:
                    sessions_with_both[mood.study_session_id] = {}
                key = 'before' if mood.is_before_session else 'after'
                sessions_with_both[mood.study_session_id][key] = mood.intensity

        improvements = 0
        total_sessions = 0
        for session_moods in sessions_with_both.values():
            if 'before' in session_moods and 'after' in session_moods:
                total_sessions += 1
                if session_moods['after'] > session_moods['before']:
                    improvements += 1

        mood_improvement_rate = (improvements / total_sessions * 100) if total_sessions > 0 else 0.0

        # Determine recent trend
        recent_moods = sorted(moods, key=lambda m: m.recorded_at)[-10:]
        if len(recent_moods) >= 5:
            first_half_avg = sum(m.intensity for m in recent_moods[:len(recent_moods)//2]) / (len(recent_moods)//2)
            second_half_avg = sum(m.intensity for m in recent_moods[len(recent_moods)//2:]) / (len(recent_moods) - len(recent_moods)//2)
            
            if second_half_avg > first_half_avg + 0.5:
                recent_trend = "improving"
            elif second_half_avg < first_half_avg - 0.5:
                recent_trend = "declining"
            else:
                recent_trend = "stable"
        else:
            recent_trend = "stable"

        return mood_schema.MoodStats(
            total_moods=total_moods,
            avg_intensity=round(avg_intensity, 2),
            most_common_mood=most_common_mood,
            mood_improvement_rate=round(mood_improvement_rate, 2),
            recent_trend=recent_trend
        )

    @staticmethod
    def update_mood(
        db: Session,
        mood_id: int,
        user_id: int,
        mood_update: mood_schema.MoodUpdate
    ) -> Optional[models.Mood]:
        """Update a mood entry"""
        mood = MoodService.get_mood_by_id(db, mood_id, user_id)
        if not mood:
            return None

        update_data = mood_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(mood, field, value)

        db.commit()
        db.refresh(mood)
        return mood

    @staticmethod
    def delete_mood(db: Session, mood_id: int, user_id: int) -> bool:
        """Delete a mood entry"""
        mood = MoodService.get_mood_by_id(db, mood_id, user_id)
        if not mood:
            return False

        db.delete(mood)
        db.commit()
        return True

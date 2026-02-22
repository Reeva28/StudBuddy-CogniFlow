"""
Flashcard service for generating and managing flashcards
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.db import models
from app.schemas import document as schemas
from app.services.ai.gemini_client import GeminiClient


class FlashcardGenerator:
    """Generate flashcards from document content using AI"""
    
    def __init__(self):
        self.gemini_client = GeminiClient()
    
    async def generate_flashcards(
        self, 
        document_content: str, 
        num_cards: int = 10
    ) -> List[dict]:
        """Generate flashcards from document content"""
        
        prompt = f"""Generate {num_cards} educational flashcards from the following document content. 
        
Each flashcard should have:
- A clear, concise question
- A complete, accurate answer
- A difficulty rating (1-5, where 1 is easiest)

Focus on key concepts, definitions, important facts, and relationships between ideas.

Document content:
{document_content[:4000]}

Return the flashcards in this exact JSON format:
{{
  "flashcards": [
    {{
      "question": "Question text here",
      "answer": "Answer text here",
      "difficulty": 3
    }}
  ]
}}"""

        response = await self.gemini_client.generate_text(prompt)
        
        # Parse the response
        import json
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            data = json.loads(json_str)
            return data.get("flashcards", [])
        except json.JSONDecodeError:
            # Fallback: try to extract question-answer pairs manually
            return self._parse_flashcards_from_text(response, num_cards)
    
    def _parse_flashcards_from_text(self, text: str, num_cards: int) -> List[dict]:
        """Fallback parser for non-JSON responses"""
        flashcards = []
        lines = text.split('\n')
        
        current_card = {}
        for line in lines:
            line = line.strip()
            if line.startswith(('Q:', 'Question:')):
                if current_card:
                    flashcards.append(current_card)
                current_card = {'question': line.split(':', 1)[1].strip()}
            elif line.startswith(('A:', 'Answer:')):
                current_card['answer'] = line.split(':', 1)[1].strip()
                current_card['difficulty'] = 3
        
        if current_card and 'question' in current_card and 'answer' in current_card:
            flashcards.append(current_card)
        
        return flashcards[:num_cards]


def get_flashcard_by_id(db: Session, flashcard_id: int) -> Optional[models.Flashcard]:
    """Get a flashcard by ID"""
    return db.query(models.Flashcard).filter(models.Flashcard.id == flashcard_id).first()


def get_flashcards_by_document(
    db: Session, document_id: int, skip: int = 0, limit: int = 100
) -> List[models.Flashcard]:
    """Get all flashcards for a document"""
    return db.query(models.Flashcard)\
        .filter(models.Flashcard.document_id == document_id)\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_flashcards_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[models.Flashcard]:
    """Get all flashcards for a user across all documents"""
    return db.query(models.Flashcard)\
        .join(models.Document)\
        .filter(models.Document.user_id == user_id)\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_flashcards_due_for_review(
    db: Session, user_id: int, limit: int = 20
) -> List[models.Flashcard]:
    """Get flashcards that are due for review based on spaced repetition"""
    now = datetime.utcnow()
    return db.query(models.Flashcard)\
        .join(models.Document)\
        .filter(
            models.Document.user_id == user_id,
            models.Flashcard.next_review <= now
        )\
        .order_by(models.Flashcard.next_review)\
        .limit(limit)\
        .all()


def create_flashcard(
    db: Session, document_id: int, flashcard_in: schemas.FlashcardCreate
) -> models.Flashcard:
    """Create a new flashcard"""
    db_flashcard = models.Flashcard(
        document_id=document_id,
        question=flashcard_in.question,
        answer=flashcard_in.answer,
        difficulty=flashcard_in.difficulty or 3,
        next_review=datetime.utcnow()  # Available for immediate review
    )
    db.add(db_flashcard)
    db.commit()
    db.refresh(db_flashcard)
    return db_flashcard


def create_flashcards_bulk(
    db: Session, document_id: int, flashcards_data: List[dict]
) -> List[models.Flashcard]:
    """Create multiple flashcards at once"""
    db_flashcards = []
    for card_data in flashcards_data:
        db_flashcard = models.Flashcard(
            document_id=document_id,
            question=card_data.get('question', ''),
            answer=card_data.get('answer', ''),
            difficulty=card_data.get('difficulty', 3),
            next_review=datetime.utcnow()
        )
        db_flashcards.append(db_flashcard)
    
    db.add_all(db_flashcards)
    db.commit()
    for card in db_flashcards:
        db.refresh(card)
    
    return db_flashcards


def update_flashcard(
    db: Session, flashcard_id: int, flashcard_in: schemas.FlashcardUpdate
) -> Optional[models.Flashcard]:
    """Update a flashcard"""
    db_flashcard = get_flashcard_by_id(db, flashcard_id)
    if not db_flashcard:
        return None
    
    if flashcard_in.question is not None:
        db_flashcard.question = flashcard_in.question
    if flashcard_in.answer is not None:
        db_flashcard.answer = flashcard_in.answer
    if flashcard_in.difficulty is not None:
        db_flashcard.difficulty = flashcard_in.difficulty
    
    db.commit()
    db.refresh(db_flashcard)
    return db_flashcard


def record_flashcard_review(
    db: Session, flashcard_id: int, quality: int
) -> Optional[models.Flashcard]:
    """
    Record a flashcard review and calculate next review date using spaced repetition
    
    Args:
        flashcard_id: ID of the flashcard
        quality: Quality of recall (1-5):
            1 = Complete blackout
            2 = Incorrect but recognized
            3 = Correct but difficult
            4 = Correct with hesitation
            5 = Perfect recall
    """
    db_flashcard = get_flashcard_by_id(db, flashcard_id)
    if not db_flashcard:
        return None
    
    now = datetime.utcnow()
    db_flashcard.last_reviewed = now
    
    # Simple spaced repetition algorithm (SM-2 inspired)
    interval_days = calculate_next_interval(quality, db_flashcard.difficulty)
    db_flashcard.next_review = now + timedelta(days=interval_days)
    
    db.commit()
    db.refresh(db_flashcard)
    return db_flashcard


def calculate_next_interval(quality: int, difficulty: int) -> int:
    """
    Calculate the next review interval in days
    
    Based on quality of recall and current difficulty:
    - Quality 1-2: Review again soon (0-1 days)
    - Quality 3: Short interval (2-4 days)
    - Quality 4: Medium interval (5-10 days)
    - Quality 5: Long interval (10-30 days)
    """
    if quality <= 2:
        return 0  # Review today
    elif quality == 3:
        return 2 + difficulty  # 2-7 days
    elif quality == 4:
        return 5 + (difficulty * 2)  # 7-15 days
    else:  # quality == 5
        return 10 + (difficulty * 4)  # 14-30 days


def delete_flashcard(db: Session, flashcard_id: int) -> bool:
    """Delete a flashcard"""
    db_flashcard = get_flashcard_by_id(db, flashcard_id)
    if not db_flashcard:
        return False
    
    db.delete(db_flashcard)
    db.commit()
    return True


async def generate_flashcards_for_document(
    db: Session, document_id: int, num_cards: int = 10
) -> List[models.Flashcard]:
    """Generate flashcards for a document using AI"""
    # Get the document
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document or not document.content:
        raise ValueError("Document not found or has no content")
    
    # Generate flashcards
    generator = FlashcardGenerator()
    flashcards_data = await generator.generate_flashcards(document.content, num_cards)
    
    # Save to database
    if flashcards_data:
        return create_flashcards_bulk(db, document_id, flashcards_data)
    
    return []

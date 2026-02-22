"""
Enhanced study session schemas with support for summaries and concept maps
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class SessionSummaryRequest(BaseModel):
    output_format: str = Field("text", description="Output format: 'text' or 'concept_map'")
    include_notes: bool = Field(True, description="Whether to include user notes in the summary")

class ConceptMapData(BaseModel):
    image: str = Field(..., description="Base64 encoded PNG image of the concept map")
    graph_data: Dict[str, Any] = Field(..., description="Raw graph data for interactive features")

class TextSummarySection(BaseModel):
    title: str
    content: str
    importance: int = Field(1, ge=1, le=5)

class TextSummaryData(BaseModel):
    overview: str
    sections: List[TextSummarySection]
    key_concepts: List[str]

class SessionSummaryResponse(BaseModel):
    format: str
    data: Dict[str, Any]  # Will contain either ConceptMapData or TextSummaryData
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    session_id: int

class QuizQuestion(BaseModel):
    id: str
    type: str = Field(..., description="Question type: 'multiple_choice', 'true_false', etc.")
    question: str
    options: List[str] = Field(..., description="Possible answers")
    correct_answer: str
    explanation: Optional[str] = None
    difficulty: int = Field(3, ge=1, le=5)
    concepts: List[str] = Field([], description="Related concepts tested by this question")

class GenerateQuizRequest(BaseModel):
    difficulty: int = Field(3, ge=1, le=5, description="Overall quiz difficulty")
    question_count: int = Field(5, ge=1, le=20, description="Number of questions to generate")
    focus_concepts: Optional[List[str]] = Field(None, description="Specific concepts to focus on")

class GenerateQuizResponse(BaseModel):
    session_id: int
    questions: List[QuizQuestion]
    total_questions: int
    difficulty: int
    concepts_covered: List[str]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class SaveQuizResultRequest(BaseModel):
    question_id: str
    user_answer: str
    time_taken_seconds: float
    was_correct: bool
    difficulty_feedback: Optional[int] = Field(None, ge=1, le=5)

class QuizResults(BaseModel):
    quiz_id: str
    session_id: int
    total_questions: int
    correct_answers: int
    average_time_per_question: float
    difficulty_rating: float
    concepts_mastered: List[str]
    concepts_need_review: List[str]
    recommendations: List[str]
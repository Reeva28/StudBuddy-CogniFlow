"""
Google Gemini client for AI services
"""
from typing import Dict, List, Any, Optional
import json
import google.generativeai as genai
from loguru import logger

from app.core.config import settings

class GeminiClient:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Use Gemini 2.5 Flash - stable version with 1M token context
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            logger.warning("GEMINI_API_KEY not configured")
            self.model = None
        
    def generate_summary(self, content: str) -> Dict[str, Any]:
        """Generate a comprehensive summary using Gemini"""
        if not self.model:
            return self._fallback_summary()
            
        try:
            prompt = f"""Analyze the following document and provide a structured summary.

Document:
{content[:4000]}  # Limit content length

Provide a JSON response with the following structure:
{{
    "summary": "A comprehensive 2-3 paragraph summary of the main content",
    "key_points": ["point 1", "point 2", "point 3", "point 4", "point 5"],
    "main_topics": ["topic 1", "topic 2", "topic 3"],
    "difficulty_level": "beginner/intermediate/advanced",
    "estimated_study_time_minutes": 30
}}

Return ONLY valid JSON, no additional text."""

            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Clean up markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            elif result_text.startswith("```"):
                result_text = result_text.replace("```", "").strip()
            
            return json.loads(result_text)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in summary: {str(e)}")
            # Return structured fallback
            return {
                "summary": response.text[:500] if 'response' in locals() else "Summary generation failed",
                "key_points": ["Key point extraction failed"],
                "main_topics": ["Topic extraction failed"],
                "difficulty_level": "intermediate",
                "estimated_study_time_minutes": 30
            }
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return self._fallback_summary()
            
    async def generate_study_plan(
        self,
        goal: str,
        subject: str,
        duration_minutes: int,
        difficulty: int = 3,
        prior_knowledge: Optional[str] = None,
        learning_style: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a personalized study plan using Gemini"""
        if not self.model:
            return self._fallback_study_plan(goal, subject, duration_minutes)
            
        try:
            prompt = self._create_study_plan_prompt(
                goal, subject, duration_minutes, 
                difficulty, prior_knowledge, learning_style
            )
            
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Clean up markdown code blocks
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            elif result_text.startswith("```"):
                result_text = result_text.replace("```", "").strip()
            
            return json.loads(result_text)
            
        except Exception as e:
            logger.error(f"Error generating study plan: {str(e)}")
            return self._fallback_study_plan(goal, subject, duration_minutes)
            
    def generate_practice_questions(
        self,
        content: str,
        difficulty: int = 3,
        question_count: int = 5,
        question_types: List[str] = ["multiple_choice", "short_answer"]
    ) -> List[Dict[str, Any]]:
        """Generate practice questions based on content"""
        if not self.model:
            return self._fallback_questions()
            
        try:
            prompt = f"""Based on the following content, generate {question_count} practice questions.

Content:
{content[:3000]}

Create questions with these types: {', '.join(question_types)}
Difficulty level: {difficulty}/5

Return a JSON array with this structure:
[
    {{
        "question": "The question text",
        "type": "multiple_choice",
        "options": ["A", "B", "C", "D"],
        "correct_answer": "B",
        "explanation": "Why this is correct"
    }}
]

Return ONLY valid JSON array, no additional text."""

            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Clean up markdown code blocks
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            elif result_text.startswith("```"):
                result_text = result_text.replace("```", "").strip()
            
            return json.loads(result_text)
            
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return self._fallback_questions()
    
    async def generate_text(self, prompt: str) -> str:
        """Generate text response from a prompt using Gemini"""
        if not self.model:
            logger.warning("Gemini model not available")
            return '{"flashcards": []}'
            
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return '{"flashcards": []}'
    
    def _create_study_plan_prompt(
        self,
        goal: str,
        subject: str,
        duration_minutes: int,
        difficulty: int,
        prior_knowledge: Optional[str],
        learning_style: Optional[str]
    ) -> str:
        """Create a detailed prompt for study plan generation"""
        prompt_parts = [
            f"Create a detailed study plan for learning {subject}.",
            f"Goal: {goal}",
            f"Total duration: {duration_minutes} minutes",
            f"Difficulty level: {difficulty}/5"
        ]
        
        if prior_knowledge:
            prompt_parts.append(f"Prior knowledge: {prior_knowledge}")
        if learning_style:
            prompt_parts.append(f"Learning style: {learning_style}")
            
        prompt_parts.extend([
            "\nProvide a JSON response with this structure:",
            "{",
            '    "overview": "Brief overview of the plan",',
            '    "sessions": [',
            '        {',
            '            "session_number": 1,',
            '            "title": "Session title",',
            '            "duration_minutes": 25,',
            '            "objectives": ["objective 1", "objective 2"],',
            '            "activities": ["activity 1", "activity 2"],',
            '            "break_after_minutes": 5',
            '        }',
            '    ],',
            '    "recommendations": ["tip 1", "tip 2", "tip 3"],',
            '    "resources": ["resource 1", "resource 2"]',
            "}",
            "\nReturn ONLY valid JSON, no additional text."
        ])
        
        return "\n".join(prompt_parts)
    
    def _fallback_summary(self) -> Dict[str, Any]:
        """Fallback summary when AI is unavailable"""
        return {
            "summary": "AI summary unavailable. Please review the document manually.",
            "key_points": ["AI processing unavailable"],
            "main_topics": ["Review document manually"],
            "difficulty_level": "intermediate",
            "estimated_study_time_minutes": 30
        }
    
    def _fallback_study_plan(self, goal: str, subject: str, duration: int) -> Dict[str, Any]:
        """Fallback study plan when AI is unavailable"""
        num_sessions = max(1, duration // 25)
        sessions = []
        for i in range(num_sessions):
            sessions.append({
                "session_number": i + 1,
                "title": f"Study Session {i + 1}",
                "duration_minutes": 25,
                "objectives": [f"Work on {subject}"],
                "activities": ["Review materials", "Practice problems"],
                "break_after_minutes": 5
            })
        
        return {
            "overview": f"Basic study plan for {goal}",
            "sessions": sessions,
            "recommendations": ["Take regular breaks", "Review before each session"],
            "resources": []
        }
    
    def _fallback_questions(self) -> List[Dict[str, Any]]:
        """Fallback questions when AI is unavailable"""
        return [
            {
                "question": "What are the main concepts covered in this material?",
                "type": "short_answer",
                "correct_answer": "Review the material to identify key concepts",
                "explanation": "AI question generation unavailable"
            }
        ]

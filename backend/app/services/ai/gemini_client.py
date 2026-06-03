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
            # Limit content to prevent token overflow
            content_preview = content[:8000] if len(content) > 8000 else content
            
            prompt = f"""Analyze the following document and provide a structured summary.

Document:
{content_preview}

You MUST respond with ONLY a valid JSON object in this exact format (no markdown, no extra text):
{{
    "summary": "A comprehensive 2-3 paragraph summary of the main content",
    "key_points": ["point 1", "point 2", "point 3", "point 4", "point 5"],
    "main_topics": ["topic 1", "topic 2", "topic 3"],
    "difficulty_level": "beginner",
    "estimated_study_time_minutes": 30
}}

Critical: Return ONLY the JSON object above with no code blocks, no markdown, no additional text."""

            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            elif result_text.startswith("```"):
                result_text = result_text.replace("```", "").strip()
            
            # Try to parse JSON
            try:
                parsed_data = json.loads(result_text)
                # Validate required fields
                if not isinstance(parsed_data.get("summary"), str):
                    parsed_data["summary"] = str(parsed_data.get("summary", ""))
                if not isinstance(parsed_data.get("key_points"), list):
                    parsed_data["key_points"] = ["Analysis in progress"]
                if not isinstance(parsed_data.get("main_topics"), list):
                    parsed_data["main_topics"] = ["General content"]
                return parsed_data
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error in summary: {str(e)}")
                logger.error(f"Response text: {result_text[:500]}")
                
                # Try to extract summary text even if JSON parsing fails
                summary_text = ""
                key_points_list = []
                
                # Clean up JSON artifacts from the response
                cleaned_text = result_text
                # Remove JSON opening/closing braces
                cleaned_text = cleaned_text.replace("```json", "").replace("```", "")
                cleaned_text = cleaned_text.replace("{", "").replace("}", "")
                
                # Try to extract summary field
                if '"summary"' in cleaned_text or "'summary'" in cleaned_text:
                    try:
                        # Find the summary value
                        patterns = [
                            ('"summary"\\s*:\\s*"([^"]*)"', 1),
                            ("'summary'\\s*:\\s*'([^']*)'", 1),
                            ('"summary"\\s*:\\s*"([^"]*)', 1),  # Handle incomplete quotes
                        ]
                        
                        import re
                        for pattern, group in patterns:
                            match = re.search(pattern, cleaned_text, re.DOTALL)
                            if match:
                                summary_text = match.group(group).strip()
                                # Clean up escape sequences
                                summary_text = summary_text.replace('\\n', '\n').replace('\\"', '"')
                                break
                        
                        # If still empty, just take text after "summary":
                        if not summary_text and ':' in cleaned_text:
                            parts = cleaned_text.split(':', 1)
                            if len(parts) > 1:
                                # Take everything after summary: until we hit another field or end
                                text_part = parts[1].strip()
                                # Stop at next field
                                for field in ['"key_points"', "'key_points'", '"main_topics"', '"difficulty_level"']:
                                    if field in text_part:
                                        text_part = text_part.split(field)[0]
                                summary_text = text_part.strip(' "\'\\n,')
                                
                    except Exception as extract_err:
                        logger.error(f"Error extracting summary: {str(extract_err)}")
                        pass
                
                # If we still don't have a summary, use the cleaned text
                if not summary_text:
                    summary_text = cleaned_text.strip()[:500]
                
                # Try to extract key points if present
                if '"key_points"' in result_text or "'key_points'" in result_text:
                    try:
                        import re
                        # Look for array pattern
                        match = re.search(r'"key_points"\s*:\s*\[(.*?)\]', result_text, re.DOTALL)
                        if match:
                            points_str = match.group(1)
                            # Extract quoted strings
                            key_points_list = re.findall(r'"([^"]+)"', points_str)
                    except:
                        pass
                
                if not key_points_list:
                    key_points_list = ["Key points could not be extracted from this document"]
                
                # Return with extracted or cleaned text
                return {
                    "summary": summary_text if summary_text else "Unable to generate summary",
                    "key_points": key_points_list,
                    "main_topics": ["Content analysis"],
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

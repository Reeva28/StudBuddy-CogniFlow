"""
Advanced document analysis using GPT-4
"""
from typing import Dict, List, Any, Optional
import json
from pathlib import Path
from loguru import logger

from app.core.config import settings
from app.services.ai.openai_client import OpenAIClient
from app.core.exceptions import AIProcessingError

class DocumentAnalyzer:
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client
        
    async def analyze_document(self, content: str) -> Dict[str, Any]:
        """
        Perform comprehensive document analysis using GPT-4
        """
        try:
            # Generate initial summary
            summary = await self._generate_summary(content)
            
            # Extract key concepts
            concepts = await self._extract_key_concepts(content)
            
            # Generate learning objectives
            objectives = await self._generate_learning_objectives(content)
            
            # Identify difficulty level
            difficulty = await self._assess_difficulty(content)
            
            # Generate study recommendations
            recommendations = await self._generate_recommendations(
                content, summary, concepts, difficulty
            )
            
            return {
                "summary": summary,
                "key_concepts": concepts,
                "learning_objectives": objectives,
                "difficulty_assessment": difficulty,
                "study_recommendations": recommendations,
                "metadata": {
                    "word_count": len(content.split()),
                    "estimated_read_time": len(content.split()) // 200  # Average reading speed
                }
            }
        except Exception as e:
            logger.error(f"Error in document analysis: {str(e)}")
            raise AIProcessingError(f"Failed to analyze document: {str(e)}")
    
    async def _generate_summary(self, content: str) -> Dict[str, Any]:
        """Generate a structured summary of the document"""
        prompt = self._create_summary_prompt(content)
        
        response = await self.openai_client.chat_completion(
            prompt,
            temperature=0.3,
            max_tokens=1000
        )
        
        try:
            # Parse the response into structured format
            summary_dict = json.loads(response)
            return {
                "brief": summary_dict["brief"],
                "detailed": summary_dict["detailed"],
                "main_points": summary_dict["main_points"],
                "context": summary_dict["context"]
            }
        except json.JSONDecodeError:
            # Fallback to simple format if JSON parsing fails
            return {
                "brief": response[:200],
                "detailed": response,
                "main_points": [],
                "context": ""
            }
    
    async def _extract_key_concepts(self, content: str) -> List[Dict[str, Any]]:
        """Extract and explain key concepts from the document"""
        prompt = (
            "Analyze the following text and identify the key concepts. "
            "For each concept, provide:\n"
            "1. The concept name\n"
            "2. A brief explanation\n"
            "3. Related concepts\n"
            "4. Importance level (1-5)\n"
            "Return as JSON array.\n\n"
            f"Text: {content[:2000]}..."  # Limit content length
        )
        
        response = await self.openai_client.chat_completion(
            prompt,
            temperature=0.3,
            max_tokens=1000
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return []
    
    async def _generate_learning_objectives(self, content: str) -> List[Dict[str, Any]]:
        """Generate specific learning objectives based on the content"""
        prompt = (
            "Based on the following content, generate SMART learning objectives. "
            "Each objective should be specific, measurable, achievable, relevant, and time-bound. "
            "Return as JSON array with 'objective' and 'assessment_criteria' for each.\n\n"
            f"Content: {content[:2000]}..."
        )
        
        response = await self.openai_client.chat_completion(
            prompt,
            temperature=0.4,
            max_tokens=800
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return []
    
    async def _assess_difficulty(self, content: str) -> Dict[str, Any]:
        """Assess the difficulty level of the content"""
        prompt = (
            "Analyze the following content and assess its difficulty level. Consider:\n"
            "1. Complexity of concepts\n"
            "2. Required prior knowledge\n"
            "3. Technical language usage\n"
            "4. Abstract thinking required\n"
            "Return as JSON with numerical ratings and explanations.\n\n"
            f"Content: {content[:2000]}..."
        )
        
        response = await self.openai_client.chat_completion(
            prompt,
            temperature=0.2,
            max_tokens=500
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "overall_difficulty": 3,
                "factors": {},
                "explanation": "Difficulty assessment failed"
            }
    
    async def _generate_recommendations(
        self,
        content: str,
        summary: Dict[str, Any],
        concepts: List[Dict[str, Any]],
        difficulty: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate personalized study recommendations"""
        context = {
            "summary": summary.get("brief", ""),
            "main_concepts": [c["name"] for c in concepts],
            "difficulty_level": difficulty.get("overall_difficulty", 3)
        }
        
        prompt = (
            f"Based on the following context: {json.dumps(context)}\n"
            "Generate comprehensive study recommendations including:\n"
            "1. Suggested study approach\n"
            "2. Resource recommendations\n"
            "3. Practice exercises\n"
            "4. Time management suggestions\n"
            "Return as JSON."
        )
        
        response = await self.openai_client.chat_completion(
            prompt,
            temperature=0.4,
            max_tokens=800
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "approach": [],
                "resources": [],
                "exercises": [],
                "time_management": []
            }
    
    def _create_summary_prompt(self, content: str) -> str:
        """Create a structured prompt for summary generation"""
        return (
            "Analyze the following text and provide a structured summary as JSON with:\n"
            "{\n"
            "  \"brief\": \"A one-paragraph overview\",\n"
            "  \"detailed\": \"A detailed summary\",\n"
            "  \"main_points\": [\"List of main points\"],\n"
            "  \"context\": \"Background context\"\n"
            "}\n\n"
            f"Text: {content[:3000]}..."  # Limit content length
        )
"""
AI-powered content recommendation system
"""
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta
from loguru import logger

from app.core.config import settings
from app.services.ai.openai_client import OpenAIClient
from app.core.exceptions import AIProcessingError

class ContentRecommender:
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client
        
    async def generate_recommendations(
        self,
        user_profile: Dict[str, Any],
        study_history: List[Dict[str, Any]],
        available_content: List[Dict[str, Any]],
        current_goals: List[str]
    ) -> Dict[str, Any]:
        """
        Generate personalized content recommendations
        """
        try:
            # Analyze user's learning patterns
            learning_patterns = await self._analyze_learning_patterns(
                user_profile,
                study_history
            )
            
            # Match content to user's needs
            content_matches = await self._match_content_to_user(
                learning_patterns,
                available_content,
                current_goals
            )
            
            # Generate personalized learning path
            learning_path = await self._generate_learning_path(
                content_matches,
                learning_patterns,
                current_goals
            )
            
            # Add supplementary resources
            supplementary = await self._suggest_supplementary_resources(
                learning_path,
                user_profile
            )
            
            return {
                "recommendations": content_matches,
                "learning_path": learning_path,
                "supplementary_resources": supplementary,
                "rationale": {
                    "learning_patterns": learning_patterns,
                    "matching_criteria": content_matches.get("criteria", {}),
                    "adaptations": learning_path.get("adaptations", {})
                }
            }
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise AIProcessingError(f"Failed to generate recommendations: {str(e)}")
    
    async def _analyze_learning_patterns(
        self,
        user_profile: Dict[str, Any],
        study_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze user's learning patterns and preferences"""
        context = {
            "profile": user_profile,
            "history": study_history
        }
        
        prompt = (
            "Analyze learning patterns including:\n"
            "1. Preferred learning styles\n"
            "2. Optimal study times\n"
            "3. Content engagement patterns\n"
            "4. Success factors\n"
            "Return as JSON.\n\n"
            f"Context: {json.dumps(context)}"
        )
        
        response = await self.openai_client.chat_completion(
            prompt,
            temperature=0.3,
            max_tokens=800
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}
    
    async def _match_content_to_user(
        self,
        learning_patterns: Dict[str, Any],
        available_content: List[Dict[str, Any]],
        goals: List[str]
    ) -> Dict[str, Any]:
        """Match available content to user's patterns and goals"""
        context = {
            "patterns": learning_patterns,
            "content": available_content,
            "goals": goals
        }
        
        prompt = (
            "Match content to user patterns and goals:\n"
            "1. Content relevance scoring\n"
            "2. Learning style alignment\n"
            "3. Difficulty appropriateness\n"
            "4. Goal alignment\n"
            "Return as JSON with scores and explanations.\n\n"
            f"Context: {json.dumps(context)}"
        )
        
        response = await self.openai_client.chat_completion(
            prompt,
            temperature=0.4,
            max_tokens=1000
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}
    
    async def _generate_learning_path(
        self,
        content_matches: Dict[str, Any],
        learning_patterns: Dict[str, Any],
        goals: List[str]
    ) -> Dict[str, Any]:
        """Generate a personalized learning path"""
        context = {
            "matches": content_matches,
            "patterns": learning_patterns,
            "goals": goals
        }
        
        prompt = (
            "Create a personalized learning path including:\n"
            "1. Content sequence\n"
            "2. Learning objectives\n"
            "3. Progress milestones\n"
            "4. Adaptation points\n"
            "Return as JSON.\n\n"
            f"Context: {json.dumps(context)}"
        )
        
        response = await self.openai_client.chat_completion(
            prompt,
            temperature=0.4,
            max_tokens=1000
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}
    
    async def _suggest_supplementary_resources(
        self,
        learning_path: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Suggest supplementary learning resources"""
        context = {
            "path": learning_path,
            "profile": user_profile
        }
        
        prompt = (
            "Suggest supplementary resources including:\n"
            "1. Practice materials\n"
            "2. Reference materials\n"
            "3. Interactive resources\n"
            "4. Assessment tools\n"
            "Return as JSON array.\n\n"
            f"Context: {json.dumps(context)}"
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
            
    async def update_recommendations(
        self,
        current_recommendations: Dict[str, Any],
        new_activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update recommendations based on new activity data
        """
        try:
            # Analyze new activity data
            activity_impact = await self._analyze_activity_impact(
                new_activity_data,
                current_recommendations
            )
            
            # Generate adjustments
            adjustments = await self._generate_recommendation_adjustments(
                current_recommendations,
                activity_impact
            )
            
            # Apply adjustments
            updated_recommendations = await self._apply_recommendation_adjustments(
                current_recommendations,
                adjustments
            )
            
            return updated_recommendations
        except Exception as e:
            logger.error(f"Error updating recommendations: {str(e)}")
            raise AIProcessingError(f"Failed to update recommendations: {str(e)}")
    
    async def _analyze_activity_impact(
        self,
        activity_data: Dict[str, Any],
        current_recommendations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze how new activity data impacts current recommendations"""
        context = {
            "activity": activity_data,
            "current": current_recommendations
        }
        
        prompt = (
            "Analyze activity impact on recommendations:\n"
            "1. Performance changes\n"
            "2. Engagement patterns\n"
            "3. Progress indicators\n"
            "4. Achievement alignment\n"
            "Return as JSON.\n\n"
            f"Context: {json.dumps(context)}"
        )
        
        response = await self.openai_client.chat_completion(
            prompt,
            temperature=0.3,
            max_tokens=800
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}
    
    async def _generate_recommendation_adjustments(
        self,
        current_recommendations: Dict[str, Any],
        impact_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate adjustments to recommendations based on impact analysis"""
        context = {
            "recommendations": current_recommendations,
            "impact": impact_analysis
        }
        
        prompt = (
            "Generate recommendation adjustments:\n"
            "1. Content updates\n"
            "2. Sequence changes\n"
            "3. Difficulty modifications\n"
            "4. Resource additions/removals\n"
            "Return as JSON.\n\n"
            f"Context: {json.dumps(context)}"
        )
        
        response = await self.openai_client.chat_completion(
            prompt,
            temperature=0.4,
            max_tokens=1000
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}
    
    async def _apply_recommendation_adjustments(
        self,
        current_recommendations: Dict[str, Any],
        adjustments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply adjustments to current recommendations"""
        # Create a deep copy of current recommendations
        updated = json.loads(json.dumps(current_recommendations))
        
        try:
            # Apply content updates
            if content_updates := adjustments.get("content_updates"):
                self._update_recommended_content(updated, content_updates)
            
            # Apply sequence changes
            if sequence_changes := adjustments.get("sequence_changes"):
                self._update_learning_path(updated, sequence_changes)
            
            # Apply difficulty modifications
            if difficulty_mods := adjustments.get("difficulty_modifications"):
                self._update_difficulty_levels(updated, difficulty_mods)
            
            # Update resources
            if resource_changes := adjustments.get("resource_changes"):
                self._update_resources(updated, resource_changes)
            
            return updated
        except Exception as e:
            logger.error(f"Error applying recommendation adjustments: {str(e)}")
            return current_recommendations
    
    def _update_recommended_content(
        self,
        recommendations: Dict[str, Any],
        updates: Dict[str, Any]
    ) -> None:
        """Update recommended content items"""
        if "recommendations" not in recommendations:
            return
            
        for item in recommendations["recommendations"]:
            item_id = item.get("id")
            if update := updates.get(str(item_id)):
                item.update(update)
    
    def _update_learning_path(
        self,
        recommendations: Dict[str, Any],
        changes: Dict[str, Any]
    ) -> None:
        """Update learning path sequence"""
        if "learning_path" not in recommendations:
            return
            
        if new_sequence := changes.get("sequence"):
            recommendations["learning_path"]["sequence"] = new_sequence
        
        if adjustments := changes.get("adjustments"):
            recommendations["learning_path"]["adjustments"] = adjustments
    
    def _update_difficulty_levels(
        self,
        recommendations: Dict[str, Any],
        modifications: Dict[str, Any]
    ) -> None:
        """Update difficulty levels of recommended content"""
        if "recommendations" not in recommendations:
            return
            
        for item in recommendations["recommendations"]:
            item_id = item.get("id")
            if mod := modifications.get(str(item_id)):
                item["difficulty"] = mod.get("new_difficulty", item.get("difficulty", 3))
                if "adaptations" in mod:
                    item["adaptations"] = mod["adaptations"]
    
    def _update_resources(
        self,
        recommendations: Dict[str, Any],
        changes: Dict[str, Any]
    ) -> None:
        """Update supplementary resources"""
        if "supplementary_resources" not in recommendations:
            recommendations["supplementary_resources"] = []
        
        # Remove resources
        if to_remove := changes.get("remove", []):
            recommendations["supplementary_resources"] = [
                r for r in recommendations["supplementary_resources"]
                if r.get("id") not in to_remove
            ]
        
        # Add new resources
        if to_add := changes.get("add", []):
            recommendations["supplementary_resources"].extend(to_add)
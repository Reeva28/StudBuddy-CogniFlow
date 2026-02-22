"""
AI-powered study session planner
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from loguru import logger

from app.core.config import settings
from app.services.ai.openai_client import OpenAIClient
from app.core.exceptions import AIProcessingError

class StudySessionPlanner:
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client
        
    async def create_study_plan(
        self,
        documents: List[Dict[str, Any]],
        user_preferences: Dict[str, Any],
        duration_days: int,
        goals: List[str]
    ) -> Dict[str, Any]:
        """
        Create a comprehensive study plan based on documents and user preferences
        """
        try:
            # Analyze documents and goals
            document_analysis = await self._analyze_study_materials(documents)
            
            # Generate initial plan
            initial_plan = await self._generate_initial_plan(
                document_analysis,
                user_preferences,
                duration_days,
                goals
            )
            
            # Optimize session scheduling
            optimized_sessions = await self._optimize_session_schedule(
                initial_plan,
                user_preferences
            )
            
            # Generate specific activities
            activities = await self._generate_session_activities(
                optimized_sessions,
                document_analysis
            )
            
            # Add assessment points
            assessments = await self._plan_assessments(activities, goals)
            
            return {
                "plan_id": str(datetime.now().timestamp()),
                "duration_days": duration_days,
                "goals": goals,
                "overview": initial_plan["overview"],
                "sessions": optimized_sessions,
                "activities": activities,
                "assessments": assessments,
                "recommendations": initial_plan["recommendations"]
            }
        except Exception as e:
            logger.error(f"Error creating study plan: {str(e)}")
            raise AIProcessingError(f"Failed to create study plan: {str(e)}")
    
    async def adapt_plan(
        self,
        current_plan: Dict[str, Any],
        progress_data: Dict[str, Any],
        performance_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Adapt the study plan based on progress and performance
        """
        try:
            # Analyze progress and performance
            analysis = await self._analyze_progress(
                current_plan,
                progress_data,
                performance_metrics
            )
            
            # Generate adjustments
            adjustments = await self._generate_plan_adjustments(
                current_plan,
                analysis
            )
            
            # Update plan
            updated_plan = await self._apply_adjustments(
                current_plan,
                adjustments
            )
            
            return updated_plan
        except Exception as e:
            logger.error(f"Error adapting study plan: {str(e)}")
            raise AIProcessingError(f"Failed to adapt study plan: {str(e)}")
    
    async def _analyze_study_materials(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze study materials to inform plan creation"""
        documents_context = [
            {
                "title": doc.get("title", "Untitled"),
                "summary": doc.get("summary", {}).get("brief", ""),
                "concepts": doc.get("key_concepts", []),
                "difficulty": doc.get("difficulty_assessment", {}).get("overall_difficulty", 3)
            }
            for doc in documents
        ]
        
        prompt = (
            "Analyze these study materials and provide:\n"
            "1. Suggested learning sequence\n"
            "2. Key prerequisites\n"
            "3. Estimated time requirements\n"
            "4. Potential challenges\n"
            "Return as JSON.\n\n"
            f"Materials: {json.dumps(documents_context)}"
        )
        
        response = await self.openai_client.chat_completion(
            prompt,
            temperature=0.3,
            max_tokens=1000
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}
    
    async def _generate_initial_plan(
        self,
        document_analysis: Dict[str, Any],
        user_preferences: Dict[str, Any],
        duration_days: int,
        goals: List[str]
    ) -> Dict[str, Any]:
        """Generate initial study plan structure"""
        context = {
            "analysis": document_analysis,
            "preferences": user_preferences,
            "duration_days": duration_days,
            "goals": goals
        }
        
        prompt = (
            "Create a structured study plan with:\n"
            "1. Daily/weekly schedule\n"
            "2. Learning milestones\n"
            "3. Review periods\n"
            "4. Practice sessions\n"
            "Return as JSON.\n\n"
            f"Context: {json.dumps(context)}"
        )
        
        response = await self.openai_client.chat_completion(
            prompt,
            temperature=0.4,
            max_tokens=1500
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {}
    
    async def _optimize_session_schedule(
        self,
        initial_plan: Dict[str, Any],
        user_preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Optimize study session scheduling"""
        context = {
            "plan": initial_plan,
            "preferences": user_preferences
        }
        
        prompt = (
            "Optimize this study schedule considering:\n"
            "1. User's preferred study times\n"
            "2. Optimal session duration\n"
            "3. Break intervals\n"
            "4. Topic spacing\n"
            "Return as JSON array of sessions.\n\n"
            f"Context: {json.dumps(context)}"
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
    
    async def _generate_session_activities(
        self,
        sessions: List[Dict[str, Any]],
        document_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate specific activities for each session"""
        context = {
            "sessions": sessions,
            "analysis": document_analysis
        }
        
        prompt = (
            "For each session, generate:\n"
            "1. Specific learning activities\n"
            "2. Practice exercises\n"
            "3. Review questions\n"
            "4. Application tasks\n"
            "Return as JSON array.\n\n"
            f"Context: {json.dumps(context)}"
        )
        
        response = await self.openai_client.chat_completion(
            prompt,
            temperature=0.4,
            max_tokens=1500
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return []
    
    async def _plan_assessments(
        self,
        activities: List[Dict[str, Any]],
        goals: List[str]
    ) -> List[Dict[str, Any]]:
        """Plan assessment points and progress checks"""
        context = {
            "activities": activities,
            "goals": goals
        }
        
        prompt = (
            "Create assessment plan including:\n"
            "1. Progress check points\n"
            "2. Knowledge assessments\n"
            "3. Practical evaluations\n"
            "4. Goal alignment checks\n"
            "Return as JSON array.\n\n"
            f"Context: {json.dumps(context)}"
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
    
    async def _analyze_progress(
        self,
        current_plan: Dict[str, Any],
        progress_data: Dict[str, Any],
        performance_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze study progress and performance"""
        context = {
            "plan": current_plan,
            "progress": progress_data,
            "performance": performance_metrics
        }
        
        prompt = (
            "Analyze study progress and performance:\n"
            "1. Goal achievement progress\n"
            "2. Learning rate analysis\n"
            "3. Difficulty assessment\n"
            "4. Time management analysis\n"
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
    
    async def _generate_plan_adjustments(
        self,
        current_plan: Dict[str, Any],
        progress_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate plan adjustments based on progress analysis"""
        context = {
            "plan": current_plan,
            "analysis": progress_analysis
        }
        
        prompt = (
            "Recommend plan adjustments based on progress:\n"
            "1. Schedule modifications\n"
            "2. Content adaptations\n"
            "3. Difficulty adjustments\n"
            "4. Additional resources/support\n"
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
    
    async def _apply_adjustments(
        self,
        current_plan: Dict[str, Any],
        adjustments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply recommended adjustments to the plan"""
        # Create a deep copy of the current plan
        updated_plan = json.loads(json.dumps(current_plan))
        
        try:
            # Apply schedule adjustments
            if schedule_mods := adjustments.get("schedule_modifications"):
                self._update_schedule(updated_plan, schedule_mods)
            
            # Apply content adaptations
            if content_adapt := adjustments.get("content_adaptations"):
                self._adapt_content(updated_plan, content_adapt)
            
            # Apply difficulty adjustments
            if diff_adjust := adjustments.get("difficulty_adjustments"):
                self._adjust_difficulty(updated_plan, diff_adjust)
            
            # Add new resources
            if new_resources := adjustments.get("additional_resources"):
                self._add_resources(updated_plan, new_resources)
            
            return updated_plan
        except Exception as e:
            logger.error(f"Error applying plan adjustments: {str(e)}")
            return current_plan  # Return original plan if adjustments fail
    
    def _update_schedule(self, plan: Dict[str, Any], modifications: Dict[str, Any]) -> None:
        """Update session schedule based on modifications"""
        if "sessions" not in plan:
            return
            
        for session in plan["sessions"]:
            session_id = session.get("id")
            if mod := modifications.get(str(session_id)):
                session.update(mod)
    
    def _adapt_content(self, plan: Dict[str, Any], adaptations: Dict[str, Any]) -> None:
        """Adapt session content based on progress"""
        if "activities" not in plan:
            return
            
        for activity in plan["activities"]:
            activity_id = activity.get("id")
            if adapt := adaptations.get(str(activity_id)):
                activity.update(adapt)
    
    def _adjust_difficulty(self, plan: Dict[str, Any], adjustments: Dict[str, Any]) -> None:
        """Adjust difficulty of activities and assessments"""
        for section in ["activities", "assessments"]:
            if section not in plan:
                continue
                
            for item in plan[section]:
                item_id = item.get("id")
                if adjust := adjustments.get(str(item_id)):
                    item["difficulty"] = adjust.get("new_difficulty", item.get("difficulty", 3))
                    if "adaptations" in adjust:
                        item["content"].update(adjust["adaptations"])
    
    def _add_resources(self, plan: Dict[str, Any], resources: List[Dict[str, Any]]) -> None:
        """Add new resources to the plan"""
        if "resources" not in plan:
            plan["resources"] = []
            
        plan["resources"].extend(resources)
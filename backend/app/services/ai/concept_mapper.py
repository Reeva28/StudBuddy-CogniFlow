"""
Service for generating concept maps and graphical summaries
"""
from typing import Dict, List, Any, Optional
import json
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
from loguru import logger

from app.core.config import settings
from app.services.ai.openai_client import OpenAIClient
from app.core.exceptions import AIProcessingError

class ConceptMapGenerator:
    def __init__(self, openai_client: OpenAIClient):
        self.openai_client = openai_client
        
    async def generate_session_summary(
        self,
        session_content: Dict[str, Any],
        user_notes: Optional[str] = None,
        output_format: str = "text"  # "text" or "concept_map"
    ) -> Dict[str, Any]:
        """
        Generate either a text summary or concept map for a study session
        """
        try:
            # Extract concepts and relationships
            concept_analysis = await self._analyze_concepts(session_content, user_notes)
            
            if output_format == "concept_map":
                # Generate graphical concept map
                concept_map = await self._create_concept_map(concept_analysis)
                return {
                    "format": "concept_map",
                    "data": concept_map,
                    "concepts": concept_analysis["concepts"],
                    "relationships": concept_analysis["relationships"]
                }
            else:
                # Generate text summary
                text_summary = await self._create_text_summary(concept_analysis)
                return {
                    "format": "text",
                    "summary": text_summary,
                    "key_concepts": concept_analysis["concepts"],
                    "relationships": concept_analysis["relationships"]
                }
                
        except Exception as e:
            logger.error(f"Error generating session summary: {str(e)}")
            raise AIProcessingError(f"Failed to generate summary: {str(e)}")

    async def _analyze_concepts(
        self,
        session_content: Dict[str, Any],
        user_notes: Optional[str]
    ) -> Dict[str, Any]:
        """Extract concepts and their relationships from session content"""
        context = {
            "content": session_content,
            "notes": user_notes
        }
        
        prompt = (
            "Analyze the study content and extract:\n"
            "1. Main concepts\n"
            "2. Relationships between concepts\n"
            "3. Hierarchical structure\n"
            "4. Cross-connections\n"
            "Return as JSON with concepts and relationships.\n\n"
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
            return {"concepts": [], "relationships": []}

    async def _create_concept_map(self, concept_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a visual concept map using networkx"""
        try:
            # Create graph
            G = nx.Graph()
            
            # Add nodes (concepts)
            for concept in concept_analysis["concepts"]:
                G.add_node(concept["name"], 
                          type=concept.get("type", "concept"),
                          importance=concept.get("importance", 1))
            
            # Add edges (relationships)
            for rel in concept_analysis["relationships"]:
                G.add_edge(rel["from"], rel["to"], 
                          type=rel.get("type", "related"),
                          description=rel.get("description", ""))
            
            # Create layout
            pos = nx.spring_layout(G)
            
            # Create figure
            plt.figure(figsize=(12, 8))
            plt.clf()
            
            # Draw nodes with different sizes based on importance
            node_sizes = [G.nodes[node].get("importance", 1) * 1000 for node in G.nodes()]
            nx.draw_networkx_nodes(G, pos, node_size=node_sizes, 
                                 node_color='lightblue', alpha=0.7)
            
            # Draw edges
            nx.draw_networkx_edges(G, pos, alpha=0.5)
            
            # Add labels
            nx.draw_networkx_labels(G, pos)
            
            # Save plot to bytes
            img_bytes = io.BytesIO()
            plt.savefig(img_bytes, format='png', bbox_inches='tight')
            img_bytes.seek(0)
            
            # Convert to base64
            img_base64 = base64.b64encode(img_bytes.read()).decode()
            
            plt.close()
            
            return {
                "image": img_base64,
                "format": "png",
                "graph_data": {
                    "nodes": list(G.nodes(data=True)),
                    "edges": list(G.edges(data=True))
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating concept map: {str(e)}")
            raise AIProcessingError(f"Failed to create concept map: {str(e)}")

    async def _create_text_summary(self, concept_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a structured text summary from concept analysis"""
        context = {
            "analysis": concept_analysis
        }
        
        prompt = (
            "Create a structured text summary including:\n"
            "1. Overview of main concepts\n"
            "2. Key relationships and dependencies\n"
            "3. Important principles\n"
            "4. Practical applications\n"
            "Return as JSON with sections.\n\n"
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
            return {
                "overview": "Summary generation failed",
                "sections": []
            }

    async def generate_quiz_from_concepts(
        self,
        concept_analysis: Dict[str, Any],
        difficulty: int = 3,
        question_count: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate quiz questions based on concept analysis"""
        context = {
            "concepts": concept_analysis["concepts"],
            "relationships": concept_analysis["relationships"],
            "settings": {
                "difficulty": difficulty,
                "question_count": question_count
            }
        }
        
        prompt = (
            "Generate quiz questions that test understanding of concepts and relationships.\n"
            "Include different question types:\n"
            "1. Multiple choice\n"
            "2. True/False\n"
            "3. Relationship identification\n"
            "4. Concept application\n"
            "Return as JSON array with questions, options, and correct answers.\n\n"
            f"Context: {json.dumps(context)}"
        )
        
        response = await self.openai_client.chat_completion(
            prompt,
            temperature=0.4,
            max_tokens=1500
        )
        
        try:
            questions = json.loads(response)
            return [
                {
                    **question,
                    "id": f"q{i+1}",
                    "difficulty": difficulty
                }
                for i, question in enumerate(questions)
            ]
        except json.JSONDecodeError:
            return []
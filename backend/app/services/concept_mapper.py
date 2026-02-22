"""
Concept mapping service for extracting and managing knowledge graphs
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import json

from app.db import models
from app.schemas import concept as schemas
from app.services.ai.gemini_client import GeminiClient


class ConceptMapper:
    """Extract and map concepts from documents using AI"""
    
    def __init__(self):
        self.gemini_client = GeminiClient()
    
    async def extract_concepts(
        self, 
        document_content: str,
        max_concepts: int = 20
    ) -> Dict[str, Any]:
        """Extract concepts and relationships from document content"""
        
        prompt = f"""Analyze the following document and extract key concepts and their relationships.

Document content:
{document_content[:6000]}

Extract the most important concepts (max {max_concepts}) and identify how they relate to each other.

For each concept, provide:
- name: Short, clear concept name (2-5 words)
- description: Brief explanation (1-2 sentences)
- importance: Score from 0.0 to 1.0 indicating centrality to the document
- type: One of "concept", "definition", "example", or "principle"

For relationships, identify:
- source: Index of source concept (0-based)
- target: Index of target concept (0-based)
- type: One of "relates_to", "depends_on", "is_example_of", or "contradicts"
- strength: Score from 0.0 to 1.0 indicating relationship strength

Return ONLY valid JSON in this exact format:
{{
  "concepts": [
    {{
      "name": "Concept Name",
      "description": "Brief description",
      "importance": 0.9,
      "type": "concept"
    }}
  ],
  "relationships": [
    {{
      "source": 0,
      "target": 1,
      "type": "depends_on",
      "strength": 0.8
    }}
  ]
}}"""

        response = await self.gemini_client.generate_text(prompt)
        
        # Parse the response
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            data = json.loads(json_str)
            
            # Validate structure
            if "concepts" not in data:
                data["concepts"] = []
            if "relationships" not in data:
                data["relationships"] = []
            
            # Limit concepts to max_concepts
            data["concepts"] = data["concepts"][:max_concepts]
            
            return data
            
        except json.JSONDecodeError:
            # Return empty graph on parse error
            return {"concepts": [], "relationships": []}


async def generate_concept_map(
    db: Session, 
    document_id: int, 
    max_concepts: int = 20,
    regenerate: bool = False
) -> schemas.ConceptGraph:
    """Generate or retrieve concept map for a document"""
    
    # Check if concepts already exist
    existing_count = db.query(func.count(models.ConceptNode.id))\
        .filter(models.ConceptNode.document_id == document_id)\
        .scalar()
    
    if existing_count > 0 and not regenerate:
        # Return existing map
        return get_concept_graph(db, document_id)
    
    # Get document
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not document or not document.content:
        return schemas.ConceptGraph(
            document_id=document_id,
            nodes=[],
            edges=[],
            total_concepts=0
        )
    
    # Delete existing concepts if regenerating
    if regenerate:
        db.query(models.ConceptRelationship)\
            .filter(models.ConceptRelationship.source_id.in_(
                db.query(models.ConceptNode.id).filter(models.ConceptNode.document_id == document_id)
            ))\
            .delete(synchronize_session=False)
        db.query(models.ConceptNode)\
            .filter(models.ConceptNode.document_id == document_id)\
            .delete()
        db.commit()
    
    # Extract concepts using AI
    mapper = ConceptMapper()
    extracted = await mapper.extract_concepts(document.content, max_concepts)
    
    # Create concept nodes
    concept_nodes = []
    for concept_data in extracted.get("concepts", []):
        node = models.ConceptNode(
            document_id=document_id,
            name=concept_data.get("name", "Unknown"),
            description=concept_data.get("description"),
            importance=float(concept_data.get("importance", 0.5)),
            type=concept_data.get("type", "concept")
        )
        db.add(node)
        concept_nodes.append(node)
    
    db.commit()
    
    # Refresh to get IDs
    for node in concept_nodes:
        db.refresh(node)
    
    # Create relationships
    for rel_data in extracted.get("relationships", []):
        source_idx = rel_data.get("source", 0)
        target_idx = rel_data.get("target", 0)
        
        # Validate indices
        if 0 <= source_idx < len(concept_nodes) and 0 <= target_idx < len(concept_nodes):
            relationship = models.ConceptRelationship(
                source_id=concept_nodes[source_idx].id,
                target_id=concept_nodes[target_idx].id,
                relationship_type=rel_data.get("type", "relates_to"),
                strength=float(rel_data.get("strength", 0.5))
            )
            db.add(relationship)
    
    db.commit()
    
    # Return the completed graph
    return get_concept_graph(db, document_id)


def get_concept_graph(db: Session, document_id: int) -> schemas.ConceptGraph:
    """Get existing concept graph for a document"""
    
    # Get all concepts for document
    concepts = db.query(models.ConceptNode)\
        .filter(models.ConceptNode.document_id == document_id)\
        .all()
    
    if not concepts:
        return schemas.ConceptGraph(
            document_id=document_id,
            nodes=[],
            edges=[],
            total_concepts=0
        )
    
    concept_ids = [c.id for c in concepts]
    
    # Get all relationships
    relationships = db.query(models.ConceptRelationship)\
        .filter(models.ConceptRelationship.source_id.in_(concept_ids))\
        .all()
    
    # Count connections per concept
    connection_counts = {}
    for rel in relationships:
        connection_counts[rel.source_id] = connection_counts.get(rel.source_id, 0) + 1
        connection_counts[rel.target_id] = connection_counts.get(rel.target_id, 0) + 1
    
    # Build graph nodes
    nodes = []
    for concept in concepts:
        nodes.append(schemas.ConceptGraphNode(
            id=concept.id,
            name=concept.name,
            description=concept.description,
            importance=concept.importance,
            type=concept.type,
            connections=connection_counts.get(concept.id, 0)
        ))
    
    # Build graph edges
    edges = []
    for rel in relationships:
        edges.append(schemas.ConceptGraphEdge(
            source=rel.source_id,
            target=rel.target_id,
            type=rel.relationship_type,
            strength=rel.strength
        ))
    
    return schemas.ConceptGraph(
        document_id=document_id,
        nodes=nodes,
        edges=edges,
        total_concepts=len(nodes)
    )


def delete_concept_map(db: Session, document_id: int) -> bool:
    """Delete all concepts for a document"""
    
    # Delete relationships first (foreign key constraint)
    db.query(models.ConceptRelationship)\
        .filter(models.ConceptRelationship.source_id.in_(
            db.query(models.ConceptNode.id).filter(models.ConceptNode.document_id == document_id)
        ))\
        .delete(synchronize_session=False)
    
    # Delete concepts
    deleted = db.query(models.ConceptNode)\
        .filter(models.ConceptNode.document_id == document_id)\
        .delete()
    
    db.commit()
    return deleted > 0

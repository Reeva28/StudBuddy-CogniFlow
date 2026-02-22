"""
Concept mapping schemas
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ConceptNodeBase(BaseModel):
    """Base concept node schema"""
    name: str = Field(..., description="Concept name")
    description: Optional[str] = Field(None, description="Concept description")
    importance: float = Field(1.0, ge=0.0, le=1.0, description="Importance score 0.0-1.0")
    type: str = Field("concept", description="concept, definition, example, principle")


class ConceptNodeCreate(ConceptNodeBase):
    """Schema for creating a concept node"""
    document_id: int


class ConceptNode(ConceptNodeBase):
    """Schema for concept node"""
    id: int
    document_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConceptRelationshipBase(BaseModel):
    """Base relationship schema"""
    relationship_type: str = Field("relates_to", description="relates_to, depends_on, is_example_of, contradicts")
    strength: float = Field(1.0, ge=0.0, le=1.0, description="Relationship strength 0.0-1.0")


class ConceptRelationshipCreate(ConceptRelationshipBase):
    """Schema for creating a relationship"""
    source_id: int
    target_id: int


class ConceptRelationship(ConceptRelationshipBase):
    """Schema for relationship"""
    id: int
    source_id: int
    target_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConceptGraphNode(BaseModel):
    """Node for graph visualization"""
    id: int
    name: str
    description: Optional[str]
    importance: float
    type: str
    connections: int = Field(0, description="Number of connections")


class ConceptGraphEdge(BaseModel):
    """Edge for graph visualization"""
    source: int
    target: int
    type: str
    strength: float


class ConceptGraph(BaseModel):
    """Full concept graph for a document"""
    document_id: int
    nodes: List[ConceptGraphNode]
    edges: List[ConceptGraphEdge]
    total_concepts: int
    
    
class ConceptExtractionRequest(BaseModel):
    """Request to extract concepts from a document"""
    max_concepts: int = Field(20, ge=5, le=100, description="Maximum number of concepts to extract")
    include_relationships: bool = Field(True, description="Whether to extract relationships")

'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { conceptMapAPI, documentsAPI } from '@/lib/api';

interface ConceptNode {
  id: number;
  name: string;
  description: string | null;
  importance: number;
  type: string;
  connections: number;
}

interface ConceptEdge {
  source: number;
  target: number;
  type: string;
  strength: number;
}

interface ConceptGraph {
  document_id: number;
  nodes: ConceptNode[];
  edges: ConceptEdge[];
  total_concepts: number;
}

interface Document {
  id: number;
  filename: string;
}

export default function ConceptMapPage() {
  const router = useRouter();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState<number | null>(null);
  const [conceptGraph, setConceptGraph] = useState<ConceptGraph | null>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selectedNode, setSelectedNode] = useState<ConceptNode | null>(null);
  const [hoveredNode, setHoveredNode] = useState<ConceptNode | null>(null);
  const [zoom, setZoom] = useState(1);
  const [panX, setPanX] = useState(0);
  const [panY, setPanY] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  useEffect(() => {
    loadDocuments();
  }, []);

  useEffect(() => {
    if (conceptGraph) {
      drawGraph();
    }
  }, [conceptGraph, hoveredNode, zoom, panX, panY]);

  const loadDocuments = async () => {
    try {
      const docs = await documentsAPI.list();
      setDocuments(docs);
      if (docs.length > 0 && !selectedDocumentId) {
        setSelectedDocumentId(docs[0].id);
        loadConceptMap(docs[0].id);
      }
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  const loadConceptMap = async (documentId: number) => {
    setLoading(true);
    try {
      const graph = await conceptMapAPI.get(documentId);
      setConceptGraph(graph);
    } catch (error) {
      console.error('Failed to load concept map:', error);
      setConceptGraph(null);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateMap = async () => {
    if (!selectedDocumentId) return;
    
    setGenerating(true);
    try {
      const graph = await conceptMapAPI.generate(selectedDocumentId, 20, true);
      setConceptGraph(graph);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to generate concept map');
    } finally {
      setGenerating(false);
    }
  };

  const handleDocumentChange = (documentId: number) => {
    setSelectedDocumentId(documentId);
    setSelectedNode(null);
    setZoom(1);
    setPanX(0);
    setPanY(0);
    loadConceptMap(documentId);
  };

  const handleZoomIn = () => setZoom(Math.min(zoom * 1.2, 3));
  const handleZoomOut = () => setZoom(Math.max(zoom / 1.2, 0.3));
  const handleResetView = () => {
    setZoom(1);
    setPanX(0);
    setPanY(0);
  };

  const handleWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.95 : 1.05;
    setZoom(Math.max(0.3, Math.min(3, zoom * delta)));
  };

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - panX, y: e.clientY - panY });
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (isDragging) {
      setPanX(e.clientX - dragStart.x);
      setPanY(e.clientY - dragStart.y);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const drawGraph = () => {
    const canvas = canvasRef.current;
    if (!canvas || !conceptGraph) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    if (conceptGraph.nodes.length === 0) return;

    // Simple force-directed layout simulation
    const nodePositions = new Map<number, { x: number; y: number; vx: number; vy: number }>();
    
    // Initialize random positions
    conceptGraph.nodes.forEach(node => {
      nodePositions.set(node.id, {
        x: width / 2 + (Math.random() - 0.5) * width * 0.6,
        y: height / 2 + (Math.random() - 0.5) * height * 0.6,
        vx: 0,
        vy: 0,
      });
    });

    // Run simple physics simulation with better spacing
    const iterations = 100;
    const repulsionStrength = 2000; // Increased for better spacing
    const attractionStrength = 0.005;
    
    for (let iter = 0; iter < iterations; iter++) {
      // Repulsion between nodes
      conceptGraph.nodes.forEach((nodeA, i) => {
        conceptGraph.nodes.forEach((nodeB, j) => {
          if (i >= j) return;
          
          const posA = nodePositions.get(nodeA.id)!;
          const posB = nodePositions.get(nodeB.id)!;
          
          const dx = posB.x - posA.x;
          const dy = posB.y - posA.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          
          const force = repulsionStrength / (dist * dist);
          posA.vx -= (dx / dist) * force;
          posA.vy -= (dy / dist) * force;
          posB.vx += (dx / dist) * force;
          posB.vy += (dy / dist) * force;
        });
      });

      // Attraction along edges
      conceptGraph.edges.forEach(edge => {
        const posA = nodePositions.get(edge.source);
        const posB = nodePositions.get(edge.target);
        if (!posA || !posB) return;

        const dx = posB.x - posA.x;
        const dy = posB.y - posA.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        
        const force = dist * attractionStrength * edge.strength;
        posA.vx += (dx / dist) * force;
        posA.vy += (dy / dist) * force;
        posB.vx -= (dx / dist) * force;
        posB.vy -= (dy / dist) * force;
      });

      // Apply velocity with damping
      nodePositions.forEach(pos => {
        pos.x += pos.vx;
        pos.y += pos.vy;
        pos.vx *= 0.8;
        pos.vy *= 0.8;

        // Keep within bounds
        pos.x = Math.max(50, Math.min(width - 50, pos.x));
        pos.y = Math.max(50, Math.min(height - 50, pos.y));
      });
    }

    // Apply zoom and pan transformation
    ctx.save();
    ctx.translate(width / 2 + panX, height / 2 + panY);
    ctx.scale(zoom, zoom);
    ctx.translate(-width / 2, -height / 2);

    // Draw edges
    ctx.strokeStyle = '#d1d5db';
    ctx.lineWidth = 1 / zoom;
    conceptGraph.edges.forEach(edge => {
      const posA = nodePositions.get(edge.source);
      const posB = nodePositions.get(edge.target);
      if (!posA || !posB) return;

      ctx.globalAlpha = edge.strength * 0.6;
      ctx.beginPath();
      ctx.moveTo(posA.x, posA.y);
      ctx.lineTo(posB.x, posB.y);
      ctx.stroke();
    });
    ctx.globalAlpha = 1;

    // Draw nodes
    conceptGraph.nodes.forEach(node => {
      const pos = nodePositions.get(node.id);
      if (!pos) return;

      const radius = 8 + node.importance * 12;
      const isHovered = hoveredNode?.id === node.id;
      const isSelected = selectedNode?.id === node.id;

      // Node circle
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, radius, 0, 2 * Math.PI);
      
      // Color by type
      const colors: Record<string, string> = {
        concept: '#3b82f6',
        definition: '#10b981',
        example: '#f59e0b',
        principle: '#8b5cf6',
      };
      ctx.fillStyle = colors[node.type] || '#6b7280';
      ctx.fill();

      // Highlight if selected or hovered
      if (isSelected || isHovered) {
        ctx.strokeStyle = isSelected ? '#1e40af' : '#60a5fa';
        ctx.lineWidth = 3;
        ctx.stroke();
      }

      // Draw label
      ctx.fillStyle = '#1f2937';
      ctx.font = `${isHovered || isSelected ? 'bold ' : ''}${12 / zoom}px sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(node.name, pos.x, pos.y - radius - 10);
    });

    ctx.restore();
  };

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!conceptGraph || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Simple click detection (recalculate positions)
    // In production, store positions in state
    setSelectedNode(null);
  };

  const getTypeIcon = (type: string) => {
    const icons: Record<string, string> = {
      concept: '💡',
      definition: '📖',
      example: '🎯',
      principle: '⚡',
    };
    return icons[type] || '•';
  };

  const getRelationshipLabel = (type: string) => {
    const labels: Record<string, string> = {
      relates_to: 'relates to',
      depends_on: 'depends on',
      is_example_of: 'is example of',
      contradicts: 'contradicts',
    };
    return labels[type] || type;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/dashboard')}
            className="text-indigo-600 hover:text-indigo-700 mb-4 flex items-center gap-2"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Concept Mapping</h1>
          <p className="text-gray-600">Visualize how concepts connect in your documents</p>
        </div>

        {/* Document Selector */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex-1 min-w-[200px]">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Document
              </label>
              <select
                value={selectedDocumentId || ''}
                onChange={(e) => handleDocumentChange(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                disabled={loading || generating}
              >
                <option value="">Select a document...</option>
                {documents.map(doc => (
                  <option key={doc.id} value={doc.id}>{doc.filename}</option>
                ))}
              </select>
            </div>

            <button
              onClick={handleGenerateMap}
              disabled={!selectedDocumentId || generating}
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition mt-6"
            >
              {generating ? 'Generating...' : 'Generate Map'}
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            <p className="mt-4 text-gray-600">Loading concept map...</p>
          </div>
        ) : conceptGraph && conceptGraph.nodes.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Graph Visualization */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Concept Network
                  <span className="text-sm text-gray-500 ml-2 font-normal">
                    ({conceptGraph.total_concepts} concepts, {conceptGraph.edges.length} connections)
                  </span>
                </h2>
                <div className="relative">
                  <canvas
                    ref={canvasRef}
                    width={800}
                    height={600}
                    onClick={handleCanvasClick}
                    onWheel={handleWheel}
                    onMouseDown={handleMouseDown}
                    onMouseMove={handleMouseMove}
                    onMouseUp={handleMouseUp}
                    onMouseLeave={handleMouseUp}
                    className="w-full h-auto border border-gray-200 rounded-lg cursor-move bg-gray-50"
                  />
                  <div className="absolute top-4 right-4 flex flex-col gap-2 bg-white rounded-lg shadow-lg p-2">
                    <button
                      onClick={handleZoomIn}
                      className="p-2 hover:bg-gray-100 rounded transition"
                      title="Zoom In"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
                      </svg>
                    </button>
                    <button
                      onClick={handleZoomOut}
                      className="p-2 hover:bg-gray-100 rounded transition"
                      title="Zoom Out"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
                      </svg>
                    </button>
                    <button
                      onClick={handleResetView}
                      className="p-2 hover:bg-gray-100 rounded transition"
                      title="Reset View"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    </button>
                    <div className="text-xs text-center text-gray-500 pt-1 border-t">
                      {Math.round(zoom * 100)}%
                    </div>
                  </div>
                </div>
                
                {/* Legend */}
                <div className="mt-4 flex gap-6 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-blue-500"></div>
                    <span>Concept</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-green-500"></div>
                    <span>Definition</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-amber-500"></div>
                    <span>Example</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded-full bg-purple-500"></div>
                    <span>Principle</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Concept List */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Concepts</h2>
                <div className="space-y-3 max-h-[600px] overflow-y-auto">
                  {conceptGraph.nodes
                    .sort((a, b) => b.importance - a.importance)
                    .map(node => (
                      <div
                        key={node.id}
                        onClick={() => setSelectedNode(node)}
                        onMouseEnter={() => setHoveredNode(node)}
                        onMouseLeave={() => setHoveredNode(null)}
                        className={`p-3 rounded-lg border cursor-pointer transition ${
                          selectedNode?.id === node.id
                            ? 'border-indigo-500 bg-indigo-50'
                            : 'border-gray-200 hover:border-indigo-300 hover:bg-gray-50'
                        }`}
                      >
                        <div className="flex items-start justify-between mb-1">
                          <div className="flex items-center gap-2">
                            <span>{getTypeIcon(node.type)}</span>
                            <span className="font-medium text-gray-900">{node.name}</span>
                          </div>
                          <span className="text-xs text-gray-500">{node.connections} edges</span>
                        </div>
                        {node.description && (
                          <p className="text-sm text-gray-600 mt-2">{node.description}</p>
                        )}
                        <div className="mt-2 flex items-center gap-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                            <div
                              className="bg-indigo-600 h-1.5 rounded-full"
                              style={{ width: `${node.importance * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-xs text-gray-500">{(node.importance * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <div className="text-6xl mb-4">🗺️</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Concept Map Yet</h3>
            <p className="text-gray-600 mb-6">
              Select a document and click "Generate Map" to visualize concepts and their relationships
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

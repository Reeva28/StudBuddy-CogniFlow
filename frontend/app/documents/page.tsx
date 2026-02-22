'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/app/contexts/AuthContext';
import { documentsAPI, flashcardsAPI, conceptMapAPI } from '@/lib/api';

interface Document {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  created_at: string;
}

interface DocumentSummary {
  summary: string;
  key_points: string[];
}

export default function DocumentsPage() {
  const router = useRouter();
  const { isAuthenticated, loading: authLoading, user, logout } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<number | null>(null);
  const [summary, setSummary] = useState<DocumentSummary | null>(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [generatingFlashcards, setGeneratingFlashcards] = useState(false);
  const [generatingConceptMap, setGeneratingConceptMap] = useState(false);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    } else if (isAuthenticated) {
      loadDocuments();
    }
  }, [isAuthenticated, authLoading, router]);

  const loadDocuments = async () => {
    try {
      const data = await documentsAPI.list();
      setDocuments(data);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      await documentsAPI.upload(file);
      await loadDocuments();
      e.target.value = '';
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  const handleViewSummary = async (docId: number) => {
    setSelectedDoc(docId);
    setLoadingSummary(true);
    setSummary(null);
    
    try {
      const data = await documentsAPI.getSummary(docId);
      setSummary(data);
    } catch (error) {
      console.error('Failed to load summary:', error);
      alert('Failed to load document summary');
    } finally {
      setLoadingSummary(false);
    }
  };

  const handleDelete = async (docId: number) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      await documentsAPI.delete(docId);
      await loadDocuments();
      if (selectedDoc === docId) {
        setSelectedDoc(null);
        setSummary(null);
      }
    } catch (error) {
      alert('Failed to delete document');
    }
  };

  const handleGenerateFlashcards = async (docId: number) => {
    setGeneratingFlashcards(true);
    try {
      const flashcards = await flashcardsAPI.generate(docId, 10);
      alert(`Successfully generated ${flashcards.length} flashcards!`);
      router.push('/flashcards');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to generate flashcards');
    } finally {
      setGeneratingFlashcards(false);
    }
  };

  const handleGenerateConceptMap = async (docId: number) => {
    setGeneratingConceptMap(true);
    try {
      const conceptGraph = await conceptMapAPI.generate(docId, 20);
      alert(`Successfully generated concept map with ${conceptGraph.total_concepts} concepts!`);
      router.push('/concept-map');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to generate concept map');
    } finally {
      setGeneratingConceptMap(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <img src="/logo.png" alt="CogniFlow" className="h-20 w-auto" />
              <button
                onClick={() => router.push('/dashboard')}
                className="text-indigo-600 hover:text-indigo-800"
              >
                ← Back
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
                <p className="text-sm text-gray-600">Manage your study materials</p>
              </div>
            </div>
            <button
              onClick={logout}
              className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Documents List */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                Your Documents ({documents.length})
              </h2>
              <label className="cursor-pointer">
                <input
                  type="file"
                  accept=".pdf,.txt,.doc,.docx"
                  onChange={handleFileUpload}
                  className="hidden"
                  disabled={uploading}
                />
                <span className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition inline-block">
                  {uploading ? 'Uploading...' : '+ Upload'}
                </span>
              </label>
            </div>

            {documents.length === 0 ? (
              <div className="text-center py-12">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <p className="mt-4 text-gray-600">No documents yet</p>
                <p className="text-sm text-gray-500 mt-1">Upload your first document to get started</p>
              </div>
            ) : (
              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className={`p-4 border rounded-lg transition cursor-pointer ${
                      selectedDoc === doc.id
                        ? 'border-indigo-500 bg-indigo-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handleViewSummary(doc.id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-gray-900 truncate">{doc.filename}</h3>
                        <div className="flex items-center gap-3 mt-1 text-sm text-gray-600">
                          <span className="uppercase">{doc.file_type}</span>
                          <span>•</span>
                          <span>{formatFileSize(doc.file_size)}</span>
                          <span>•</span>
                          <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(doc.id);
                        }}
                        className="ml-2 p-2 text-red-600 hover:bg-red-50 rounded transition"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                          />
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Summary Panel */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">AI Summary</h2>

            {!selectedDoc ? (
              <div className="text-center py-12 text-gray-500">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <p className="mt-4">Select a document to view its AI-generated summary</p>
              </div>
            ) : loadingSummary ? (
              <div className="flex justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
              </div>
            ) : summary ? (
              <div className="space-y-6">
                <div className="flex gap-2 mb-4">
                  <button
                    onClick={() => selectedDoc && handleGenerateFlashcards(selectedDoc)}
                    disabled={generatingFlashcards}
                    className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-2 rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {generatingFlashcards ? 'Generating...' : '🎯 Generate Flashcards'}
                  </button>
                  <button
                    onClick={() => selectedDoc && handleGenerateConceptMap(selectedDoc)}
                    disabled={generatingConceptMap}
                    className="flex-1 bg-gradient-to-r from-teal-600 to-cyan-600 text-white px-4 py-2 rounded-lg font-medium hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {generatingConceptMap ? 'Generating...' : '🗺️ Generate Concept Map'}
                  </button>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Summary</h3>
                  <p className="text-gray-700 leading-relaxed">{summary.summary}</p>
                </div>

                {summary.key_points && summary.key_points.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Key Points</h3>
                    <ul className="space-y-2">
                      {summary.key_points.map((point, index) => (
                        <li key={index} className="flex items-start">
                          <span className="inline-block w-6 h-6 bg-indigo-100 text-indigo-600 rounded-full flex-shrink-0 flex items-center justify-center text-sm font-medium mr-3 mt-0.5">
                            {index + 1}
                          </span>
                          <span className="text-gray-700">{point}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12 text-red-600">
                Failed to load summary. Please try again.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

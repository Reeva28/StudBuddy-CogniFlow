'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';
import { flashcardsAPI, documentsAPI } from '@/lib/api';

interface Flashcard {
  id: number;
  document_id: number;
  question: string;
  answer: string;
  difficulty: number;
  created_at: string;
  last_reviewed: string | null;
  next_review: string | null;
}

interface Document {
  id: number;
  filename: string;
}

export default function FlashcardsPage() {
  const router = useRouter();
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState<'browse' | 'study'>('browse');
  const [selectedDocument, setSelectedDocument] = useState<number | null>(null);
  
  // Study mode state
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [studyCards, setStudyCards] = useState<Flashcard[]>([]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, authLoading, router]);

  useEffect(() => {
    if (isAuthenticated) {
      loadData();
    }
  }, [isAuthenticated, selectedDocument]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [cardsData, docsData] = await Promise.all([
        selectedDocument 
          ? flashcardsAPI.getByDocument(selectedDocument)
          : flashcardsAPI.getAll(),
        documentsAPI.list()
      ]);
      setFlashcards(cardsData);
      setDocuments(docsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const startStudySession = async () => {
    try {
      const dueCards = await flashcardsAPI.getDue(20);
      if (dueCards.length === 0) {
        alert('No cards due for review! Great job staying on top of your studies.');
        return;
      }
      setStudyCards(dueCards);
      setCurrentCardIndex(0);
      setShowAnswer(false);
      setMode('study');
    } catch (error) {
      console.error('Failed to start study session:', error);
    }
  };

  const handleReview = async (quality: number) => {
    if (currentCardIndex >= studyCards.length) return;

    const card = studyCards[currentCardIndex];
    try {
      await flashcardsAPI.review(card.id, quality);
      
      // Move to next card
      if (currentCardIndex < studyCards.length - 1) {
        setCurrentCardIndex(currentCardIndex + 1);
        setShowAnswer(false);
      } else {
        // Study session complete
        alert(`Study session complete! Reviewed ${studyCards.length} cards.`);
        setMode('browse');
        loadData();
      }
    } catch (error) {
      console.error('Failed to record review:', error);
    }
  };

  const deleteCard = async (cardId: number) => {
    if (!confirm('Are you sure you want to delete this flashcard?')) return;

    try {
      await flashcardsAPI.delete(cardId);
      loadData();
    } catch (error) {
      console.error('Failed to delete flashcard:', error);
    }
  };

  const getDifficultyColor = (difficulty: number) => {
    if (difficulty <= 2) return 'text-green-600 bg-green-100';
    if (difficulty <= 3) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getDifficultyLabel = (difficulty: number) => {
    if (difficulty <= 2) return 'Easy';
    if (difficulty <= 3) return 'Medium';
    return 'Hard';
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading flashcards...</p>
        </div>
      </div>
    );
  }

  // Study Mode View
  if (mode === 'study' && studyCards.length > 0) {
    const currentCard = studyCards[currentCardIndex];
    const progress = ((currentCardIndex + 1) / studyCards.length) * 100;

    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 p-4 md:p-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-6">
            <button
              onClick={() => setMode('browse')}
              className="text-purple-600 hover:text-purple-700 flex items-center gap-2 mb-4"
            >
              ← Back to Browse
            </button>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Study Session</h1>
            <div className="flex items-center gap-4">
              <span className="text-gray-600">
                Card {currentCardIndex + 1} of {studyCards.length}
              </span>
              <div className="flex-1 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Flashcard */}
          <div className="perspective-1000">
            <div
              className={`relative bg-white rounded-2xl shadow-2xl p-12 min-h-[400px] flex items-center justify-center cursor-pointer transition-transform duration-500 ${
                showAnswer ? 'rotate-y-180' : ''
              }`}
              onClick={() => setShowAnswer(!showAnswer)}
            >
              {!showAnswer ? (
                <div className="text-center">
                  <span className="text-sm text-gray-500 mb-4 block">Question</span>
                  <p className="text-2xl font-medium text-gray-800">{currentCard.question}</p>
                  <p className="text-sm text-gray-400 mt-8">Click to reveal answer</p>
                </div>
              ) : (
                <div className="text-center transform rotate-y-180">
                  <span className="text-sm text-gray-500 mb-4 block">Answer</span>
                  <p className="text-2xl font-medium text-gray-800">{currentCard.answer}</p>
                  <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium mt-6 ${getDifficultyColor(currentCard.difficulty)}`}>
                    {getDifficultyLabel(currentCard.difficulty)}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Review Buttons */}
          {showAnswer && (
            <div className="mt-8 grid grid-cols-5 gap-4">
              <button
                onClick={() => handleReview(1)}
                className="bg-red-500 hover:bg-red-600 text-white py-4 px-4 rounded-lg font-medium transition-colors"
              >
                😰
                <br />
                <span className="text-sm">Forgot</span>
              </button>
              <button
                onClick={() => handleReview(2)}
                className="bg-orange-500 hover:bg-orange-600 text-white py-4 px-4 rounded-lg font-medium transition-colors"
              >
                😕
                <br />
                <span className="text-sm">Hard</span>
              </button>
              <button
                onClick={() => handleReview(3)}
                className="bg-yellow-500 hover:bg-yellow-600 text-white py-4 px-4 rounded-lg font-medium transition-colors"
              >
                🤔
                <br />
                <span className="text-sm">Good</span>
              </button>
              <button
                onClick={() => handleReview(4)}
                className="bg-green-500 hover:bg-green-600 text-white py-4 px-4 rounded-lg font-medium transition-colors"
              >
                😊
                <br />
                <span className="text-sm">Easy</span>
              </button>
              <button
                onClick={() => handleReview(5)}
                className="bg-blue-500 hover:bg-blue-600 text-white py-4 px-4 rounded-lg font-medium transition-colors"
              >
                🎯
                <br />
                <span className="text-sm">Perfect</span>
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Browse Mode View
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
            Flashcards
          </h1>
          <p className="text-gray-600">Master your knowledge with spaced repetition</p>
        </div>

        {/* Actions */}
        <div className="flex flex-wrap gap-4 mb-8">
          <button
            onClick={startStudySession}
            className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg transition-all flex items-center gap-2"
          >
            🎯 Start Study Session
          </button>
          
          <button
            onClick={() => router.push('/documents')}
            className="bg-white text-purple-600 px-6 py-3 rounded-lg font-medium hover:shadow-lg transition-all border-2 border-purple-200"
          >
            ➕ Generate from Document
          </button>

          <select
            value={selectedDocument || ''}
            onChange={(e) => setSelectedDocument(e.target.value ? parseInt(e.target.value) : null)}
            className="px-4 py-3 bg-white rounded-lg border-2 border-gray-200 focus:border-purple-400 focus:outline-none"
          >
            <option value="">All Documents</option>
            {documents.map((doc) => (
              <option key={doc.id} value={doc.id}>
                {doc.filename}
              </option>
            ))}
          </select>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-2xl shadow-lg p-6 border-2 border-purple-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Cards</p>
                <p className="text-3xl font-bold text-purple-600">{flashcards.length}</p>
              </div>
              <span className="text-4xl">📚</span>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6 border-2 border-green-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Documents</p>
                <p className="text-3xl font-bold text-green-600">{documents.length}</p>
              </div>
              <span className="text-4xl">📄</span>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6 border-2 border-orange-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Due for Review</p>
                <p className="text-3xl font-bold text-orange-600">
                  {flashcards.filter(c => c.next_review && new Date(c.next_review) <= new Date()).length}
                </p>
              </div>
              <span className="text-4xl">⏰</span>
            </div>
          </div>
        </div>

        {/* Flashcards Grid */}
        {flashcards.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
            <span className="text-6xl mb-4 block">📚</span>
            <h3 className="text-xl font-bold text-gray-800 mb-2">No flashcards yet</h3>
            <p className="text-gray-600 mb-6">
              Generate flashcards from your documents to start studying
            </p>
            <button
              onClick={() => router.push('/documents')}
              className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg transition-all"
            >
              Go to Documents
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {flashcards.map((card) => {
              const doc = documents.find(d => d.id === card.document_id);
              const isDue = card.next_review && new Date(card.next_review) <= new Date();
              
              return (
                <div
                  key={card.id}
                  className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-all"
                >
                  <div className="flex items-start justify-between mb-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getDifficultyColor(card.difficulty)}`}>
                      {getDifficultyLabel(card.difficulty)}
                    </span>
                    {isDue && (
                      <span className="px-3 py-1 bg-orange-100 text-orange-600 rounded-full text-xs font-medium">
                        Due Now
                      </span>
                    )}
                  </div>

                  <div className="mb-4">
                    <p className="text-sm text-gray-500 mb-2">Q:</p>
                    <p className="font-medium text-gray-800 line-clamp-3">{card.question}</p>
                  </div>

                  <div className="mb-4">
                    <p className="text-sm text-gray-500 mb-2">A:</p>
                    <p className="text-gray-600 line-clamp-2">{card.answer}</p>
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                    <span className="text-xs text-gray-500">
                      {doc?.filename || 'Unknown'}
                    </span>
                    <button
                      onClick={() => deleteCard(card.id)}
                      className="text-red-500 hover:text-red-600 text-sm font-medium"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/app/contexts/AuthContext';
import { studySessionsAPI, notesAPI } from '@/lib/api';

interface Note {
  id: number;
  content: string;
  type: string;
  created_at: string;
  updated_at: string;
}

export default function SessionPage() {
  const router = useRouter();
  const { isAuthenticated, loading: authLoading, logout } = useAuth();
  const [sessionDuration, setSessionDuration] = useState(25); // Duration in minutes
  const [timeLeft, setTimeLeft] = useState(25 * 60); // 25 minutes in seconds
  const [isRunning, setIsRunning] = useState(false);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [notes, setNotes] = useState('');
  const [sessionType, setSessionType] = useState<'study' | 'break'>('study');
  const [sessionNotes, setSessionNotes] = useState<Note[]>([]);
  const [newNoteContent, setNewNoteContent] = useState('');
  const [newNoteType, setNewNoteType] = useState('general');
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null);
  const [editingContent, setEditingContent] = useState('');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, authLoading, router]);

  useEffect(() => {
    // Update timeLeft when sessionDuration changes (only if not started)
    if (!sessionId && !isRunning && sessionType === 'study') {
      setTimeLeft(sessionDuration * 60);
    }
  }, [sessionDuration]);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (isRunning && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (timeLeft === 0) {
      handleTimerComplete();
    }

    return () => clearInterval(interval);
  }, [isRunning, timeLeft]);

  const startSession = async () => {
    try {
      const session = await studySessionsAPI.create({
        duration_minutes: sessionType === 'study' ? sessionDuration : 5,
      });
      setSessionId(session.id);
      setIsRunning(true);
      loadSessionNotes(session.id);
    } catch (error) {
      console.error('Failed to start session:', error);
      alert('Failed to start session');
    }
  };

  const loadSessionNotes = async (sessionIdToLoad: number) => {
    try {
      const notes = await notesAPI.list({ session_id: sessionIdToLoad });
      setSessionNotes(notes);
    } catch (error) {
      console.error('Failed to load notes:', error);
    }
  };

  const addNote = async () => {
    if (!sessionId || !newNoteContent.trim()) return;

    try {
      const note = await notesAPI.create({
        content: newNoteContent,
        type: newNoteType,
        session_id: sessionId,
      });
      setSessionNotes([...sessionNotes, note]);
      setNewNoteContent('');
      setNewNoteType('general');
    } catch (error) {
      console.error('Failed to add note:', error);
      alert('Failed to add note');
    }
  };

  const startEditNote = (note: Note) => {
    setEditingNoteId(note.id);
    setEditingContent(note.content);
  };

  const saveEditNote = async () => {
    if (!editingNoteId || !editingContent.trim()) return;

    try {
      const updated = await notesAPI.update(editingNoteId, {
        content: editingContent,
      });
      setSessionNotes(sessionNotes.map(n => n.id === editingNoteId ? updated : n));
      setEditingNoteId(null);
      setEditingContent('');
    } catch (error) {
      console.error('Failed to update note:', error);
      alert('Failed to update note');
    }
  };

  const deleteNote = async (noteId: number) => {
    if (!confirm('Delete this note?')) return;

    try {
      await notesAPI.delete(noteId);
      setSessionNotes(sessionNotes.filter(n => n.id !== noteId));
    } catch (error) {
      console.error('Failed to delete note:', error);
      alert('Failed to delete note');
    }
  };

  const pauseSession = () => {
    setIsRunning(false);
  };

  const resumeSession = () => {
    setIsRunning(true);
  };

  const handleTimerComplete = () => {
    setIsRunning(false);
    if (sessionType === 'study') {
      alert('Study session complete! Time for a break.');
    } else {
      alert('Break complete! Ready for another session?');
    }
  };

  const completeSession = async () => {
    if (!sessionId) return;

    try {
      await studySessionsAPI.complete(sessionId, {
        notes: notes || undefined,
        rating: 5,
      });
      alert('Session completed successfully!');
      resetSession();
      router.push('/dashboard');
    } catch (error) {
      console.error('Failed to complete session:', error);
      alert('Failed to complete session');
    }
  };

  const resetSession = () => {
    setIsRunning(false);
    setTimeLeft(sessionType === 'study' ? sessionDuration * 60 : 5 * 60);
    setSessionId(null);
    setNotes('');
    setSessionNotes([]);
    setNewNoteContent('');
    setEditingNoteId(null);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const switchSessionType = (type: 'study' | 'break') => {
    if (!isRunning) {
      setSessionType(type);
      setTimeLeft(type === 'study' ? sessionDuration * 60 : 5 * 60);
    }
  };

  const changeDuration = (minutes: number) => {
    if (!isRunning && !sessionId) {
      setSessionDuration(minutes);
      setTimeLeft(minutes * 60);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const progress = ((sessionType === 'study' ? sessionDuration * 60 : 5 * 60) - timeLeft) / (sessionType === 'study' ? sessionDuration * 60 : 5 * 60) * 100;

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
                <h1 className="text-2xl font-bold text-gray-900">Study Session</h1>
                <p className="text-sm text-gray-600">Pomodoro timer for focused studying</p>
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

      <div className="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Session Configuration */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="mb-4">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Session Type</h3>
            <div className="flex gap-4">
              <button
                onClick={() => switchSessionType('study')}
                disabled={isRunning}
                className={`flex-1 py-3 px-4 rounded-lg font-semibold transition ${
                  sessionType === 'study'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                } ${isRunning ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                Study Session
              </button>
              <button
                onClick={() => switchSessionType('break')}
                disabled={isRunning}
                className={`flex-1 py-3 px-4 rounded-lg font-semibold transition ${
                  sessionType === 'break'
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                } ${isRunning ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                Break
              </button>
            </div>
          </div>

          {sessionType === 'study' && (
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-3">Study Duration</h3>
              <div className="flex gap-3">
                <button
                  onClick={() => changeDuration(10)}
                  disabled={isRunning || !!sessionId}
                  className={`flex-1 py-2 px-4 rounded-lg font-medium transition ${
                    sessionDuration === 10
                      ? 'bg-indigo-100 text-indigo-700 border-2 border-indigo-600'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border-2 border-transparent'
                  } ${isRunning || sessionId ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  10 min
                </button>
                <button
                  onClick={() => changeDuration(25)}
                  disabled={isRunning || !!sessionId}
                  className={`flex-1 py-2 px-4 rounded-lg font-medium transition ${
                    sessionDuration === 25
                      ? 'bg-indigo-100 text-indigo-700 border-2 border-indigo-600'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border-2 border-transparent'
                  } ${isRunning || sessionId ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  25 min
                </button>
                <button
                  onClick={() => changeDuration(45)}
                  disabled={isRunning || !!sessionId}
                  className={`flex-1 py-2 px-4 rounded-lg font-medium transition ${
                    sessionDuration === 45
                      ? 'bg-indigo-100 text-indigo-700 border-2 border-indigo-600'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border-2 border-transparent'
                  } ${isRunning || sessionId ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  45 min
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Timer Display */}
        <div className="bg-white rounded-lg shadow p-8 mb-6">
          <div className="text-center">
            {/* Progress Ring */}
            <div className="relative inline-flex items-center justify-center mb-6">
              <svg className="transform -rotate-90 w-64 h-64">
                <circle
                  cx="128"
                  cy="128"
                  r="120"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="none"
                  className="text-gray-200"
                />
                <circle
                  cx="128"
                  cy="128"
                  r="120"
                  stroke="currentColor"
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={2 * Math.PI * 120}
                  strokeDashoffset={2 * Math.PI * 120 * (1 - progress / 100)}
                  className={sessionType === 'study' ? 'text-indigo-600' : 'text-green-600'}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute text-6xl font-bold text-gray-900">
                {formatTime(timeLeft)}
              </div>
            </div>

            {/* Controls */}
            <div className="flex justify-center gap-4 mt-6">
              {!isRunning && !sessionId ? (
                <button
                  onClick={startSession}
                  className="px-8 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition shadow-lg"
                >
                  Start Session
                </button>
              ) : isRunning ? (
                <button
                  onClick={pauseSession}
                  className="px-8 py-3 bg-yellow-600 text-white font-semibold rounded-lg hover:bg-yellow-700 transition shadow-lg"
                >
                  Pause
                </button>
              ) : (
                <>
                  <button
                    onClick={resumeSession}
                    className="px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition shadow-lg"
                  >
                    Resume
                  </button>
                  <button
                    onClick={completeSession}
                    className="px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition shadow-lg"
                  >
                    Complete
                  </button>
                  <button
                    onClick={resetSession}
                    className="px-6 py-3 bg-gray-600 text-white font-semibold rounded-lg hover:bg-gray-700 transition shadow-lg"
                  >
                    Reset
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Notes */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Session Notes</h2>
          
          {/* Add New Note */}
          {sessionId && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <div className="flex gap-2 mb-3">
                <select
                  value={newNoteType}
                  onChange={(e) => setNewNoteType(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-gray-900"
                >
                  <option value="general">General</option>
                  <option value="question">Question</option>
                  <option value="insight">Insight</option>
                  <option value="distraction">Distraction</option>
                </select>
              </div>
              <textarea
                value={newNoteContent}
                onChange={(e) => setNewNoteContent(e.target.value)}
                placeholder="Write a note..."
                className="w-full h-24 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none text-gray-900 mb-2"
              />
              <button
                onClick={addNote}
                disabled={!newNoteContent.trim()}
                className="px-4 py-2 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                Add Note
              </button>
            </div>
          )}

          {/* Notes List */}
          {sessionNotes.length > 0 ? (
            <div className="space-y-3">
              {sessionNotes.map((note) => (
                <div
                  key={note.id}
                  className={`p-4 rounded-lg border-l-4 ${
                    note.type === 'question'
                      ? 'bg-yellow-50 border-yellow-400'
                      : note.type === 'insight'
                      ? 'bg-green-50 border-green-400'
                      : note.type === 'distraction'
                      ? 'bg-red-50 border-red-400'
                      : 'bg-gray-50 border-gray-400'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-xs font-medium text-gray-600 uppercase">
                      {note.type}
                    </span>
                    <div className="flex gap-2">
                      {editingNoteId === note.id ? (
                        <>
                          <button
                            onClick={saveEditNote}
                            className="text-green-600 hover:text-green-800 text-sm font-medium"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => {
                              setEditingNoteId(null);
                              setEditingContent('');
                            }}
                            className="text-gray-600 hover:text-gray-800 text-sm font-medium"
                          >
                            Cancel
                          </button>
                        </>
                      ) : (
                        <>
                          <button
                            onClick={() => startEditNote(note)}
                            className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => deleteNote(note.id)}
                            className="text-red-600 hover:text-red-800 text-sm font-medium"
                          >
                            Delete
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                  {editingNoteId === note.id ? (
                    <textarea
                      value={editingContent}
                      onChange={(e) => setEditingContent(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded text-gray-900"
                      rows={3}
                    />
                  ) : (
                    <p className="text-gray-900">{note.content}</p>
                  )}
                  <p className="text-xs text-gray-500 mt-2">
                    {new Date(note.created_at).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          ) : sessionId ? (
            <p className="text-center text-gray-500 py-8">
              No notes yet. Add your first note above!
            </p>
          ) : (
            <p className="text-center text-gray-500 py-8">
              Start a session to take notes
            </p>
          )}
        </div>

        {/* Tips */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-2">Pomodoro Technique Tips</h3>
          <ul className="space-y-1 text-sm text-blue-800">
            <li>• Focus on one task during each 25-minute session</li>
            <li>• Take a 5-minute break after each session</li>
            <li>• Take a longer 15-30 minute break after 4 sessions</li>
            <li>• Eliminate all distractions during study time</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

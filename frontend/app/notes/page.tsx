'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/app/contexts/AuthContext';
import { notesAPI } from '@/lib/api';

interface Note {
  id: number;
  content: string;
  type: string;
  session_id: number | null;
  created_at: string;
  updated_at: string;
}

export default function NotesPage() {
  const router = useRouter();
  const { isAuthenticated, loading: authLoading, logout } = useAuth();
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null);
  const [editingContent, setEditingContent] = useState('');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    } else if (isAuthenticated) {
      loadNotes();
    }
  }, [isAuthenticated, authLoading, router]);

  const loadNotes = async () => {
    try {
      const allNotes = await notesAPI.list();
      setNotes(allNotes);
    } catch (error) {
      console.error('Failed to load notes:', error);
    } finally {
      setLoading(false);
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
      setNotes(notes.map(n => n.id === editingNoteId ? updated : n));
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
      setNotes(notes.filter(n => n.id !== noteId));
    } catch (error) {
      console.error('Failed to delete note:', error);
      alert('Failed to delete note');
    }
  };

  const filteredNotes = notes.filter(note => {
    const matchesType = filterType === 'all' || note.type === filterType;
    const matchesSearch = note.content.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesSearch;
  });

  const groupedByDate = filteredNotes.reduce((groups, note) => {
    const date = new Date(note.created_at).toLocaleDateString();
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(note);
    return groups;
  }, {} as Record<string, Note[]>);

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
                <h1 className="text-2xl font-bold text-gray-900">My Notes</h1>
                <p className="text-sm text-gray-600">All your study notes in one place</p>
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
        {/* Filters and Search */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search notes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-gray-900"
              />
            </div>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 text-gray-900"
            >
              <option value="all">All Types</option>
              <option value="general">General</option>
              <option value="question">Question</option>
              <option value="insight">Insight</option>
              <option value="distraction">Distraction</option>
            </select>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Total Notes</div>
            <div className="text-2xl font-bold text-gray-900">{notes.length}</div>
          </div>
          <div className="bg-yellow-50 rounded-lg shadow p-4">
            <div className="text-sm text-yellow-800">Questions</div>
            <div className="text-2xl font-bold text-yellow-900">
              {notes.filter(n => n.type === 'question').length}
            </div>
          </div>
          <div className="bg-green-50 rounded-lg shadow p-4">
            <div className="text-sm text-green-800">Insights</div>
            <div className="text-2xl font-bold text-green-900">
              {notes.filter(n => n.type === 'insight').length}
            </div>
          </div>
          <div className="bg-red-50 rounded-lg shadow p-4">
            <div className="text-sm text-red-800">Distractions</div>
            <div className="text-2xl font-bold text-red-900">
              {notes.filter(n => n.type === 'distraction').length}
            </div>
          </div>
        </div>

        {/* Notes by Date */}
        {Object.keys(groupedByDate).length > 0 ? (
          <div className="space-y-6">
            {Object.entries(groupedByDate).map(([date, dateNotes]) => (
              <div key={date} className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">{date}</h2>
                <div className="space-y-3">
                  {dateNotes.map((note) => (
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
                        <div>
                          <span className="text-xs font-medium text-gray-600 uppercase">
                            {note.type}
                          </span>
                          {note.session_id && (
                            <span className="ml-2 text-xs text-gray-500">
                              Session #{note.session_id}
                            </span>
                          )}
                        </div>
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
                        <p className="text-gray-900 whitespace-pre-wrap">{note.content}</p>
                      )}
                      <p className="text-xs text-gray-500 mt-2">
                        {new Date(note.created_at).toLocaleTimeString()}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-500 text-lg">
              {searchQuery || filterType !== 'all'
                ? 'No notes match your filters'
                : 'No notes yet. Start a study session and take some notes!'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

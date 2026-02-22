'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/app/contexts/AuthContext';
import { documentsAPI, studySessionsAPI, studyPlansAPI } from '@/lib/api';

interface Stats {
  totalDocuments: number;
  totalSessions: number;
  totalStudyTime: number;
  activePlans: number;
}

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, loading: authLoading, logout } = useAuth();
  const [stats, setStats] = useState<Stats>({
    totalDocuments: 0,
    totalSessions: 0,
    totalStudyTime: 0,
    activePlans: 0,
  });
  const [recentSessions, setRecentSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    } else if (isAuthenticated) {
      loadDashboardData();
    }
  }, [isAuthenticated, authLoading, router]);

  const loadDashboardData = async () => {
    try {
      const [documents, sessions, plans] = await Promise.all([
        documentsAPI.list(),
        studySessionsAPI.list(),
        studyPlansAPI.list(),
      ]);

      const completedSessions = sessions.filter((s: any) => s.status === 'completed');
      const totalMinutes = completedSessions.reduce(
        (sum: number, s: any) => sum + (s.total_duration_minutes || 0),
        0
      );

      setStats({
        totalDocuments: documents.length,
        totalSessions: completedSessions.length,
        totalStudyTime: Math.round(totalMinutes / 60),
        activePlans: plans.length,
      });

      setRecentSessions(sessions.slice(0, 5));
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <img src="/logo.png" alt="CogniFlow" className="h-24 w-auto" />
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Welcome back, {user?.full_name}</p>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => router.push('/profile')}
              className="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
            >
              Profile
            </button>
            <button
              onClick={logout}
              className="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Documents</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.totalDocuments}</p>
              </div>
              <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-full">
                <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Study Sessions</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.totalSessions}</p>
              </div>
              <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-full">
                <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Study Hours</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.totalStudyTime}</p>
              </div>
              <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-full">
                <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Active Plans</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.activePlans}</p>
              </div>
              <div className="p-3 bg-yellow-100 dark:bg-yellow-900/30 rounded-full">
                <svg className="w-6 h-6 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <button
              onClick={() => router.push('/documents')}
              className="p-4 border-2 border-indigo-200 dark:border-indigo-800 rounded-lg hover:border-indigo-400 dark:hover:border-indigo-600 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 transition text-left"
            >
              <div className="font-semibold text-gray-900 dark:text-white mb-1">Upload Document</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Add new study materials</div>
            </button>

            <button
              onClick={() => router.push('/session')}
              className="p-4 border-2 border-green-200 dark:border-green-800 rounded-lg hover:border-green-400 dark:hover:border-green-600 hover:bg-green-50 dark:hover:bg-green-900/30 transition text-left"
            >
              <div className="font-semibold text-gray-900 dark:text-white mb-1">Start Session</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Begin a new study session</div>
            </button>

            <button
              onClick={() => router.push('/plan')}
              className="p-4 border-2 border-purple-200 dark:border-purple-800 rounded-lg hover:border-purple-400 dark:hover:border-purple-600 hover:bg-purple-50 dark:hover:bg-purple-900/30 transition text-left"
            >
              <div className="font-semibold text-gray-900 dark:text-white mb-1">Create Plan</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Generate AI study plan</div>
            </button>

            <button
              onClick={() => router.push('/notes')}
              className="p-4 border-2 border-yellow-200 dark:border-yellow-800 rounded-lg hover:border-yellow-400 dark:hover:border-yellow-600 hover:bg-yellow-50 dark:hover:bg-yellow-900/30 transition text-left"
            >
              <div className="font-semibold text-gray-900 dark:text-white mb-1">View Notes</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Browse all your notes</div>
            </button>

            <button
              onClick={() => router.push('/analytics')}
              className="p-4 border-2 border-pink-200 dark:border-pink-800 rounded-lg hover:border-pink-400 dark:hover:border-pink-600 hover:bg-pink-50 dark:hover:bg-pink-900/30 transition text-left"
            >
              <div className="font-semibold text-gray-900 dark:text-white mb-1">Analytics</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">View insights & progress</div>
            </button>

            <button
              onClick={() => router.push('/flashcards')}
              className="p-4 border-2 border-blue-200 dark:border-blue-800 rounded-lg hover:border-blue-400 dark:hover:border-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/30 transition text-left"
            >
              <div className="font-semibold text-gray-900 dark:text-white mb-1">Flashcards</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Study with spaced repetition</div>
            </button>

            <button
              onClick={() => router.push('/concept-map')}
              className="p-4 border-2 border-teal-200 dark:border-teal-800 rounded-lg hover:border-teal-400 dark:hover:border-teal-600 hover:bg-teal-50 dark:hover:bg-teal-900/30 transition text-left"
            >
              <div className="font-semibold text-gray-900 dark:text-white mb-1">Concept Map</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Visualize knowledge graphs</div>
            </button>

            <button
              onClick={() => router.push('/mood')}
              className="p-4 border-2 border-rose-200 dark:border-rose-800 rounded-lg hover:border-rose-400 dark:hover:border-rose-600 hover:bg-rose-50 dark:hover:bg-rose-900/30 transition text-left"
            >
              <div className="font-semibold text-gray-900 dark:text-white mb-1">Mood Tracker 🌈</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Track emotional state</div>
            </button>
          </div>
        </div>

        {/* Recent Sessions */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Recent Activity</h2>
          {recentSessions.length === 0 ? (
            <p className="text-gray-600 dark:text-gray-400 text-center py-8">No study sessions yet. Start your first session!</p>
          ) : (
            <div className="space-y-3">
              {recentSessions.map((session: any) => (
                <div key={session.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">Study Session</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {session.total_duration_minutes} minutes • {new Date(session.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      session.status === 'completed'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}
                  >
                    {session.status === 'completed' ? 'Completed' : 'In Progress'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

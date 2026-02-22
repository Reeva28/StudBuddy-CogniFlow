'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';
import { analyticsAPI } from '@/lib/api';

interface SessionStats {
  total_sessions: number;
  completed_sessions: number;
  total_study_minutes: number;
  average_session_minutes: number;
  completion_rate: number;
  current_streak_days: number;
  longest_streak_days: number;
}

interface NoteStats {
  total_notes: number;
  notes_by_type: { [key: string]: number };
  average_notes_per_session: number;
}

interface ProductivityStats {
  average_focus_rating: number | null;
  average_productivity_rating: number | null;
  most_productive_hour: number | null;
  total_break_minutes: number;
}

interface RecentSession {
  id: number;
  title: string;
  subject: string;
  start_time: string | null;
  end_time: string | null;
  actual_duration_minutes: number | null;
  status: string;
  focus_rating: number | null;
  notes_count: number;
}

interface TimeDistribution {
  hour: number;
  minutes: number;
  session_count: number;
}

interface DailyActivity {
  date: string;
  total_minutes: number;
  session_count: number;
  notes_count: number;
  average_focus: number | null;
}

interface AnalyticsDashboard {
  session_stats: SessionStats;
  note_stats: NoteStats;
  productivity_stats: ProductivityStats;
  recent_sessions: RecentSession[];
  time_distribution: TimeDistribution[];
  daily_activity: DailyActivity[];
  weekly_summary: { [key: string]: number };
  monthly_summary: { [key: string]: number };
}

export default function AnalyticsPage() {
  const router = useRouter();
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [dashboard, setDashboard] = useState<AnalyticsDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedView, setSelectedView] = useState<'week' | 'month' | 'all'>('week');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, authLoading, router]);

  useEffect(() => {
    if (isAuthenticated) {
      loadDashboard();
    }
  }, [isAuthenticated]);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const data = await analyticsAPI.getDashboard();
      setDashboard(data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatMinutes = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  const formatHour = (hour: number) => {
    if (hour === 0) return '12 AM';
    if (hour === 12) return '12 PM';
    if (hour < 12) return `${hour} AM`;
    return `${hour - 12} PM`;
  };

  const getMaxMinutes = (distribution: TimeDistribution[]) => {
    return Math.max(...distribution.map(d => d.minutes), 1);
  };

  const getMaxDailyMinutes = (activity: DailyActivity[]) => {
    return Math.max(...activity.map(d => d.total_minutes), 1);
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 flex items-center justify-center">
        <p className="text-gray-600">No data available</p>
      </div>
    );
  }

  const { session_stats, note_stats, productivity_stats, recent_sessions, time_distribution, daily_activity, weekly_summary, monthly_summary } = dashboard;
  
  // Get current summary based on selected view
  const getCurrentSummaryMinutes = () => {
    if (selectedView === 'all') return session_stats.total_study_minutes;
    if (selectedView === 'week') return weekly_summary.total_minutes;
    return monthly_summary.total_minutes;
  };
  
  const getCurrentSummarySessions = () => {
    if (selectedView === 'all') return session_stats.total_sessions;
    if (selectedView === 'week') return weekly_summary.total_sessions;
    return monthly_summary.total_sessions;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
            Analytics & Insights
          </h1>
          <p className="text-gray-600">Track your learning progress and productivity patterns</p>
        </div>

        {/* Time Period Selector */}
        <div className="mb-6 flex gap-2">
          <button
            onClick={() => setSelectedView('week')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedView === 'week'
                ? 'bg-purple-600 text-white'
                : 'bg-white text-gray-700 hover:bg-purple-50'
            }`}
          >
            This Week
          </button>
          <button
            onClick={() => setSelectedView('month')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedView === 'month'
                ? 'bg-purple-600 text-white'
                : 'bg-white text-gray-700 hover:bg-purple-50'
            }`}
          >
            This Month
          </button>
          <button
            onClick={() => setSelectedView('all')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedView === 'all'
                ? 'bg-purple-600 text-white'
                : 'bg-white text-gray-700 hover:bg-purple-50'
            }`}
          >
            All Time
          </button>
        </div>

        {/* Key Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Study Time */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border-2 border-purple-100">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-gray-600 text-sm font-medium">Total Study Time</h3>
              <span className="text-2xl">⏱️</span>
            </div>
            <p className="text-3xl font-bold text-purple-600">
              {formatMinutes(getCurrentSummaryMinutes())}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              {getCurrentSummarySessions()} sessions
            </p>
          </div>

          {/* Current Streak */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border-2 border-orange-100">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-gray-600 text-sm font-medium">Current Streak</h3>
              <span className="text-2xl">🔥</span>
            </div>
            <p className="text-3xl font-bold text-orange-600">
              {session_stats.current_streak_days} days
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Longest: {session_stats.longest_streak_days} days
            </p>
          </div>

          {/* Completion Rate */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border-2 border-green-100">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-gray-600 text-sm font-medium">Completion Rate</h3>
              <span className="text-2xl">✅</span>
            </div>
            <p className="text-3xl font-bold text-green-600">
              {session_stats.completion_rate}%
            </p>
            <p className="text-sm text-gray-500 mt-1">
              {session_stats.completed_sessions} completed
            </p>
          </div>

          {/* Total Notes */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border-2 border-blue-100">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-gray-600 text-sm font-medium">Total Notes</h3>
              <span className="text-2xl">📝</span>
            </div>
            <p className="text-3xl font-bold text-blue-600">
              {note_stats.total_notes}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              {note_stats.average_notes_per_session} per session
            </p>
          </div>
        </div>

        {/* Additional Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Average Focus */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h3 className="text-gray-600 text-sm font-medium mb-3">Average Focus Rating</h3>
            <div className="flex items-center gap-4">
              <div className="relative w-20 h-20">
                <svg className="transform -rotate-90" viewBox="0 0 36 36">
                  <circle
                    cx="18"
                    cy="18"
                    r="16"
                    fill="none"
                    stroke="#e5e7eb"
                    strokeWidth="3"
                  />
                  <circle
                    cx="18"
                    cy="18"
                    r="16"
                    fill="none"
                    stroke="#8b5cf6"
                    strokeWidth="3"
                    strokeDasharray={`${((productivity_stats.average_focus_rating || 0) / 5) * 100} 100`}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-xl font-bold text-purple-600">
                    {productivity_stats.average_focus_rating?.toFixed(1) || 'N/A'}
                  </span>
                </div>
              </div>
              <div className="text-sm text-gray-600">
                {productivity_stats.average_focus_rating ? `${((productivity_stats.average_focus_rating / 5) * 100).toFixed(0)}% focus level` : 'No data yet'}
              </div>
            </div>
          </div>

          {/* Average Productivity */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h3 className="text-gray-600 text-sm font-medium mb-3">Average Productivity</h3>
            <div className="flex items-center gap-4">
              <div className="relative w-20 h-20">
                <svg className="transform -rotate-90" viewBox="0 0 36 36">
                  <circle
                    cx="18"
                    cy="18"
                    r="16"
                    fill="none"
                    stroke="#e5e7eb"
                    strokeWidth="3"
                  />
                  <circle
                    cx="18"
                    cy="18"
                    r="16"
                    fill="none"
                    stroke="#ec4899"
                    strokeWidth="3"
                    strokeDasharray={`${((productivity_stats.average_productivity_rating || 0) / 5) * 100} 100`}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-xl font-bold text-pink-600">
                    {productivity_stats.average_productivity_rating?.toFixed(1) || 'N/A'}
                  </span>
                </div>
              </div>
              <div className="text-sm text-gray-600">
                {productivity_stats.average_productivity_rating ? `${((productivity_stats.average_productivity_rating / 5) * 100).toFixed(0)}% productivity` : 'No data yet'}
              </div>
            </div>
          </div>

          {/* Most Productive Hour */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h3 className="text-gray-600 text-sm font-medium mb-3">Most Productive Hour</h3>
            <div className="flex items-center gap-4">
              <span className="text-4xl">🌟</span>
              <div>
                <p className="text-2xl font-bold text-blue-600">
                  {productivity_stats.most_productive_hour !== null 
                    ? formatHour(productivity_stats.most_productive_hour)
                    : 'N/A'}
                </p>
                <p className="text-sm text-gray-600">Peak performance time</p>
              </div>
            </div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Study Time by Hour */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-800 mb-4">Study Time Distribution</h3>
            <p className="text-sm text-gray-600 mb-4">Hours of the day you study most</p>
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {time_distribution
                .filter(d => d.minutes > 0)
                .sort((a, b) => b.minutes - a.minutes)
                .slice(0, 12)
                .map((dist, idx) => (
                  <div key={dist.hour} className="flex items-center gap-3">
                    <span className="text-sm font-medium text-gray-600 w-16">
                      {formatHour(dist.hour)}
                    </span>
                    <div className="flex-1 bg-gray-200 rounded-full h-8 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-purple-500 to-pink-500 h-full flex items-center px-3 text-white text-sm font-medium transition-all"
                        style={{
                          width: `${(dist.minutes / getMaxMinutes(time_distribution)) * 100}%`,
                          minWidth: dist.minutes > 0 ? '60px' : '0'
                        }}
                      >
                        {formatMinutes(dist.minutes)}
                      </div>
                    </div>
                    <span className="text-xs text-gray-500 w-16 text-right">
                      {dist.session_count} sessions
                    </span>
                  </div>
                ))}
              {time_distribution.filter(d => d.minutes > 0).length === 0 && (
                <p className="text-center text-gray-500 py-8">No study data yet</p>
              )}
            </div>
          </div>

          {/* Notes by Type */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-800 mb-4">Notes Breakdown</h3>
            <p className="text-sm text-gray-600 mb-4">Types of notes you create</p>
            <div className="space-y-4">
              {Object.entries(note_stats.notes_by_type).map(([type, count]) => {
                const percentage = (count / note_stats.total_notes) * 100;
                const colors: { [key: string]: string } = {
                  general: 'from-blue-500 to-blue-600',
                  question: 'from-yellow-500 to-orange-500',
                  insight: 'from-green-500 to-emerald-500',
                  distraction: 'from-red-500 to-pink-500',
                };
                const icons: { [key: string]: string } = {
                  general: '📝',
                  question: '❓',
                  insight: '💡',
                  distraction: '⚠️',
                };
                
                return (
                  <div key={type}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700 capitalize flex items-center gap-2">
                        <span>{icons[type] || '📝'}</span>
                        {type}
                      </span>
                      <span className="text-sm font-bold text-gray-800">{count} ({percentage.toFixed(0)}%)</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                      <div
                        className={`bg-gradient-to-r ${colors[type] || 'from-gray-500 to-gray-600'} h-full transition-all`}
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
              {Object.keys(note_stats.notes_by_type).length === 0 && (
                <p className="text-center text-gray-500 py-8">No notes yet</p>
              )}
            </div>
          </div>
        </div>

        {/* Daily Activity Chart */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Daily Activity (Last 30 Days)</h3>
          <p className="text-sm text-gray-600 mb-4">Your study patterns over time</p>
          <div className="overflow-x-auto">
            <div className="flex gap-2 items-end h-40 min-w-max pb-8">
              {daily_activity.slice(-30).map((day, idx) => {
                const height = day.total_minutes > 0 
                  ? (day.total_minutes / getMaxDailyMinutes(daily_activity)) * 100
                  : 0;
                
                return (
                  <div key={day.date} className="flex flex-col items-center gap-2">
                    <div className="relative group">
                      <div
                        className={`w-8 rounded-t-lg transition-all ${
                          day.total_minutes > 0
                            ? 'bg-gradient-to-t from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600'
                            : 'bg-gray-200'
                        }`}
                        style={{ height: `${Math.max(height, 4)}px` }}
                      ></div>
                      {day.total_minutes > 0 && (
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block bg-gray-900 text-white text-xs rounded py-1 px-2 whitespace-nowrap z-10">
                          {formatMinutes(day.total_minutes)}
                          <br />
                          {day.session_count} sessions
                          <br />
                          {day.notes_count} notes
                          {day.average_focus && (
                            <>
                              <br />
                              Focus: {day.average_focus.toFixed(1)}/5
                            </>
                          )}
                        </div>
                      )}
                    </div>
                    <span className="text-xs text-gray-500 transform -rotate-45 origin-top-left w-12">
                      {new Date(day.date).getDate()}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Recent Sessions */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-lg font-bold text-gray-800 mb-4">Recent Sessions</h3>
          <div className="space-y-3">
            {recent_sessions.slice(0, 10).map((session) => (
              <div
                key={session.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{session.title}</h4>
                  <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                    <span className="flex items-center gap-1">
                      📚 {session.subject}
                    </span>
                    {session.actual_duration_minutes && (
                      <span className="flex items-center gap-1">
                        ⏱️ {formatMinutes(session.actual_duration_minutes)}
                      </span>
                    )}
                    <span className="flex items-center gap-1">
                      📝 {session.notes_count} notes
                    </span>
                    {session.focus_rating && (
                      <span className="flex items-center gap-1">
                        ⭐ {session.focus_rating}/5
                      </span>
                    )}
                  </div>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${
                    session.status === 'completed'
                      ? 'bg-green-100 text-green-700'
                      : session.status === 'active'
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  {session.status}
                </span>
              </div>
            ))}
            {recent_sessions.length === 0 && (
              <p className="text-center text-gray-500 py-8">No sessions yet. Start studying to see your progress!</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

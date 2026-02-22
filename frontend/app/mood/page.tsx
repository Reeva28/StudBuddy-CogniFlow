'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { moodAPI } from '@/lib/api';

interface Mood {
  id: number;
  mood_type: string;
  intensity: number;
  is_before_session: boolean;
  study_session_id: number | null;
  notes: string | null;
  recorded_at: string;
}

interface MoodStats {
  total_moods: number;
  avg_intensity: number;
  most_common_mood: string;
  mood_improvement_rate: number;
  recent_trend: string;
}

interface MoodTrend {
  date: string;
  avg_before_intensity: number | null;
  avg_after_intensity: number | null;
  most_common_mood: string | null;
  session_count: number;
}

const MOOD_TYPES = [
  { value: 'happy', label: 'Happy', emoji: '😊', color: 'bg-yellow-100 border-yellow-300' },
  { value: 'focused', label: 'Focused', emoji: '🎯', color: 'bg-blue-100 border-blue-300' },
  { value: 'stressed', label: 'Stressed', emoji: '😰', color: 'bg-red-100 border-red-300' },
  { value: 'tired', label: 'Tired', emoji: '😴', color: 'bg-gray-100 border-gray-300' },
  { value: 'energized', label: 'Energized', emoji: '⚡', color: 'bg-green-100 border-green-300' },
  { value: 'frustrated', label: 'Frustrated', emoji: '😤', color: 'bg-orange-100 border-orange-300' },
  { value: 'motivated', label: 'Motivated', emoji: '💪', color: 'bg-purple-100 border-purple-300' },
];

export default function MoodPage() {
  const router = useRouter();
  const [moods, setMoods] = useState<Mood[]>([]);
  const [stats, setStats] = useState<MoodStats | null>(null);
  const [trends, setTrends] = useState<MoodTrend[]>([]);
  const [loading, setLoading] = useState(true);
  const [showLogModal, setShowLogModal] = useState(false);
  const [selectedMoodType, setSelectedMoodType] = useState('');
  const [intensity, setIntensity] = useState(3);
  const [notes, setNotes] = useState('');
  const [isBeforeSession, setIsBeforeSession] = useState(true);
  const [logging, setLogging] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [moodsData, statsData, trendsData] = await Promise.all([
        moodAPI.getAll(0, 50),
        moodAPI.getStats(30),
        moodAPI.getTrends(30),
      ]);
      setMoods(moodsData);
      setStats(statsData);
      setTrends(trendsData);
    } catch (error) {
      console.error('Error loading mood data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogMood = async () => {
    if (!selectedMoodType) {
      alert('Please select a mood');
      return;
    }

    try {
      setLogging(true);
      await moodAPI.create({
        mood_type: selectedMoodType,
        intensity,
        is_before_session: isBeforeSession,
        notes: notes || undefined,
      });
      setShowLogModal(false);
      setSelectedMoodType('');
      setIntensity(3);
      setNotes('');
      loadData();
    } catch (error) {
      console.error('Error logging mood:', error);
      alert('Failed to log mood');
    } finally {
      setLogging(false);
    }
  };

  const getMoodEmoji = (moodType: string) => {
    const mood = MOOD_TYPES.find(m => m.value === moodType);
    return mood?.emoji || '😐';
  };

  const getTrendIndicator = (trend: string) => {
    if (trend === 'improving') return { icon: '📈', color: 'text-green-600', label: 'Improving' };
    if (trend === 'declining') return { icon: '📉', color: 'text-red-600', label: 'Declining' };
    return { icon: '➡️', color: 'text-gray-600', label: 'Stable' };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 p-8">
        <div className="max-w-7xl mx-auto text-center">
          <div className="text-gray-600">Loading mood data...</div>
        </div>
      </div>
    );
  }

  const trendInfo = stats ? getTrendIndicator(stats.recent_trend) : null;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Mood Tracker 🌈</h1>
          <p className="text-gray-700">Track your emotional state and patterns</p>
        </div>

        {/* Quick Log Mood - Horizontal Layout */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Log Mood</h2>
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-end">
            {/* Mood Selection */}
            <div className="lg:col-span-5">
              <label className="block text-sm font-medium text-gray-900 mb-2">How are you feeling?</label>
              <div className="grid grid-cols-4 gap-2">
                {MOOD_TYPES.map((mood) => (
                  <button
                    key={mood.value}
                    onClick={() => setSelectedMoodType(mood.value)}
                    className={`p-2 border-2 rounded-lg transition ${
                      selectedMoodType === mood.value
                        ? mood.color + ' border-opacity-100 ring-2 ring-offset-1'
                        : 'border-gray-300 hover:border-gray-400 bg-white'
                    }`}
                    title={mood.label}
                  >
                    <div className="text-2xl">{mood.emoji}</div>
                    <div className="text-xs font-medium text-gray-900">{mood.label}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Intensity */}
            <div className="lg:col-span-2">
              <label className="block text-sm font-medium text-gray-900 mb-2">
                Intensity: {intensity}/5
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={intensity}
                onChange={(e) => setIntensity(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-300 rounded-lg appearance-none cursor-pointer accent-purple-600"
              />
              <div className="flex justify-between text-xs text-gray-700 mt-1">
                <span>Mild</span>
                <span>Strong</span>
              </div>
            </div>

            {/* Timing */}
            <div className="lg:col-span-2">
              <label className="block text-sm font-medium text-gray-900 mb-2">When?</label>
              <div className="flex gap-2">
                <button
                  onClick={() => setIsBeforeSession(true)}
                  className={`flex-1 py-2 px-3 rounded-lg transition text-sm font-medium ${
                    isBeforeSession
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  Before
                </button>
                <button
                  onClick={() => setIsBeforeSession(false)}
                  className={`flex-1 py-2 px-3 rounded-lg transition text-sm font-medium ${
                    !isBeforeSession
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  After
                </button>
              </div>
            </div>

            {/* Notes */}
            <div className="lg:col-span-2">
              <label className="block text-sm font-medium text-gray-900 mb-2">Notes (optional)</label>
              <input
                type="text"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Quick note..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 bg-white"
              />
            </div>

            {/* Submit Button */}
            <div className="lg:col-span-1">
              <button
                onClick={handleLogMood}
                disabled={logging || !selectedMoodType}
                className="w-full px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-md"
              >
                {logging ? '...' : 'Log'}
              </button>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="text-sm text-gray-700 font-medium mb-1">Total Moods</div>
              <div className="text-3xl font-bold text-purple-600">{stats.total_moods}</div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="text-sm text-gray-700 font-medium mb-1">Avg Intensity</div>
              <div className="text-3xl font-bold text-blue-600">{stats.avg_intensity}/5</div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="text-sm text-gray-700 font-medium mb-1">Common Mood</div>
              <div className="text-3xl">{getMoodEmoji(stats.most_common_mood)}</div>
              <div className="text-sm text-gray-900 font-medium capitalize">{stats.most_common_mood}</div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="text-sm text-gray-700 font-medium mb-1">Recent Trend</div>
              <div className="flex items-center gap-2">
                <span className="text-3xl">{trendInfo?.icon}</span>
                <span className={`text-lg font-semibold ${trendInfo?.color}`}>
                  {trendInfo?.label}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Mood Improvement Rate */}
        {stats && stats.total_moods > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Mood Improvement After Sessions</h2>
            <div className="relative pt-1">
              <div className="flex mb-2 items-center justify-between">
                <div>
                  <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-green-700 bg-green-200">
                    Improvement Rate
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-sm font-bold inline-block text-green-700">
                    {stats.mood_improvement_rate.toFixed(1)}%
                  </span>
                </div>
              </div>
              <div className="overflow-hidden h-4 mb-4 text-xs flex rounded-full bg-green-200">
                <div
                  style={{ width: `${stats.mood_improvement_rate}%` }}
                  className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-gradient-to-r from-green-500 to-green-600 transition-all duration-500"
                ></div>
              </div>
            </div>
          </div>
        )}

        {/* Trends Chart */}
        {trends.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">30-Day Mood Trends</h2>
            <div className="overflow-x-auto">
              <div className="flex gap-2 min-w-max">
                {trends.slice(-14).map((trend) => (
                  <div key={trend.date} className="flex flex-col items-center gap-2 p-2">
                    <div className="text-xs text-gray-900 font-medium whitespace-nowrap">
                      {new Date(trend.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </div>
                    <div className="flex flex-col gap-1">
                      {trend.avg_before_intensity && (
                        <div
                          className="w-12 bg-blue-500 rounded transition-all"
                          style={{ height: `${trend.avg_before_intensity * 20}px` }}
                          title={`Before: ${trend.avg_before_intensity.toFixed(1)}`}
                        ></div>
                      )}
                      {trend.avg_after_intensity && (
                        <div
                          className="w-12 bg-green-500 rounded transition-all"
                          style={{ height: `${trend.avg_after_intensity * 20}px` }}
                          title={`After: ${trend.avg_after_intensity.toFixed(1)}`}
                        ></div>
                      )}
                    </div>
                    <div className="text-xl">{trend.most_common_mood ? getMoodEmoji(trend.most_common_mood) : '—'}</div>
                  </div>
                ))}
              </div>
              <div className="flex gap-4 mt-4 justify-center text-sm text-gray-900">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-blue-500 rounded"></div>
                  <span>Before Session</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-green-500 rounded"></div>
                  <span>After Session</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Recent Moods */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Mood Logs</h2>
          {moods.length === 0 ? (
            <div className="text-center py-8 text-gray-700">
              No moods logged yet. Start tracking your emotional state!
            </div>
          ) : (
            <div className="space-y-3">
              {moods.slice(0, 10).map((mood) => {
                const moodInfo = MOOD_TYPES.find(m => m.value === mood.mood_type);
                return (
                  <div key={mood.id} className={`border-2 rounded-lg p-4 ${moodInfo?.color || 'bg-gray-100 border-gray-300'}`}>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-3xl">{getMoodEmoji(mood.mood_type)}</span>
                        <div>
                          <div className="font-semibold text-gray-900 capitalize">{mood.mood_type}</div>
                          <div className="text-sm text-gray-900">
                            Intensity: {'⭐'.repeat(mood.intensity)}
                          </div>
                          {mood.notes && <div className="text-sm text-gray-900 mt-1">{mood.notes}</div>}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xs text-gray-700 font-medium">
                          {new Date(mood.recorded_at).toLocaleString()}
                        </div>
                        <div className={`text-xs mt-1 px-2 py-1 rounded font-medium ${mood.is_before_session ? 'bg-blue-200 text-blue-900' : 'bg-green-200 text-green-900'}`}>
                          {mood.is_before_session ? 'Before Session' : 'After Session'}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>


      </div>
    </div>
  );
}

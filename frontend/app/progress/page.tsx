'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { analyticsAPI, studySessionsAPI, moodAPI } from '@/lib/api';

interface DailyActivity {
  date: string;
  study_minutes: number;
  session_count: number;
}

interface SessionStats {
  total_sessions: number;
  total_study_time: number;
  avg_session_length: number;
  completion_rate: number;
}

interface MoodTrend {
  date: string;
  avg_before_intensity: number | null;
  avg_after_intensity: number | null;
  most_common_mood: string | null;
  session_count: number;
}

export default function ProgressPage() {
  const router = useRouter();
  const [dailyActivity, setDailyActivity] = useState<DailyActivity[]>([]);
  const [sessionStats, setSessionStats] = useState<SessionStats | null>(null);
  const [moodTrends, setMoodTrends] = useState<MoodTrend[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState<7 | 30 | 90>(30);
  const [currentStreak, setCurrentStreak] = useState(0);
  const [longestStreak, setLongestStreak] = useState(0);

  useEffect(() => {
    loadProgressData();
  }, [timeRange]);

  const loadProgressData = async () => {
    try {
      setLoading(true);
      const [analyticsData, sessions, moods] = await Promise.all([
        analyticsAPI.getDashboard(timeRange),
        studySessionsAPI.list(),
        moodAPI.getTrends(timeRange),
      ]);

      setDailyActivity(analyticsData.daily_activity || []);
      
      // Calculate session stats
      const completedSessions = sessions.filter((s: any) => s.status === 'completed');
      const totalMinutes = completedSessions.reduce(
        (sum: number, s: any) => sum + (s.total_duration_minutes || 0),
        0
      );
      
      setSessionStats({
        total_sessions: completedSessions.length,
        total_study_time: totalMinutes,
        avg_session_length: completedSessions.length > 0 ? totalMinutes / completedSessions.length : 0,
        completion_rate: sessions.length > 0 ? (completedSessions.length / sessions.length) * 100 : 0,
      });

      setMoodTrends(moods);

      // Calculate streaks
      calculateStreaks(analyticsData.daily_activity || []);
    } catch (error) {
      console.error('Error loading progress data:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateStreaks = (activities: DailyActivity[]) => {
    if (activities.length === 0) {
      setCurrentStreak(0);
      setLongestStreak(0);
      return;
    }

    const sortedActivities = [...activities].sort((a, b) => 
      new Date(a.date).getTime() - new Date(b.date).getTime()
    );

    let current = 0;
    let longest = 0;
    let tempStreak = 0;
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Calculate longest streak
    for (let i = 0; i < sortedActivities.length; i++) {
      if (sortedActivities[i].study_minutes > 0) {
        tempStreak++;
        longest = Math.max(longest, tempStreak);
      } else {
        tempStreak = 0;
      }
    }

    // Calculate current streak (working backwards from today)
    for (let i = sortedActivities.length - 1; i >= 0; i--) {
      const activityDate = new Date(sortedActivities[i].date);
      activityDate.setHours(0, 0, 0, 0);
      
      if (sortedActivities[i].study_minutes > 0) {
        current++;
      } else {
        break;
      }
    }

    setCurrentStreak(current);
    setLongestStreak(longest);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 p-8">
        <div className="max-w-7xl mx-auto text-center">
          <div className="text-gray-600">Loading progress data...</div>
        </div>
      </div>
    );
  }

  const maxStudyMinutes = Math.max(...dailyActivity.map(d => d.study_minutes), 1);
  const maxSessions = Math.max(...dailyActivity.map(d => d.session_count), 1);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Progress Dashboard 📊</h1>
            <p className="text-gray-700">Track your learning journey</p>
          </div>
          <div className="flex gap-2">
            {[7, 30, 90].map((days) => (
              <button
                key={days}
                onClick={() => setTimeRange(days as 7 | 30 | 90)}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  timeRange === days
                    ? 'bg-indigo-600 text-white shadow-lg'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                {days} Days
              </button>
            ))}
          </div>
        </div>

        {/* Stats Grid */}
        {sessionStats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="text-sm text-gray-700 font-medium mb-1">Total Sessions</div>
              <div className="text-3xl font-bold text-indigo-600">{sessionStats.total_sessions}</div>
              <div className="text-xs text-gray-600 mt-1">Completed sessions</div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="text-sm text-gray-700 font-medium mb-1">Total Study Time</div>
              <div className="text-3xl font-bold text-purple-600">
                {Math.round(sessionStats.total_study_time / 60)}h
              </div>
              <div className="text-xs text-gray-600 mt-1">
                {sessionStats.total_study_time % 60}m additional
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="text-sm text-gray-700 font-medium mb-1">Avg Session</div>
              <div className="text-3xl font-bold text-blue-600">
                {Math.round(sessionStats.avg_session_length)}m
              </div>
              <div className="text-xs text-gray-600 mt-1">Per session</div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="text-sm text-gray-700 font-medium mb-1">Completion Rate</div>
              <div className="text-3xl font-bold text-green-600">
                {sessionStats.completion_rate.toFixed(0)}%
              </div>
              <div className="text-xs text-gray-600 mt-1">Sessions completed</div>
            </div>
          </div>
        )}

        {/* Streaks */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-gradient-to-br from-orange-400 to-red-500 rounded-xl shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium mb-1 opacity-90">Current Streak</div>
                <div className="text-5xl font-bold">{currentStreak}</div>
                <div className="text-sm mt-1 opacity-90">
                  {currentStreak === 1 ? 'day' : 'days'} in a row 🔥
                </div>
              </div>
              <div className="text-6xl">🔥</div>
            </div>
          </div>
          <div className="bg-gradient-to-br from-yellow-400 to-orange-500 rounded-xl shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium mb-1 opacity-90">Longest Streak</div>
                <div className="text-5xl font-bold">{longestStreak}</div>
                <div className="text-sm mt-1 opacity-90">
                  {longestStreak === 1 ? 'day' : 'days'} personal best 🏆
                </div>
              </div>
              <div className="text-6xl">🏆</div>
            </div>
          </div>
        </div>

        {/* Study Time Chart */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Daily Study Time</h2>
          <div className="overflow-x-auto">
            <div className="flex items-end gap-2 min-w-max h-64">
              {dailyActivity.map((day) => (
                <div key={day.date} className="flex flex-col items-center gap-2 flex-1 min-w-[40px]">
                  <div className="text-xs text-gray-700 font-medium">
                    {day.study_minutes}m
                  </div>
                  <div
                    className="w-full bg-gradient-to-t from-indigo-600 to-purple-500 rounded-t transition-all hover:from-indigo-700 hover:to-purple-600"
                    style={{ 
                      height: `${(day.study_minutes / maxStudyMinutes) * 200}px`,
                      minHeight: day.study_minutes > 0 ? '20px' : '0px'
                    }}
                    title={`${day.study_minutes} minutes`}
                  ></div>
                  <div className="text-xs text-gray-700 font-medium whitespace-nowrap">
                    {new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Session Count Chart */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Session Count by Day</h2>
          <div className="overflow-x-auto">
            <div className="flex items-end gap-2 min-w-max h-48">
              {dailyActivity.map((day) => (
                <div key={day.date} className="flex flex-col items-center gap-2 flex-1 min-w-[40px]">
                  <div className="text-xs text-gray-700 font-medium">
                    {day.session_count}
                  </div>
                  <div
                    className="w-full bg-gradient-to-t from-blue-600 to-cyan-500 rounded-t transition-all hover:from-blue-700 hover:to-cyan-600"
                    style={{ 
                      height: `${(day.session_count / maxSessions) * 150}px`,
                      minHeight: day.session_count > 0 ? '20px' : '0px'
                    }}
                    title={`${day.session_count} sessions`}
                  ></div>
                  <div className="text-xs text-gray-700 font-medium whitespace-nowrap">
                    {new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Mood Correlation */}
        {moodTrends.length > 0 && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Mood & Study Correlation</h2>
            <div className="overflow-x-auto">
              <div className="flex gap-3 min-w-max">
                {moodTrends.slice(-14).map((trend) => (
                  <div key={trend.date} className="flex flex-col items-center gap-2 p-2 bg-gray-50 rounded-lg min-w-[100px]">
                    <div className="text-xs text-gray-900 font-medium whitespace-nowrap">
                      {new Date(trend.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </div>
                    <div className="flex flex-col gap-1 w-full">
                      {trend.avg_before_intensity && (
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-700">Before:</span>
                          <div className="flex-1 h-3 bg-gray-200 rounded overflow-hidden">
                            <div
                              className="h-full bg-blue-500"
                              style={{ width: `${(trend.avg_before_intensity / 5) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-xs font-medium text-gray-900">{trend.avg_before_intensity.toFixed(1)}</span>
                        </div>
                      )}
                      {trend.avg_after_intensity && (
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-700">After:</span>
                          <div className="flex-1 h-3 bg-gray-200 rounded overflow-hidden">
                            <div
                              className="h-full bg-green-500"
                              style={{ width: `${(trend.avg_after_intensity / 5) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-xs font-medium text-gray-900">{trend.avg_after_intensity.toFixed(1)}</span>
                        </div>
                      )}
                    </div>
                    <div className="text-sm text-gray-700 font-medium">
                      {trend.session_count} {trend.session_count === 1 ? 'session' : 'sessions'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Weekly Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">This Week</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Study Time</span>
                <span className="font-bold text-indigo-600">
                  {Math.round(
                    dailyActivity
                      .slice(-7)
                      .reduce((sum, d) => sum + d.study_minutes, 0) / 60
                  )}h
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Sessions</span>
                <span className="font-bold text-purple-600">
                  {dailyActivity.slice(-7).reduce((sum, d) => sum + d.session_count, 0)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Avg/Day</span>
                <span className="font-bold text-blue-600">
                  {Math.round(
                    dailyActivity
                      .slice(-7)
                      .reduce((sum, d) => sum + d.study_minutes, 0) / 7
                  )}m
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Last Week</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Study Time</span>
                <span className="font-bold text-indigo-600">
                  {Math.round(
                    dailyActivity
                      .slice(-14, -7)
                      .reduce((sum, d) => sum + d.study_minutes, 0) / 60
                  )}h
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Sessions</span>
                <span className="font-bold text-purple-600">
                  {dailyActivity.slice(-14, -7).reduce((sum, d) => sum + d.session_count, 0)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Avg/Day</span>
                <span className="font-bold text-blue-600">
                  {Math.round(
                    dailyActivity
                      .slice(-14, -7)
                      .reduce((sum, d) => sum + d.study_minutes, 0) / 7
                  )}m
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Growth</h3>
            <div className="space-y-3">
              {(() => {
                const thisWeek = dailyActivity.slice(-7).reduce((sum, d) => sum + d.study_minutes, 0);
                const lastWeek = dailyActivity.slice(-14, -7).reduce((sum, d) => sum + d.study_minutes, 0);
                const growth = lastWeek > 0 ? ((thisWeek - lastWeek) / lastWeek) * 100 : 0;
                const isPositive = growth >= 0;
                
                return (
                  <>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-700">vs Last Week</span>
                      <span className={`font-bold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                        {isPositive ? '+' : ''}{growth.toFixed(0)}%
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-700">Trend</span>
                      <span className="text-2xl">
                        {isPositive ? '📈' : '📉'}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-700">Status</span>
                      <span className={`font-bold ${isPositive ? 'text-green-600' : 'text-orange-600'}`}>
                        {isPositive ? 'Improving' : 'Needs Boost'}
                      </span>
                    </div>
                  </>
                );
              })()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/app/contexts/AuthContext';
import { useTheme } from '@/app/contexts/ThemeContext';
import { authAPI, analyticsAPI, studySessionsAPI, moodAPI } from '@/lib/api';

interface UserStats {
  total_study_time: number;
  session_count: number;
  subject_distribution: { [key: string]: number };
}

interface DailyActivity {
  date: string;
  study_minutes: number;
  session_count: number;
}

interface MoodTrend {
  date: string;
  avg_before_intensity: number | null;
  avg_after_intensity: number | null;
  most_common_mood: string | null;
  session_count: number;
}

export default function ProfilePage() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const { isDarkMode, toggleDarkMode } = useTheme();
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [changePassword, setChangePassword] = useState(false);
  const [dailyActivity, setDailyActivity] = useState<DailyActivity[]>([]);
  const [moodTrends, setMoodTrends] = useState<MoodTrend[]>([]);
  const [currentStreak, setCurrentStreak] = useState(0);
  const [longestStreak, setLongestStreak] = useState(0);
  const [timeRange, setTimeRange] = useState<7 | 30 | 90>(30);
  
  // Profile form
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  
  // Password form
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setEmail(user.email || '');
      setUsername(user.email || ''); // Username is email
      loadStats();
    }
  }, [user]);

  const loadStats = async () => {
    try {
      const [statsData, analyticsData, sessions, moods] = await Promise.all([
        authAPI.getStats(),
        analyticsAPI.getDashboard(timeRange),
        studySessionsAPI.list(),
        moodAPI.getTrends(timeRange),
      ]);
      setStats(statsData);
      setDailyActivity(analyticsData.daily_activity || []);
      setMoodTrends(moods);
      calculateStreaks(analyticsData.daily_activity || []);
    } catch (error) {
      console.error('Error loading stats:', error);
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

    let longest = 0;
    let tempStreak = 0;

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
    let current = 0;
    for (let i = sortedActivities.length - 1; i >= 0; i--) {
      if (sortedActivities[i].study_minutes > 0) {
        current++;
      } else {
        break;
      }
    }

    setCurrentStreak(current);
    setLongestStreak(longest);
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSuccessMessage('');
    setErrorMessage('');

    try {
      await authAPI.updateProfile({
        full_name: fullName,
        email: email,
      });
      setSuccessMessage('Profile updated successfully!');
      setEditMode(false);
      
      // Refresh user data
      window.location.reload();
    } catch (error: any) {
      setErrorMessage(error.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSuccessMessage('');
    setErrorMessage('');

    if (newPassword !== confirmPassword) {
      setErrorMessage('Passwords do not match');
      setLoading(false);
      return;
    }

    if (newPassword.length < 6) {
      setErrorMessage('Password must be at least 6 characters');
      setLoading(false);
      return;
    }

    try {
      await authAPI.updateProfile({
        password: newPassword,
      });
      setSuccessMessage('Password changed successfully!');
      setChangePassword(false);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (error: any) {
      setErrorMessage(error.response?.data?.detail || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      alert('Account deletion feature coming soon!');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Profile & Settings ⚙️</h1>
          <p className="text-gray-700 dark:text-gray-300">Manage your account and preferences</p>
        </div>

        {/* Success/Error Messages */}
        {successMessage && (
          <div className="mb-6 bg-green-100 dark:bg-green-900 border border-green-400 dark:border-green-600 text-green-800 dark:text-green-200 px-4 py-3 rounded-lg">
            {successMessage}
          </div>
        )}
        {errorMessage && (
          <div className="mb-6 bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-600 text-red-800 dark:text-red-200 px-4 py-3 rounded-lg">
            {errorMessage}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Profile Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* Profile Card */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Profile Information</h2>
                {!editMode && (
                  <button
                    onClick={() => setEditMode(true)}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
                  >
                    Edit Profile
                  </button>
                )}
              </div>

              {editMode ? (
                <form onSubmit={handleUpdateProfile} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-900 dark:text-gray-200 mb-2">Full Name</label>
                    <input
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-gray-900 dark:text-white dark:bg-gray-700"
                      placeholder="Your full name"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-900 dark:text-gray-200 mb-2">Email</label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-gray-900 dark:text-white dark:bg-gray-700"
                      placeholder="your.email@example.com"
                    />
                  </div>

                  <div className="flex gap-3 pt-4">
                    <button
                      type="submit"
                      disabled={loading}
                      className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
                    >
                      {loading ? 'Saving...' : 'Save Changes'}
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setEditMode(false);
                        setFullName(user?.full_name || '');
                        setEmail(user?.email || '');
                      }}
                      className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              ) : (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Full Name</label>
                    <p className="text-lg text-gray-900 dark:text-white">{user?.full_name || 'Not set'}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Email</label>
                    <p className="text-lg text-gray-900 dark:text-white">{user?.email}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Account Status</label>
                    <span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                      Active
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Security Card */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Security</h2>

              {!changePassword ? (
                <button
                  onClick={() => setChangePassword(true)}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
                >
                  Change Password
                </button>
              ) : (
                <form onSubmit={handleChangePassword} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-900 dark:text-gray-200 mb-2">New Password</label>
                    <input
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 dark:text-white dark:bg-gray-700"
                      placeholder="Enter new password"
                      minLength={6}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-900 dark:text-gray-200 mb-2">Confirm New Password</label>
                    <input
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-gray-900 dark:text-white dark:bg-gray-700"
                      placeholder="Confirm new password"
                      minLength={6}
                    />
                  </div>

                  <div className="flex gap-3 pt-4">
                    <button
                      type="submit"
                      disabled={loading}
                      className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:opacity-50"
                    >
                      {loading ? 'Changing...' : 'Change Password'}
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setChangePassword(false);
                        setNewPassword('');
                        setConfirmPassword('');
                      }}
                      className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              )}
            </div>

            {/* Danger Zone */}
            <div className="bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold text-red-900 dark:text-red-400 mb-4">Danger Zone</h2>
              <p className="text-red-700 dark:text-red-300 mb-4">
                Once you delete your account, there is no going back. Please be certain.
              </p>
              <button
                onClick={handleDeleteAccount}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
              >
                Delete Account
              </button>
            </div>

            {/* Progress Charts */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Progress Dashboard 📊</h2>
                <div className="flex gap-2">
                  {[7, 30, 90].map((days) => (
                    <button
                      key={days}
                      onClick={() => {
                        setTimeRange(days as 7 | 30 | 90);
                        loadStats();
                      }}
                      className={`px-3 py-1 rounded-lg text-sm font-medium transition ${
                        timeRange === days
                          ? 'bg-indigo-600 text-white shadow-md'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                      }`}
                    >
                      {days}d
                    </button>
                  ))}
                </div>
              </div>

              {/* Streaks */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div className="bg-gradient-to-br from-orange-400 to-red-500 rounded-xl p-4 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-xs font-medium mb-1 opacity-90">Current Streak</div>
                      <div className="text-4xl font-bold">{currentStreak}</div>
                      <div className="text-xs mt-1 opacity-90">
                        {currentStreak === 1 ? 'day' : 'days'} in a row 🔥
                      </div>
                    </div>
                    <div className="text-5xl">🔥</div>
                  </div>
                </div>
                <div className="bg-gradient-to-br from-yellow-400 to-orange-500 rounded-xl p-4 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-xs font-medium mb-1 opacity-90">Longest Streak</div>
                      <div className="text-4xl font-bold">{longestStreak}</div>
                      <div className="text-xs mt-1 opacity-90">
                        {longestStreak === 1 ? 'day' : 'days'} personal best 🏆
                      </div>
                    </div>
                    <div className="text-5xl">🏆</div>
                  </div>
                </div>
              </div>

              {/* Daily Study Time Chart */}
              {dailyActivity.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-3">Daily Study Time</h3>
                  <div className="overflow-x-auto">
                    <div className="flex items-end gap-1 min-w-max h-48">
                      {dailyActivity.map((day) => {
                        const maxStudyMinutes = Math.max(...dailyActivity.map(d => d.study_minutes), 1);
                        return (
                          <div key={day.date} className="flex flex-col items-center gap-1 flex-1 min-w-[30px]">
                            <div className="text-[10px] text-gray-700 dark:text-gray-300 font-medium">
                              {day.study_minutes}m
                            </div>
                            <div
                              className="w-full bg-gradient-to-t from-indigo-600 to-purple-500 rounded-t transition-all hover:from-indigo-700 hover:to-purple-600"
                              style={{ 
                                height: `${(day.study_minutes / maxStudyMinutes) * 150}px`,
                                minHeight: day.study_minutes > 0 ? '15px' : '0px'
                              }}
                              title={`${day.study_minutes} minutes`}
                            ></div>
                            <div className="text-[9px] text-gray-700 font-medium whitespace-nowrap rotate-45 origin-left mt-2">
                              {new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}

              {/* Session Count Chart */}
              {dailyActivity.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-3">Session Count by Day</h3>
                  <div className="overflow-x-auto">
                    <div className="flex items-end gap-1 min-w-max h-40">
                      {dailyActivity.map((day) => {
                        const maxSessions = Math.max(...dailyActivity.map(d => d.session_count), 1);
                        return (
                          <div key={day.date} className="flex flex-col items-center gap-1 flex-1 min-w-[30px]">
                            <div className="text-[10px] text-gray-700 dark:text-gray-300 font-medium">
                              {day.session_count}
                            </div>
                            <div
                              className="w-full bg-gradient-to-t from-blue-600 to-cyan-500 rounded-t transition-all hover:from-blue-700 hover:to-cyan-600"
                              style={{ 
                                height: `${(day.session_count / maxSessions) * 120}px`,
                                minHeight: day.session_count > 0 ? '15px' : '0px'
                              }}
                              title={`${day.session_count} sessions`}
                            ></div>
                            <div className="text-[9px] text-gray-700 dark:text-gray-300 font-medium whitespace-nowrap rotate-45 origin-left mt-2">
                              {new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}

              {/* Mood Correlation */}
              {moodTrends.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-3">Mood & Study Correlation</h3>
                  <div className="overflow-x-auto">
                    <div className="flex gap-2 min-w-max">
                      {moodTrends.slice(-14).map((trend) => (
                        <div key={trend.date} className="flex flex-col items-center gap-2 p-2 bg-gray-50 dark:bg-gray-700 rounded-lg min-w-[90px]">
                          <div className="text-[10px] text-gray-900 dark:text-gray-100 font-medium whitespace-nowrap">
                            {new Date(trend.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                          </div>
                          <div className="flex flex-col gap-1 w-full">
                            {trend.avg_before_intensity && (
                              <div className="flex items-center gap-1">
                                <span className="text-[9px] text-gray-700 dark:text-gray-300">Before:</span>
                                <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-600 rounded overflow-hidden">
                                  <div
                                    className="h-full bg-blue-500"
                                    style={{ width: `${(trend.avg_before_intensity / 5) * 100}%` }}
                                  ></div>
                                </div>
                                <span className="text-[9px] font-medium text-gray-900 dark:text-gray-100">{trend.avg_before_intensity.toFixed(1)}</span>
                              </div>
                            )}
                            {trend.avg_after_intensity && (
                              <div className="flex items-center gap-1">
                                <span className="text-[9px] text-gray-700 dark:text-gray-300">After:</span>
                                <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-600 rounded overflow-hidden">
                                  <div
                                    className="h-full bg-green-500"
                                    style={{ width: `${(trend.avg_after_intensity / 5) * 100}%` }}
                                  ></div>
                                </div>
                                <span className="text-[9px] font-medium text-gray-900 dark:text-gray-100">{trend.avg_after_intensity.toFixed(1)}</span>
                              </div>
                            )}
                          </div>
                          <div className="text-[10px] text-gray-700 dark:text-gray-300 font-medium">
                            {trend.session_count} {trend.session_count === 1 ? 'session' : 'sessions'}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Weekly Summary */}
              {dailyActivity.length >= 7 && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/30 dark:to-purple-900/30 rounded-lg p-4">
                    <h3 className="text-sm font-bold text-gray-900 dark:text-white mb-3">This Week</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-gray-700 dark:text-gray-300">Study Time</span>
                        <span className="font-bold text-indigo-600 dark:text-indigo-400 text-sm">
                          {Math.round(
                            dailyActivity
                              .slice(-7)
                              .reduce((sum, d) => sum + d.study_minutes, 0) / 60
                          )}h
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-gray-700 dark:text-gray-300">Sessions</span>
                        <span className="font-bold text-purple-600 dark:text-purple-400 text-sm">
                          {dailyActivity.slice(-7).reduce((sum, d) => sum + d.session_count, 0)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-gray-700 dark:text-gray-300">Avg/Day</span>
                        <span className="font-bold text-blue-600 dark:text-blue-400 text-sm">
                          {Math.round(
                            dailyActivity
                              .slice(-7)
                              .reduce((sum, d) => sum + d.study_minutes, 0) / 7
                          )}m
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-900/30 dark:to-cyan-900/30 rounded-lg p-4">
                    <h3 className="text-sm font-bold text-gray-900 dark:text-white mb-3">Last Week</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-gray-700 dark:text-gray-300">Study Time</span>
                        <span className="font-bold text-indigo-600 dark:text-indigo-400 text-sm">
                          {Math.round(
                            dailyActivity
                              .slice(-14, -7)
                              .reduce((sum, d) => sum + d.study_minutes, 0) / 60
                          )}h
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-gray-700 dark:text-gray-300">Sessions</span>
                        <span className="font-bold text-purple-600 dark:text-purple-400 text-sm">
                          {dailyActivity.slice(-14, -7).reduce((sum, d) => sum + d.session_count, 0)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-gray-700 dark:text-gray-300">Avg/Day</span>
                        <span className="font-bold text-blue-600 dark:text-blue-400 text-sm">
                          {Math.round(
                            dailyActivity
                              .slice(-14, -7)
                              .reduce((sum, d) => sum + d.study_minutes, 0) / 7
                          )}m
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/30 dark:to-emerald-900/30 rounded-lg p-4">
                    <h3 className="text-sm font-bold text-gray-900 dark:text-white mb-3">Growth</h3>
                    <div className="space-y-2">
                      {(() => {
                        const thisWeek = dailyActivity.slice(-7).reduce((sum, d) => sum + d.study_minutes, 0);
                        const lastWeek = dailyActivity.slice(-14, -7).reduce((sum, d) => sum + d.study_minutes, 0);
                        const growth = lastWeek > 0 ? ((thisWeek - lastWeek) / lastWeek) * 100 : 0;
                        const isPositive = growth >= 0;
                        
                        return (
                          <>
                            <div className="flex justify-between items-center">
                              <span className="text-xs text-gray-700 dark:text-gray-300">vs Last Week</span>
                              <span className={`font-bold text-sm ${isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                                {isPositive ? '+' : ''}{growth.toFixed(0)}%
                              </span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-xs text-gray-700 dark:text-gray-300">Trend</span>
                              <span className="text-xl">
                                {isPositive ? '📈' : '📉'}
                              </span>
                            </div>
                            <div className="flex justify-between items-center">
                              <span className="text-xs text-gray-700 dark:text-gray-300">Status</span>
                              <span className={`font-bold text-xs ${isPositive ? 'text-green-600 dark:text-green-400' : 'text-orange-600 dark:text-orange-400'}`}>
                                {isPositive ? 'Improving' : 'Needs Boost'}
                              </span>
                            </div>
                          </>
                        );
                      })()}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Stats & Quick Actions */}
          <div className="space-y-6">
            {/* Stats Card */}
            {stats && (
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Your Stats</h3>
                <div className="space-y-4">
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Study Time</div>
                    <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                      {Math.round(stats.total_study_time / 60)}h {stats.total_study_time % 60}m
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Sessions</div>
                    <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">{stats.session_count}</div>
                  </div>
                  {Object.keys(stats.subject_distribution).length > 0 && (
                    <div>
                      <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">Top Subjects</div>
                      <div className="space-y-2">
                        {Object.entries(stats.subject_distribution)
                          .sort(([, a], [, b]) => b - a)
                          .slice(0, 3)
                          .map(([subject, minutes]) => (
                            <div key={subject} className="flex justify-between text-sm">
                              <span className="text-gray-900 dark:text-gray-100">{subject}</span>
                              <span className="text-gray-600 dark:text-gray-400">{minutes}m</span>
                            </div>
                          ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <button
                  onClick={() => router.push('/dashboard')}
                  className="w-full px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-lg hover:from-indigo-600 hover:to-purple-600 transition"
                >
                  Go to Dashboard
                </button>
                <button
                  onClick={() => router.push('/documents')}
                  className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
                >
                  My Documents
                </button>
                <button
                  onClick={() => router.push('/analytics')}
                  className="w-full px-4 py-2 bg-pink-500 text-white rounded-lg hover:bg-pink-600 transition"
                >
                  View Analytics
                </button>
                <button
                  onClick={logout}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition"
                >
                  Logout
                </button>
              </div>
            </div>

            {/* Preferences (Placeholder) */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Preferences</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700 dark:text-gray-300">Email Notifications</span>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" defaultChecked />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                  </label>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700 dark:text-gray-300">Study Reminders</span>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                  </label>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700 dark:text-gray-300">Dark Mode</span>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input 
                      type="checkbox" 
                      className="sr-only peer" 
                      checked={isDarkMode}
                      onChange={toggleDarkMode}
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

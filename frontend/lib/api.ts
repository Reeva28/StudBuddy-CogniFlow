import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await axios.post(`${API_URL}/api/v1/auth/token`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  register: async (email: string, username: string, password: string, fullName?: string) => {
    const response = await api.post('/api/v1/auth/register', {
      email,
      username,
      password,
      full_name: fullName,
    });
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/v1/users/me');
    return response.data;
  },

  updateProfile: async (data: {
    email?: string;
    username?: string;
    full_name?: string;
    password?: string;
  }) => {
    const response = await api.put('/api/v1/users/me', data);
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/api/v1/users/me/stats');
    return response.data;
  },
};

// Documents API
export const documentsAPI = {
  list: async () => {
    const response = await api.get('/api/v1/documents/');
    return response.data;
  },

  upload: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/v1/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getSummary: async (documentId: number) => {
    const response = await api.get(`/api/v1/documents/${documentId}/summary`);
    return response.data;
  },

  delete: async (documentId: number) => {
    const response = await api.delete(`/api/v1/documents/${documentId}`);
    return response.data;
  },
};

// Study Plans API
export const studyPlansAPI = {
  list: async () => {
    const response = await api.get('/api/v1/study-plans/');
    return response.data;
  },

  create: async (data: {
    goal: string;
    subject: string;
    duration_minutes: number;
    difficulty_level?: number;
  }) => {
    const response = await api.post('/api/v1/study-plans/', data);
    return response.data;
  },

  get: async (planId: number) => {
    const response = await api.get(`/api/v1/study-plans/${planId}`);
    return response.data;
  },
};

// Study Sessions API
export const studySessionsAPI = {
  list: async () => {
    const response = await api.get('/api/v1/study-sessions/');
    return response.data;
  },

  create: async (data: { plan_id?: number; duration_minutes: number }) => {
    const response = await api.post('/api/v1/study-sessions/', data);
    return response.data;
  },

  complete: async (sessionId: number, data: { notes?: string; rating?: number }) => {
    const response = await api.put(`/api/v1/study-sessions/${sessionId}/complete`, data);
    return response.data;
  },

  get: async (sessionId: number) => {
    const response = await api.get(`/api/v1/study-sessions/${sessionId}`);
    return response.data;
  },
};

// Notes API
export const notesAPI = {
  list: async (params?: { session_id?: number; note_type?: string }) => {
    const response = await api.get('/api/v1/notes/', { params });
    return response.data;
  },

  create: async (data: { content: string; type?: string; session_id?: number }) => {
    const response = await api.post('/api/v1/notes/', data);
    return response.data;
  },

  get: async (noteId: number) => {
    const response = await api.get(`/api/v1/notes/${noteId}`);
    return response.data;
  },

  update: async (noteId: number, data: { content?: string; type?: string }) => {
    const response = await api.put(`/api/v1/notes/${noteId}`, data);
    return response.data;
  },

  delete: async (noteId: number) => {
    const response = await api.delete(`/api/v1/notes/${noteId}`);
    return response.data;
  },
};
// Analytics API
export const analyticsAPI = {
  getDashboard: async (days: number = 30) => {
    const response = await api.get('/api/v1/analytics/dashboard', {
      params: { days }
    });
    return response.data;
  },

  getSessionStats: async () => {
    const response = await api.get('/api/v1/analytics/sessions');
    return response.data;
  },

  getNoteStats: async () => {
    const response = await api.get('/api/v1/analytics/notes');
    return response.data;
  },

  getProductivityStats: async () => {
    const response = await api.get('/api/v1/analytics/productivity');
    return response.data;
  },

  getRecentSessions: async (limit: number = 10) => {
    const response = await api.get('/api/v1/analytics/recent-sessions', {
      params: { limit }
    });
    return response.data;
  },

  getTimeDistribution: async () => {
    const response = await api.get('/api/v1/analytics/time-distribution');
    return response.data;
  },

  getDailyActivity: async (days: number = 30) => {
    const response = await api.get('/api/v1/analytics/daily-activity', {
      params: { days }
    });
    return response.data;
  },
};

// Flashcards API
export const flashcardsAPI = {
  generate: async (documentId: number, numCards: number = 10) => {
    const response = await api.post(`/api/v1/flashcards/generate/${documentId}`, null, {
      params: { num_cards: numCards }
    });
    return response.data;
  },

  getAll: async () => {
    const response = await api.get('/api/v1/flashcards/');
    return response.data;
  },

  getByDocument: async (documentId: number) => {
    const response = await api.get(`/api/v1/flashcards/document/${documentId}`);
    return response.data;
  },

  getDue: async (limit: number = 20) => {
    const response = await api.get('/api/v1/flashcards/due', {
      params: { limit }
    });
    return response.data;
  },

  get: async (flashcardId: number) => {
    const response = await api.get(`/api/v1/flashcards/${flashcardId}`);
    return response.data;
  },

  create: async (data: { document_id: number; question: string; answer: string; difficulty?: number }) => {
    const response = await api.post('/api/v1/flashcards/', data);
    return response.data;
  },

  update: async (flashcardId: number, data: { question?: string; answer?: string; difficulty?: number }) => {
    const response = await api.put(`/api/v1/flashcards/${flashcardId}`, data);
    return response.data;
  },

  review: async (flashcardId: number, quality: number) => {
    const response = await api.post(`/api/v1/flashcards/${flashcardId}/review`, null, {
      params: { quality }
    });
    return response.data;
  },

  delete: async (flashcardId: number) => {
    const response = await api.delete(`/api/v1/flashcards/${flashcardId}`);
    return response.data;
  },
};

// Concept Map API
export const conceptMapAPI = {
  generate: async (documentId: number, maxConcepts: number = 20, regenerate: boolean = false) => {
    const response = await api.post(`/api/v1/concept-map/generate/${documentId}`, {
      max_concepts: maxConcepts,
      include_relationships: true
    }, {
      params: { regenerate }
    });
    return response.data;
  },

  get: async (documentId: number) => {
    const response = await api.get(`/api/v1/concept-map/${documentId}`);
    return response.data;
  },

  delete: async (documentId: number) => {
    const response = await api.delete(`/api/v1/concept-map/${documentId}`);
    return response.data;
  },
};

// Mood API
export const moodAPI = {
  create: async (data: {
    mood_type: string;
    intensity: number;
    is_before_session: boolean;
    study_session_id?: number;
    notes?: string;
  }) => {
    const response = await api.post('/api/v1/mood', data);
    return response.data;
  },

  getAll: async (skip: number = 0, limit: number = 100) => {
    const response = await api.get('/api/v1/mood', {
      params: { skip, limit }
    });
    return response.data;
  },

  getSessionMoods: async (sessionId: number) => {
    const response = await api.get(`/api/v1/mood/session/${sessionId}`);
    return response.data;
  },

  getTrends: async (days: number = 30) => {
    const response = await api.get('/api/v1/mood/trends', {
      params: { days }
    });
    return response.data;
  },

  getStats: async (days: number = 30) => {
    const response = await api.get('/api/v1/mood/stats', {
      params: { days }
    });
    return response.data;
  },

  get: async (moodId: number) => {
    const response = await api.get(`/api/v1/mood/${moodId}`);
    return response.data;
  },

  update: async (moodId: number, data: {
    mood_type?: string;
    intensity?: number;
    notes?: string;
  }) => {
    const response = await api.put(`/api/v1/mood/${moodId}`, data);
    return response.data;
  },

  delete: async (moodId: number) => {
    const response = await api.delete(`/api/v1/mood/${moodId}`);
    return response.data;
  },
};

export default api;

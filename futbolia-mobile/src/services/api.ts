/**
 * FutbolIA API Service
 * Handles all communication with the backend
 */
import AsyncStorage from '@react-native-async-storage/async-storage';

// API Configuration
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api/v1'
  : 'https://api.futbolia.com/api/v1';

const TOKEN_KEY = '@futbolia_token';

// Types
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

interface User {
  id: string;
  email: string;
  username: string;
  language: string;
  theme: string;
  created_at: string;
}

interface AuthResponse {
  user: User;
  access_token: string;
  token_type: string;
}

interface PredictionResult {
  winner: string;
  predicted_score: string;
  confidence: number;
  reasoning: string;
  key_factors: string[];
  star_player_home: string;
  star_player_away: string;
}

interface Team {
  id: string;
  name: string;
  short_name: string;
  logo_url: string;
  form: string;
}

interface Match {
  id: string;
  home_team: Team;
  away_team: Team;
  date: string;
  venue: string;
  league: string;
  status: string;
}

interface Prediction {
  id: string;
  user_id: string;
  match: Match;
  result: PredictionResult;
  created_at: string;
  is_correct: boolean | null;
  language: string;
}

interface PredictionStats {
  total_predictions: number;
  correct_predictions: number;
  accuracy: number;
}

// Token Management
export const getToken = async (): Promise<string | null> => {
  try {
    return await AsyncStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
};

export const setToken = async (token: string): Promise<void> => {
  await AsyncStorage.setItem(TOKEN_KEY, token);
};

export const removeToken = async (): Promise<void> => {
  await AsyncStorage.removeItem(TOKEN_KEY);
};

// API Request Helper
const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> => {
  try {
    const token = await getToken();
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      return {
        success: false,
        error: data.detail || data.error || 'Request failed',
      };
    }
    
    return data;
  } catch (error) {
    console.error('API Error:', error);
    return {
      success: false,
      error: 'Network error. Please check your connection.',
    };
  }
};

// ==================== AUTH API ====================

export const authApi = {
  register: async (email: string, username: string, password: string, language: string = 'es') => {
    const response = await apiRequest<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, username, password, language }),
    });
    
    if (response.success && response.data?.access_token) {
      await setToken(response.data.access_token);
    }
    
    return response;
  },
  
  login: async (email: string, password: string, language: string = 'es') => {
    const response = await apiRequest<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password, language }),
    });
    
    if (response.success && response.data?.access_token) {
      await setToken(response.data.access_token);
    }
    
    return response;
  },
  
  logout: async () => {
    await removeToken();
    return { success: true };
  },
  
  getProfile: async () => {
    return apiRequest<{ user: User }>('/auth/me');
  },
  
  updatePreferences: async (language?: string, theme?: string) => {
    return apiRequest<{ user: User }>('/auth/preferences', {
      method: 'PUT',
      body: JSON.stringify({ language, theme }),
    });
  },
};

// ==================== PREDICTIONS API ====================

export const predictionsApi = {
  predict: async (homeTeam: string, awayTeam: string, language: string = 'es') => {
    return apiRequest<{ prediction: Prediction; context: any }>('/predictions/predict', {
      method: 'POST',
      body: JSON.stringify({ 
        home_team: homeTeam, 
        away_team: awayTeam,
        language,
      }),
    });
  },
  
  getHistory: async (limit: number = 20) => {
    return apiRequest<{ predictions: Prediction[]; stats: PredictionStats }>(
      `/predictions/history?limit=${limit}`
    );
  },
  
  getUpcomingMatches: async (leagueId: number = 39) => {
    return apiRequest<{ matches: Match[] }>(
      `/predictions/matches?league_id=${leagueId}`
    );
  },
  
  compareTeams: async (teamA: string, teamB: string) => {
    return apiRequest<any>('/predictions/compare', {
      method: 'POST',
      body: JSON.stringify({ team_a: teamA, team_b: teamB }),
    });
  },
  
  getAvailableTeams: async () => {
    return apiRequest<{ teams: { name: string; player_count: number }[] }>(
      '/predictions/teams'
    );
  },
};

// Export types
export type { 
  User, 
  AuthResponse, 
  PredictionResult, 
  Team, 
  Match, 
  Prediction,
  PredictionStats,
  ApiResponse,
};

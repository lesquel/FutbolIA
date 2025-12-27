/**
 * FutbolIA API Service
 * Handles all communication with the backend
 */
import AsyncStorage from "@react-native-async-storage/async-storage";

// API Configuration
const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL || "https://futbolia.onrender.com/api/v1";

const TOKEN_KEY = "@futbolia_token";

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
  match_preview?: string;
  tactical_insight?: string;
}

// Player data for detailed analytics
interface Player {
  name: string;
  position: string;
  overall_rating: number;
  pace: number;
  shooting: number;
  passing: number;
  dribbling: number;
  defending: number;
  physical: number;
}

// Analytics context returned with prediction
interface PredictionContext {
  home_players: Player[];
  away_players: Player[];
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
  context?: PredictionContext;
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

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    // Merge with existing headers
    if (options.headers) {
      const existingHeaders = options.headers as Record<string, string>;
      Object.assign(headers, existingHeaders);
    }

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const url = `${API_BASE_URL}${endpoint}`;
    console.log(`🚀 API Request: ${url}`);

    const response = await fetch(url, {
      ...options,
      headers,
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        success: false,
        error: data.detail || data.error || "Request failed",
      };
    }

    return data;
  } catch (error: any) {
    console.error("🚀 API Error Details:", {
      message: error.message,
      url: `${API_BASE_URL}${endpoint}`,
      stack: error.stack,
    });

    return {
      success: false,
      error: `Error de conexión: ${error.message}. Verifique que el servidor en ${API_BASE_URL} sea accesible.`,
    };
  }
};

// ==================== AUTH API ====================

export const authApi = {
  register: async (
    email: string,
    username: string,
    password: string,
    language: string = "es"
  ) => {
    const response = await apiRequest<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, username, password, language }),
    });

    if (response.success && response.data?.access_token) {
      await setToken(response.data.access_token);
    }

    return response;
  },

  login: async (email: string, password: string, language: string = "es") => {
    const response = await apiRequest<AuthResponse>("/auth/login", {
      method: "POST",
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
    return apiRequest<{ user: User }>("/auth/me");
  },

  updatePreferences: async (language?: string, theme?: string) => {
    return apiRequest<{ user: User }>("/auth/preferences", {
      method: "PUT",
      body: JSON.stringify({ language, theme }),
    });
  },
};

// ==================== PREDICTIONS API ====================

export const predictionsApi = {
  predict: async (
    homeTeam: string,
    awayTeam: string,
    language: string = "es"
  ) => {
    return apiRequest<{ prediction: Prediction; context: any }>(
      "/predictions/predict",
      {
        method: "POST",
        body: JSON.stringify({
          home_team: homeTeam,
          away_team: awayTeam,
          language,
        }),
      }
    );
  },

  getHistory: async (limit: number = 20) => {
    return apiRequest<{ predictions: Prediction[]; stats: PredictionStats }>(
      `/predictions/history?limit=${limit}`
    );
  },

  getPredictionDetail: async (id: string) => {
    return apiRequest<Prediction>(`/predictions/${id}`);
  },

  getUpcomingMatches: async (leagueId: number = 39) => {
    return apiRequest<{ matches: Match[] }>(
      `/predictions/matches?league_id=${leagueId}`
    );
  },

  compareTeams: async (teamA: string, teamB: string) => {
    return apiRequest<any>("/predictions/compare", {
      method: "POST",
      body: JSON.stringify({ team_a: teamA, team_b: teamB }),
    });
  },

  getAvailableTeams: async () => {
    return apiRequest<{ teams: { name: string; player_count: number }[] }>(
      "/predictions/teams"
    );
  },
};

// ==================== TEAMS API ====================

interface TeamSearchResult {
  id: string;
  name: string;
  short_name: string;
  logo_url: string;
  country: string;
  league: string;
  has_players: boolean;
  player_count: number;
  source?: string;
}

interface PlayerCreate {
  name: string;
  position?: string;
  overall_rating?: number;
  pace?: number;
  shooting?: number;
  passing?: number;
  dribbling?: number;
  defending?: number;
  physical?: number;
}

interface TeamCreate {
  name: string;
  short_name?: string;
  logo_url?: string;
  country?: string;
  league?: string;
  players?: PlayerCreate[];
}

export const teamsApi = {
  // Search teams (local DB + API)
  search: async (
    query: string,
    searchApi: boolean = true,
    limit: number = 20
  ) => {
    return apiRequest<{ teams: TeamSearchResult[]; total: number }>(
      `/teams/search?q=${encodeURIComponent(
        query
      )}&search_api=${searchApi}&limit=${limit}`
    );
  },

  // Get teams that have player data
  getTeamsWithPlayers: async () => {
    return apiRequest<{ teams: TeamSearchResult[]; total: number }>(
      "/teams/with-players"
    );
  },

  // Add a new team
  addTeam: async (team: TeamCreate) => {
    return apiRequest<{ team: any; players_added: number }>("/teams/add", {
      method: "POST",
      body: JSON.stringify(team),
    });
  },

  // Add players to a team
  addPlayersToTeam: async (teamName: string, players: PlayerCreate[]) => {
    return apiRequest<{
      team: string;
      players_added: number;
      total_players: number;
    }>(`/teams/add-players/${encodeURIComponent(teamName)}`, {
      method: "POST",
      body: JSON.stringify(players),
    });
  },

  // Bulk add teams
  bulkAddTeams: async (teams: TeamCreate[]) => {
    return apiRequest<{ teams_created: number; players_added: number }>(
      "/teams/bulk-add",
      {
        method: "POST",
        body: JSON.stringify({ teams }),
      }
    );
  },

  // Get players for a team (with stats)
  getTeamPlayers: async (teamName: string) => {
    return apiRequest<{
      team: string;
      players: Player[];
      count: number;
      stats: {
        overall: number;
        pace: number;
        shooting: number;
        passing: number;
        defending: number;
        physical: number;
      } | null;
    }>(`/teams/${encodeURIComponent(teamName)}/players`);
  },

  // Auto-generate players for a team
  generatePlayers: async (
    teamName: string,
    count: number = 11,
    avgRating: number = 75
  ) => {
    return apiRequest<{
      team: string;
      players_generated: number;
      avg_rating: number;
      players: any[];
    }>(
      `/teams/generate-players/${encodeURIComponent(
        teamName
      )}?count=${count}&avg_rating=${avgRating}`,
      {
        method: "POST",
      }
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
  TeamSearchResult,
  PlayerCreate,
  TeamCreate,
  Player,
  PredictionContext,
};

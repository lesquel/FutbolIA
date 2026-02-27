/**
 * FutbolIA Offline Storage Service
 * Handles local caching and offline mode functionality
 *
 * Features:
 * - Cache favorite teams
 * - Store recent predictions offline
 * - Queue predictions for when back online
 * - Team suggestions caching
 */
import AsyncStorage from '@react-native-async-storage/async-storage';

// Storage Keys
const STORAGE_KEYS = {
  FAVORITE_TEAMS: '@futbolia_favorite_teams',
  RECENT_PREDICTIONS: '@futbolia_recent_predictions',
  PENDING_PREDICTIONS: '@futbolia_pending_predictions',
  TEAM_CACHE: '@futbolia_team_cache',
  LAST_SYNC: '@futbolia_last_sync',
  OFFLINE_MODE: '@futbolia_offline_mode',
} as const;

// Types
export interface CachedTeam {
  id: string;
  name: string;
  shortName: string;
  logoUrl: string;
  country?: string;
  league?: string;
  playerCount?: number;
  cachedAt: number; // timestamp
}

export interface CachedPrediction {
  id: string;
  homeTeam: string;
  awayTeam: string;
  winner: string;
  confidence: number;
  reasoning: string;
  keyFactors: string[];
  createdAt: string;
  cachedAt: number;
}

export interface PendingPrediction {
  id: string;
  homeTeam: string;
  awayTeam: string;
  requestedAt: number;
  language: string;
}

// Cache duration in milliseconds (24 hours)
const CACHE_DURATION = 24 * 60 * 60 * 1000;

// ==================== Favorite Teams ====================

/**
 * Get all favorite teams
 */
export const getFavoriteTeams = async (): Promise<CachedTeam[]> => {
  try {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.FAVORITE_TEAMS);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Error reading favorite teams:', error);
    return [];
  }
};

/**
 * Add a team to favorites
 */
export const addFavoriteTeam = async (team: Omit<CachedTeam, 'cachedAt'>): Promise<void> => {
  try {
    const favorites = await getFavoriteTeams();

    // Check if already exists
    if (favorites.some((t) => t.name.toLowerCase() === team.name.toLowerCase())) {
      return;
    }

    const newFavorite: CachedTeam = {
      ...team,
      cachedAt: Date.now(),
    };

    favorites.push(newFavorite);
    await AsyncStorage.setItem(STORAGE_KEYS.FAVORITE_TEAMS, JSON.stringify(favorites));
  } catch (error) {
    console.error('Error adding favorite team:', error);
    throw error;
  }
};

/**
 * Remove a team from favorites
 */
export const removeFavoriteTeam = async (teamName: string): Promise<void> => {
  try {
    const favorites = await getFavoriteTeams();
    const updated = favorites.filter((t) => t.name.toLowerCase() !== teamName.toLowerCase());
    await AsyncStorage.setItem(STORAGE_KEYS.FAVORITE_TEAMS, JSON.stringify(updated));
  } catch (error) {
    console.error('Error removing favorite team:', error);
    throw error;
  }
};

/**
 * Check if a team is favorite
 */
export const isTeamFavorite = async (teamName: string): Promise<boolean> => {
  const favorites = await getFavoriteTeams();
  return favorites.some((t) => t.name.toLowerCase() === teamName.toLowerCase());
};

// ==================== Recent Predictions Cache ====================

/**
 * Get cached predictions
 */
export const getCachedPredictions = async (limit: number = 20): Promise<CachedPrediction[]> => {
  try {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.RECENT_PREDICTIONS);
    if (!data) return [];

    const predictions: CachedPrediction[] = JSON.parse(data);

    // Filter out expired predictions
    const now = Date.now();
    const valid = predictions.filter((p) => now - p.cachedAt < CACHE_DURATION);

    return valid.slice(0, limit);
  } catch (error) {
    console.error('Error reading cached predictions:', error);
    return [];
  }
};

/**
 * Cache a new prediction
 */
export const cachePrediction = async (
  prediction: Omit<CachedPrediction, 'cachedAt'>,
): Promise<void> => {
  try {
    const cached = await getCachedPredictions(50);

    // Check if prediction already exists
    const exists = cached.some(
      (p) => p.homeTeam === prediction.homeTeam && p.awayTeam === prediction.awayTeam,
    );

    if (exists) {
      // Update existing prediction
      const updated = cached.map((p) =>
        p.homeTeam === prediction.homeTeam && p.awayTeam === prediction.awayTeam
          ? { ...prediction, cachedAt: Date.now() }
          : p,
      );
      await AsyncStorage.setItem(STORAGE_KEYS.RECENT_PREDICTIONS, JSON.stringify(updated));
    } else {
      // Add new prediction
      const newPrediction: CachedPrediction = {
        ...prediction,
        cachedAt: Date.now(),
      };

      // Keep only last 50 predictions
      const updated = [newPrediction, ...cached].slice(0, 50);
      await AsyncStorage.setItem(STORAGE_KEYS.RECENT_PREDICTIONS, JSON.stringify(updated));
    }
  } catch (error) {
    console.error('Error caching prediction:', error);
  }
};

/**
 * Get a cached prediction for specific teams
 */
export const getCachedPredictionForMatch = async (
  homeTeam: string,
  awayTeam: string,
): Promise<CachedPrediction | null> => {
  const cached = await getCachedPredictions();
  return (
    cached.find(
      (p) =>
        p.homeTeam.toLowerCase() === homeTeam.toLowerCase() &&
        p.awayTeam.toLowerCase() === awayTeam.toLowerCase(),
    ) || null
  );
};

// ==================== Pending Predictions Queue ====================

/**
 * Get pending predictions (to be processed when online)
 */
export const getPendingPredictions = async (): Promise<PendingPrediction[]> => {
  try {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.PENDING_PREDICTIONS);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Error reading pending predictions:', error);
    return [];
  }
};

/**
 * Add a prediction request to the queue
 */
export const queuePrediction = async (
  homeTeam: string,
  awayTeam: string,
  language: string = 'es',
): Promise<string> => {
  try {
    const pending = await getPendingPredictions();

    // Generate a temporary ID
    const id = `pending_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const newRequest: PendingPrediction = {
      id,
      homeTeam,
      awayTeam,
      requestedAt: Date.now(),
      language,
    };

    pending.push(newRequest);
    await AsyncStorage.setItem(STORAGE_KEYS.PENDING_PREDICTIONS, JSON.stringify(pending));

    return id;
  } catch (error) {
    console.error('Error queuing prediction:', error);
    throw error;
  }
};

/**
 * Remove a pending prediction from queue
 */
export const removePendingPrediction = async (id: string): Promise<void> => {
  try {
    const pending = await getPendingPredictions();
    const updated = pending.filter((p) => p.id !== id);
    await AsyncStorage.setItem(STORAGE_KEYS.PENDING_PREDICTIONS, JSON.stringify(updated));
  } catch (error) {
    console.error('Error removing pending prediction:', error);
  }
};

/**
 * Clear all pending predictions
 */
export const clearPendingPredictions = async (): Promise<void> => {
  await AsyncStorage.removeItem(STORAGE_KEYS.PENDING_PREDICTIONS);
};

// ==================== Team Cache ====================

/**
 * Cache team search results
 */
export const cacheTeamSearch = async (query: string, teams: CachedTeam[]): Promise<void> => {
  try {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.TEAM_CACHE);
    const cache: Record<string, { teams: CachedTeam[]; cachedAt: number }> = data
      ? JSON.parse(data)
      : {};

    cache[query.toLowerCase()] = {
      teams,
      cachedAt: Date.now(),
    };

    // Keep only last 100 searches
    const keys = Object.keys(cache);
    if (keys.length > 100) {
      const sorted = keys.sort((a, b) => cache[a].cachedAt - cache[b].cachedAt);
      sorted.slice(0, keys.length - 100).forEach((key) => delete cache[key]);
    }

    await AsyncStorage.setItem(STORAGE_KEYS.TEAM_CACHE, JSON.stringify(cache));
  } catch (error) {
    console.error('Error caching team search:', error);
  }
};

/**
 * Get cached team search results
 */
export const getCachedTeamSearch = async (query: string): Promise<CachedTeam[] | null> => {
  try {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.TEAM_CACHE);
    if (!data) return null;

    const cache: Record<string, { teams: CachedTeam[]; cachedAt: number }> = JSON.parse(data);
    const entry = cache[query.toLowerCase()];

    if (!entry) return null;

    // Check if cache is still valid
    if (Date.now() - entry.cachedAt > CACHE_DURATION) {
      return null;
    }

    return entry.teams;
  } catch (error) {
    console.error('Error reading team cache:', error);
    return null;
  }
};

// ==================== Offline Mode Management ====================

/**
 * Check if offline mode is enabled
 */
export const isOfflineModeEnabled = async (): Promise<boolean> => {
  try {
    const value = await AsyncStorage.getItem(STORAGE_KEYS.OFFLINE_MODE);
    return value === 'true';
  } catch {
    return false;
  }
};

/**
 * Set offline mode
 */
export const setOfflineMode = async (enabled: boolean): Promise<void> => {
  await AsyncStorage.setItem(STORAGE_KEYS.OFFLINE_MODE, enabled.toString());
};

/**
 * Get last sync timestamp
 */
export const getLastSync = async (): Promise<number | null> => {
  try {
    const value = await AsyncStorage.getItem(STORAGE_KEYS.LAST_SYNC);
    return value ? parseInt(value, 10) : null;
  } catch {
    return null;
  }
};

/**
 * Update last sync timestamp
 */
export const updateLastSync = async (): Promise<void> => {
  await AsyncStorage.setItem(STORAGE_KEYS.LAST_SYNC, Date.now().toString());
};

// ==================== Utility Functions ====================

/**
 * Get offline stats summary
 */
export const getOfflineStats = async (): Promise<{
  favoriteTeams: number;
  cachedPredictions: number;
  pendingPredictions: number;
  lastSync: string | null;
}> => {
  const [favorites, predictions, pending, lastSync] = await Promise.all([
    getFavoriteTeams(),
    getCachedPredictions(),
    getPendingPredictions(),
    getLastSync(),
  ]);

  return {
    favoriteTeams: favorites.length,
    cachedPredictions: predictions.length,
    pendingPredictions: pending.length,
    lastSync: lastSync ? new Date(lastSync).toISOString() : null,
  };
};

/**
 * Clear all offline data
 */
export const clearOfflineData = async (): Promise<void> => {
  await Promise.all([
    AsyncStorage.removeItem(STORAGE_KEYS.FAVORITE_TEAMS),
    AsyncStorage.removeItem(STORAGE_KEYS.RECENT_PREDICTIONS),
    AsyncStorage.removeItem(STORAGE_KEYS.PENDING_PREDICTIONS),
    AsyncStorage.removeItem(STORAGE_KEYS.TEAM_CACHE),
    AsyncStorage.removeItem(STORAGE_KEYS.LAST_SYNC),
  ]);
};

/**
 * Export offline data for backup
 */
export const exportOfflineData = async (): Promise<string> => {
  const [favorites, predictions] = await Promise.all([getFavoriteTeams(), getCachedPredictions()]);

  return JSON.stringify(
    {
      version: 1,
      exportedAt: new Date().toISOString(),
      data: {
        favoriteTeams: favorites,
        predictions: predictions,
      },
    },
    null,
    2,
  );
};

/**
 * Import offline data from backup
 */
export const importOfflineData = async (jsonData: string): Promise<boolean> => {
  try {
    const data = JSON.parse(jsonData);

    if (data.version !== 1) {
      throw new Error('Unsupported backup version');
    }

    if (data.data.favoriteTeams) {
      await AsyncStorage.setItem(
        STORAGE_KEYS.FAVORITE_TEAMS,
        JSON.stringify(data.data.favoriteTeams),
      );
    }

    if (data.data.predictions) {
      await AsyncStorage.setItem(
        STORAGE_KEYS.RECENT_PREDICTIONS,
        JSON.stringify(data.data.predictions),
      );
    }

    return true;
  } catch (error) {
    console.error('Error importing offline data:', error);
    return false;
  }
};

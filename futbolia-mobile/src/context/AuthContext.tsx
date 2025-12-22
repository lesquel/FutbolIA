/**
 * FutbolIA - Authentication Context
 * Manages user authentication state across the app
 */
import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useMemo,
  useCallback,
  ReactNode,
} from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { authApi, User, getToken, removeToken } from "@/src/services/api";

// Storage keys
const USER_KEY = "@futbolia_user";
const FAVORITE_TEAMS_KEY = "@futbolia_favorite_teams";

// Favorite team type
export interface FavoriteTeam {
  id: string;
  name: string;
  shortName?: string;
  logoUrl?: string;
  league?: string;
  country?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  favoriteTeams: FavoriteTeam[];
  login: (
    email: string,
    password: string
  ) => Promise<{ success: boolean; error?: string }>;
  register: (
    email: string,
    username: string,
    password: string
  ) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  updateProfile: (
    data: Partial<User>
  ) => Promise<{ success: boolean; error?: string }>;
  addFavoriteTeam: (team: FavoriteTeam) => Promise<void>;
  removeFavoriteTeam: (teamId: string) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  readonly children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [favoriteTeams, setFavoriteTeams] = useState<FavoriteTeam[]>([]);

  // Initialize auth state on app load
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      // Check for existing token
      const token = await getToken();
      if (token) {
        // Try to get user profile
        const response = await authApi.getProfile();
        if (response.success && response.data?.user) {
          setUser(response.data.user);
          await AsyncStorage.setItem(
            USER_KEY,
            JSON.stringify(response.data.user)
          );
        } else {
          // Token invalid, clear it
          await removeToken();
          await AsyncStorage.removeItem(USER_KEY);
        }
      } else {
        // Check for cached user data
        const cachedUser = await AsyncStorage.getItem(USER_KEY);
        if (cachedUser) {
          setUser(JSON.parse(cachedUser));
        }
      }

      // Load favorite teams
      const cachedTeams = await AsyncStorage.getItem(FAVORITE_TEAMS_KEY);
      if (cachedTeams) {
        setFavoriteTeams(JSON.parse(cachedTeams));
      }
    } catch (err) {
      console.error("Auth initialization error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const login = useCallback(async (email: string, password: string) => {
    try {
      const response = await authApi.login(email, password);
      if (response.success && response.data?.user) {
        setUser(response.data.user);
        await AsyncStorage.setItem(
          USER_KEY,
          JSON.stringify(response.data.user)
        );
        return { success: true };
      }
      return { success: false, error: response.error || "Login failed" };
    } catch (err) {
      console.error("Login error:", err);
      return { success: false, error: "Network error" };
    }
  }, []);

  const register = useCallback(
    async (email: string, username: string, password: string) => {
      try {
        const response = await authApi.register(email, username, password);
        if (response.success && response.data?.user) {
          setUser(response.data.user);
          await AsyncStorage.setItem(
            USER_KEY,
            JSON.stringify(response.data.user)
          );
          return { success: true };
        }
        return {
          success: false,
          error: response.error || "Registration failed",
        };
      } catch (err) {
        console.error("Register error:", err);
        return { success: false, error: "Network error" };
      }
    },
    []
  );

  const logout = useCallback(async () => {
    await authApi.logout();
    await AsyncStorage.removeItem(USER_KEY);
    setUser(null);
  }, []);

  const updateProfile = useCallback(async (data: Partial<User>) => {
    try {
      const response = await authApi.updatePreferences(
        data.language,
        data.theme
      );
      if (response.success && response.data?.user) {
        setUser(response.data.user);
        await AsyncStorage.setItem(
          USER_KEY,
          JSON.stringify(response.data.user)
        );
        return { success: true };
      }
      return { success: false, error: response.error || "Update failed" };
    } catch (err) {
      console.error("Update profile error:", err);
      return { success: false, error: "Network error" };
    }
  }, []);

  const addFavoriteTeam = useCallback(async (team: FavoriteTeam) => {
    setFavoriteTeams((prev) => {
      const exists = prev.some((t) => t.id === team.id);
      if (exists) return prev;
      const updated = [...prev, team];
      AsyncStorage.setItem(FAVORITE_TEAMS_KEY, JSON.stringify(updated));
      return updated;
    });
  }, []);

  const removeFavoriteTeam = useCallback(async (teamId: string) => {
    setFavoriteTeams((prev) => {
      const updated = prev.filter((t) => t.id !== teamId);
      AsyncStorage.setItem(FAVORITE_TEAMS_KEY, JSON.stringify(updated));
      return updated;
    });
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      const response = await authApi.getProfile();
      if (response.success && response.data?.user) {
        setUser(response.data.user);
        await AsyncStorage.setItem(
          USER_KEY,
          JSON.stringify(response.data.user)
        );
      }
    } catch (err) {
      console.error("Refresh user error:", err);
    }
  }, []);

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: !!user,
      isLoading,
      favoriteTeams,
      login,
      register,
      logout,
      updateProfile,
      addFavoriteTeam,
      removeFavoriteTeam,
      refreshUser,
    }),
    [
      user,
      isLoading,
      favoriteTeams,
      login,
      register,
      logout,
      updateProfile,
      addFavoriteTeam,
      removeFavoriteTeam,
      refreshUser,
    ]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

export default AuthContext;

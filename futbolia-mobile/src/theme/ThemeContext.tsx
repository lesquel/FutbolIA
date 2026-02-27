/**
 * FutbolIA Theme Context
 * Provides dark/light mode switching throughout the app
 */
import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { useColorScheme as useSystemColorScheme } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { lightTheme, darkTheme, Theme, ThemeName } from "./colors";

interface ThemeContextType {
  theme: Theme;
  themeName: ThemeName;
  isDark: boolean;
  toggleTheme: () => void;
  setTheme: (name: ThemeName) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const THEME_STORAGE_KEY = "@futbolia_theme";

interface ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const systemColorScheme = useSystemColorScheme();
  const [themeName, setThemeName] = useState<ThemeName>("dark"); // Default to dark for that futuristic feel

  // Load saved theme on mount
  useEffect(() => {
    loadSavedTheme();
  }, []);

  const loadSavedTheme = async () => {
    try {
      const saved = await AsyncStorage.getItem(THEME_STORAGE_KEY);
      if (saved === "light" || saved === "dark") {
        setThemeName(saved);
      } else if (systemColorScheme) {
        setThemeName(systemColorScheme);
      }
    } catch (error) {
      console.log("Error loading theme:", error);
    }
  };

  const saveTheme = async (name: ThemeName) => {
    try {
      await AsyncStorage.setItem(THEME_STORAGE_KEY, name);
    } catch (error) {
      console.log("Error saving theme:", error);
    }
  };

  const toggleTheme = () => {
    const newTheme = themeName === "dark" ? "light" : "dark";
    setThemeName(newTheme);
    saveTheme(newTheme);
  };

  const setTheme = (name: ThemeName) => {
    setThemeName(name);
    saveTheme(name);
  };

  const theme = themeName === "dark" ? darkTheme : lightTheme;
  const isDark = themeName === "dark";

  return (
    <ThemeContext.Provider
      value={{ theme, themeName, isDark, toggleTheme, setTheme }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}

// Hook for getting themed styles
export function useThemedStyles<T>(
  stylesFactory: (theme: Theme, isDark: boolean) => T
): T {
  const { theme, isDark } = useTheme();
  return stylesFactory(theme, isDark);
}

export { lightTheme, darkTheme };
export type { Theme, ThemeName };

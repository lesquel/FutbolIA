/**
 * FutbolIA Theme Configuration
 * Dark/Light mode support with green accent (futuristic sports feel)
 */

export const lightTheme = {
  name: 'light',
  colors: {
    // Backgrounds
    background: '#f8fafc', // slate-50
    surface: '#ffffff', // white
    surfaceSecondary: '#f1f5f9', // slate-100

    // Text
    text: '#0f172a', // slate-900
    textSecondary: '#475569', // slate-600
    textMuted: '#94a3b8', // slate-400

    // Primary (Green accent - Sporty/Futuristic)
    primary: '#10b981', // emerald-500
    primaryDark: '#059669', // emerald-600
    primaryLight: '#34d399', // emerald-400

    // Secondary (Blue for info)
    secondary: '#3b82f6', // blue-500
    secondaryDark: '#2563eb', // blue-600

    // Accents
    accent: '#00ff9d', // Neon green
    accentGold: '#fbbf24', // amber-400 (for wins)

    // Semantic colors
    success: '#22c55e', // green-500
    warning: '#f59e0b', // amber-500
    error: '#ef4444', // red-500
    info: '#3b82f6', // blue-500

    // Borders
    border: '#e2e8f0', // slate-200
    borderLight: '#f1f5f9', // slate-100

    // Cards
    card: '#ffffff',
    cardBorder: '#e2e8f0',

    // Tab bar
    tabBar: '#ffffff',
    tabBarActive: '#10b981',
    tabBarInactive: '#94a3b8',
  },
  gradients: {
    primary: ['#10b981', '#059669'],
    hero: ['#f8fafc', '#f1f5f9'],
    card: ['#ffffff', '#f8fafc'],
  },
};

export const darkTheme = {
  name: 'dark',
  colors: {
    // Backgrounds
    background: '#020617', // slate-950
    surface: '#0f172a', // slate-900
    surfaceSecondary: '#1e293b', // slate-800

    // Text
    text: '#f8fafc', // slate-50
    textSecondary: '#cbd5e1', // slate-300
    textMuted: '#64748b', // slate-500

    // Primary (Neon Green - Futuristic)
    primary: '#00ff9d', // Neon green
    primaryDark: '#10b981', // emerald-500
    primaryLight: '#34d399', // emerald-400

    // Secondary (Cyan for info)
    secondary: '#06b6d4', // cyan-500
    secondaryDark: '#0891b2', // cyan-600

    // Accents
    accent: '#00ff9d', // Neon green
    accentGold: '#fbbf24', // amber-400 (for wins)

    // Semantic colors
    success: '#22c55e', // green-500
    warning: '#f59e0b', // amber-500
    error: '#f87171', // red-400
    info: '#38bdf8', // sky-400

    // Borders
    border: '#334155', // slate-700
    borderLight: '#1e293b', // slate-800

    // Cards
    card: '#0f172a', // slate-900
    cardBorder: '#334155', // slate-700

    // Tab bar
    tabBar: '#0f172a',
    tabBarActive: '#00ff9d',
    tabBarInactive: '#64748b',
  },
  gradients: {
    primary: ['#00ff9d', '#10b981'],
    hero: ['#020617', '#0f172a'],
    card: ['#0f172a', '#1e293b'],
  },
};

export type Theme = typeof lightTheme;
export type ThemeName = 'light' | 'dark';

// Tailwind class mappings for NativeWind
export const themeClasses = {
  light: {
    bg: 'bg-slate-50',
    surface: 'bg-white',
    text: 'text-slate-900',
    textSecondary: 'text-slate-600',
    border: 'border-slate-200',
    card: 'bg-white border-slate-200',
  },
  dark: {
    bg: 'bg-slate-950',
    surface: 'bg-slate-900',
    text: 'text-slate-50',
    textSecondary: 'text-slate-300',
    border: 'border-slate-700',
    card: 'bg-slate-900 border-slate-700',
  },
};

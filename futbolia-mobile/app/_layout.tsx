/**
 * FutbolIA - Root Layout
 * Main app layout with theme, i18n and auth providers
 */
import 'react-native-reanimated';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import {
  DarkTheme,
  DefaultTheme,
  ThemeProvider as NavigationThemeProvider,
} from '@react-navigation/native';
import { useFonts } from 'expo-font';
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';
import { LogBox, Platform } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import '../global.css';

// i18n initialization
import '@/src/i18n/i18n';

// Silenciar warnings específicos de React Native
const warningsToIgnore = [
  'props.pointerEvents is deprecated',
  'Cannot record touch end without a touch start',
  'useNativeDriver is not supported',
  'paddingTop was given a value',
  'SafeAreaView has been deprecated',
];

if (Platform.OS === 'web') {
  // Silenciar warnings en Web
  const originalWarn = console.warn;
  console.warn = (...args: any[]) => {
    const message = args[0]?.toString() || '';
    if (warningsToIgnore.some((w) => message.includes(w))) {
      return; // Silenciar estos warnings
    }
    originalWarn.apply(console, args);
  };
} else {
  // Para plataformas nativas, usar LogBox
  LogBox.ignoreLogs(warningsToIgnore);
}

// Theme provider
import { ThemeProvider, useTheme } from '@/src/theme';

// Auth provider
import { AuthProvider } from '@/src/context';

export { ErrorBoundary } from 'expo-router';

export const unstable_settings = {
  initialRouteName: '(tabs)',
};

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [loaded, error] = useFonts({
    SpaceMono: require('../assets/fonts/SpaceMono-Regular.ttf'),
    ...FontAwesome.font,
  });

  useEffect(() => {
    if (error) throw error;
  }, [error]);

  useEffect(() => {
    if (loaded) {
      SplashScreen.hideAsync();
    }
  }, [loaded]);

  if (!loaded) {
    return null;
  }

  return (
    <SafeAreaProvider>
      <ThemeProvider>
        <AuthProvider>
          <RootLayoutNav />
        </AuthProvider>
      </ThemeProvider>
    </SafeAreaProvider>
  );
}

function RootLayoutNav() {
  const { isDark, theme } = useTheme();

  // Custom navigation themes
  const customDarkTheme = {
    ...DarkTheme,
    colors: {
      ...DarkTheme.colors,
      background: theme.colors.background,
      card: theme.colors.surface,
      text: theme.colors.text,
      border: theme.colors.border,
      primary: theme.colors.primary,
    },
  };

  const customLightTheme = {
    ...DefaultTheme,
    colors: {
      ...DefaultTheme.colors,
      background: theme.colors.background,
      card: theme.colors.surface,
      text: theme.colors.text,
      border: theme.colors.border,
      primary: theme.colors.primary,
    },
  };

  return (
    <NavigationThemeProvider value={isDark ? customDarkTheme : customLightTheme}>
      <Stack>
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen
          name="login"
          options={{
            title: 'Iniciar Sesión',
            headerShown: false,
            presentation: 'card',
          }}
        />
        <Stack.Screen
          name="register"
          options={{
            title: 'Registrarse',
            headerShown: false,
            presentation: 'card',
          }}
        />
        <Stack.Screen
          name="profile"
          options={{
            title: 'Mi Perfil',
            presentation: 'card',
          }}
        />
        <Stack.Screen
          name="teams"
          options={{
            title: 'Equipos',
            headerShown: false,
            presentation: 'card',
          }}
        />
        <Stack.Screen
          name="modal"
          options={{
            presentation: 'modal',
            title: 'Información',
          }}
        />
      </Stack>
    </NavigationThemeProvider>
  );
}

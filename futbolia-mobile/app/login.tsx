/**
 * FutbolIA - Login Screen
 * User authentication with email and password
 */
import React, { useState } from "react";
import {
  View,
  StyleSheet,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Image,
  useWindowDimensions,
} from "react-native";
import { useRouter } from "expo-router";
import { useTranslation } from "react-i18next";

import { useTheme } from "@/src/theme";
import { useAuth } from "@/src/context";
import { ThemedView, ThemedText, Card, Button } from "@/src/components/ui";

export default function LoginScreen() {
  const { theme } = useTheme();
  const { t } = useTranslation();
  const { login } = useAuth();
  const router = useRouter();
  const { width: screenWidth } = useWindowDimensions();
  const isTablet = screenWidth >= 768;
  const isDesktop = screenWidth >= 1024;
  const isLargeScreen = isTablet || isDesktop;

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async () => {
    // Validation
    if (!email.trim()) {
      setError(t("auth.emailRequired"));
      return;
    }
    if (!password.trim()) {
      setError(t("auth.passwordRequired"));
      return;
    }

    setLoading(true);
    setError(null);

    const result = await login(email.trim(), password);

    setLoading(false);

    if (result.success) {
      router.replace("/(tabs)");
    } else {
      setError(result.error || t("auth.loginError"));
    }
  };

  const handleGuestMode = () => {
    // Continue without login
    router.replace("/(tabs)");
  };

  return (
    <ThemedView variant="background" style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={[
            styles.scrollContent,
            isLargeScreen && styles.scrollContentLarge,
          ]}
          keyboardShouldPersistTaps="handled"
        >
          {/* Logo & Header */}
          <View style={[styles.header, isLargeScreen && styles.headerLarge]}>
            <Image
              source={require("../assets/images/logo.png")}
              style={[styles.logoImage, isLargeScreen && styles.logoImageLarge]}
              resizeMode="contain"
            />
            <ThemedText size={isLargeScreen ? "4xl" : "3xl"} weight="bold">
              GoalMind: El Oráculo del Fútbol
            </ThemedText>
            <ThemedText
              variant="secondary"
              size={isLargeScreen ? "xl" : "lg"}
              style={[styles.subtitle, isLargeScreen && styles.subtitleLarge]}
            >
              {t("auth.loginSubtitle")}
            </ThemedText>
          </View>

          {/* Login Form */}
          <Card
            variant="elevated"
            padding={isLargeScreen ? "xl" : "lg"}
            style={[styles.formCard, isLargeScreen && styles.formCardLarge]}
          >
            <ThemedText
              size={isLargeScreen ? "2xl" : "xl"}
              weight="semibold"
              style={[styles.formTitle, isLargeScreen && styles.formTitleLarge]}
            >
              {t("auth.login")}
            </ThemedText>

            {/* Error Message */}
            {error && (
              <View
                style={[
                  styles.errorBox,
                  { backgroundColor: theme.colors.error + "20" },
                ]}
              >
                <ThemedText style={{ color: theme.colors.error }}>
                  {error}
                </ThemedText>
              </View>
            )}

            {/* Debug Info (Only in Dev) */}
            {__DEV__ && (
              <ThemedText
                size="xs"
                variant="secondary"
                style={{ textAlign: "center", marginBottom: 10, opacity: 0.5 }}
              >
                API: {process.env.EXPO_PUBLIC_API_URL || "Fallback (localhost)"}
              </ThemedText>
            )}

            {/* Email Input */}
            <View style={styles.inputGroup}>
              <ThemedText weight="medium" style={styles.label}>
                {t("auth.email")}
              </ThemedText>
              <TextInput
                style={[
                  styles.input,
                  {
                    backgroundColor: theme.colors.surfaceSecondary,
                    borderColor: theme.colors.border,
                    color: theme.colors.text,
                  },
                ]}
                placeholder={t("auth.emailPlaceholder")}
                placeholderTextColor={theme.colors.textMuted}
                value={email}
                onChangeText={setEmail}
                autoCapitalize="none"
                keyboardType="email-address"
                autoComplete="email"
              />
            </View>

            {/* Password Input */}
            <View style={styles.inputGroup}>
              <ThemedText weight="medium" style={styles.label}>
                {t("auth.password")}
              </ThemedText>
              <View style={styles.passwordContainer}>
                <TextInput
                  style={[
                    styles.input,
                    styles.passwordInput,
                    {
                      backgroundColor: theme.colors.surfaceSecondary,
                      borderColor: theme.colors.border,
                      color: theme.colors.text,
                    },
                  ]}
                  placeholder={t("auth.passwordPlaceholder")}
                  placeholderTextColor={theme.colors.textMuted}
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry={!showPassword}
                  autoComplete="password"
                />
                <TouchableOpacity
                  style={styles.eyeButton}
                  onPress={() => setShowPassword(!showPassword)}
                >
                  <ThemedText size="lg">
                    {showPassword ? "🙈" : "👁️"}
                  </ThemedText>
                </TouchableOpacity>
              </View>
            </View>

            {/* Login Button */}
            <Button
              title={loading ? "" : t("auth.loginButton")}
              variant="primary"
              size="lg"
              fullWidth
              onPress={handleLogin}
              disabled={loading}
              style={styles.loginButton}
            >
              {loading && (
                <ActivityIndicator color="#fff" style={styles.loader} />
              )}
            </Button>

            {/* Forgot Password */}
            <TouchableOpacity style={styles.forgotPassword}>
              <ThemedText variant="primary" size="sm">
                {t("auth.forgotPassword")}
              </ThemedText>
            </TouchableOpacity>
          </Card>

          {/* Register Link */}
          <View style={styles.registerSection}>
            <ThemedText variant="secondary">{t("auth.noAccount")}</ThemedText>
            <TouchableOpacity onPress={() => router.push("/register")}>
              <ThemedText variant="primary" weight="semibold">
                {" "}
                {t("auth.registerNow")}
              </ThemedText>
            </TouchableOpacity>
          </View>

          {/* Guest Mode */}
          <TouchableOpacity style={styles.guestMode} onPress={handleGuestMode}>
            <ThemedText variant="muted" size="sm">
              {t("auth.continueAsGuest")} →
            </ThemedText>
          </TouchableOpacity>

          {/* GoalMind Message */}
          <View
            style={[
              styles.goalMindBox,
              { backgroundColor: theme.colors.primary + "15" },
            ]}
          >
            <ThemedText
              variant="secondary"
              size="sm"
              style={styles.goalMindText}
            >
              {t("auth.dixieWelcome")}
            </ThemedText>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    paddingHorizontal: 20,
    paddingVertical: 24,
    justifyContent: "center",
  },
  header: {
    alignItems: "center",
    marginBottom: 32,
  },
  logoImage: {
    width: 100,
    height: 100,
    marginBottom: 20,
  },
  logo: {
    fontSize: 56,
    marginBottom: 10,
  },
  subtitle: {
    marginTop: 10,
    textAlign: "center",
    paddingHorizontal: 16,
    lineHeight: 24,
  },
  formCard: {
    marginBottom: 24,
    paddingHorizontal: 20,
    paddingVertical: 24,
  },
  formTitle: {
    textAlign: "center",
    marginBottom: 24,
  },
  errorBox: {
    padding: 14,
    borderRadius: 10,
    marginBottom: 18,
  },
  inputGroup: {
    marginBottom: 18,
  },
  label: {
    marginBottom: 10,
  },
  input: {
    borderWidth: 1,
    borderRadius: 14,
    padding: 16,
    fontSize: 16,
    minHeight: 52,
  },
  passwordContainer: {
    position: "relative",
  },
  passwordInput: {
    paddingRight: 54,
  },
  eyeButton: {
    position: "absolute",
    right: 14,
    top: 14,
    padding: 6,
  },
  loginButton: {
    marginTop: 12,
  },
  loader: {
    marginLeft: 10,
  },
  forgotPassword: {
    alignItems: "center",
    marginTop: 18,
    padding: 8,
  },
  registerSection: {
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 18,
    flexWrap: "wrap",
  },
  guestMode: {
    alignItems: "center",
    marginBottom: 28,
    padding: 8,
  },
  goalMindBox: {
    flexDirection: "row",
    alignItems: "center",
    padding: 18,
    borderRadius: 14,
    gap: 14,
  },
  goalMindText: {
    flex: 1,
    lineHeight: 22,
  },
  // ==========================================
  // RESPONSIVE STYLES FOR TABLETS AND DESKTOP
  // ==========================================
  scrollContentLarge: {
    paddingHorizontal: 48,
    maxWidth: 600,
    alignSelf: "center",
    width: "100%",
  },
  headerLarge: {
    marginBottom: 40,
  },
  logoImageLarge: {
    width: 140,
    height: 140,
    marginBottom: 28,
  },
  subtitleLarge: {
    marginTop: 14,
    lineHeight: 30,
  },
  formCardLarge: {
    borderRadius: 20,
    marginBottom: 32,
    paddingHorizontal: 32,
    paddingVertical: 32,
  },
  formTitleLarge: {
    marginBottom: 32,
  },
});

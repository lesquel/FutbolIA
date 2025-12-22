/**
 * FutbolIA - Register Screen
 * User registration with email, username, and password
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
} from "react-native";
import { useRouter } from "expo-router";
import { useTranslation } from "react-i18next";

import { useTheme } from "@/src/theme";
import { useAuth } from "@/src/context";
import { ThemedView, ThemedText, Card, Button } from "@/src/components/ui";

export default function RegisterScreen() {
  const { theme } = useTheme();
  const { t } = useTranslation();
  const { register } = useAuth();
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const handleRegister = async () => {
    // Validation
    if (!email.trim()) {
      setError(t("auth.emailRequired"));
      return;
    }
    if (!username.trim()) {
      setError(t("auth.usernameRequired"));
      return;
    }
    if (username.trim().length < 3) {
      setError(t("auth.usernameTooShort"));
      return;
    }
    if (!password.trim()) {
      setError(t("auth.passwordRequired"));
      return;
    }
    if (password.length < 6) {
      setError(t("auth.passwordTooShort"));
      return;
    }
    if (password !== confirmPassword) {
      setError(t("auth.passwordsDontMatch"));
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setError(t("auth.invalidEmail"));
      return;
    }

    setLoading(true);
    setError(null);

    const result = await register(email.trim(), username.trim(), password);

    setLoading(false);

    if (result.success) {
      router.replace("/(tabs)");
    } else {
      setError(result.error || t("auth.registerError"));
    }
  };

  return (
    <ThemedView variant="background" style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          {/* Header */}
          <View style={styles.header}>
            <ThemedText size="3xl" weight="bold" style={styles.logo}>
              ⚽
            </ThemedText>
            <ThemedText size="2xl" weight="bold">
              {t("auth.createAccount")}
            </ThemedText>
            <ThemedText variant="secondary" style={styles.subtitle}>
              {t("auth.registerSubtitle")}
            </ThemedText>
          </View>

          {/* Register Form */}
          <Card variant="elevated" padding="lg" style={styles.formCard}>
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

            {/* Email Input */}
            <View style={styles.inputGroup}>
              <ThemedText weight="medium" style={styles.label}>
                {t("auth.email")} *
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

            {/* Username Input */}
            <View style={styles.inputGroup}>
              <ThemedText weight="medium" style={styles.label}>
                {t("auth.username")} *
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
                placeholder={t("auth.usernamePlaceholder")}
                placeholderTextColor={theme.colors.textMuted}
                value={username}
                onChangeText={setUsername}
                autoCapitalize="none"
                autoComplete="username-new"
              />
            </View>

            {/* Password Input */}
            <View style={styles.inputGroup}>
              <ThemedText weight="medium" style={styles.label}>
                {t("auth.password")} *
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
                  autoComplete="password-new"
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
              <ThemedText variant="muted" size="xs" style={styles.hint}>
                {t("auth.passwordHint")}
              </ThemedText>
            </View>

            {/* Confirm Password Input */}
            <View style={styles.inputGroup}>
              <ThemedText weight="medium" style={styles.label}>
                {t("auth.confirmPassword")} *
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
                placeholder={t("auth.confirmPasswordPlaceholder")}
                placeholderTextColor={theme.colors.textMuted}
                value={confirmPassword}
                onChangeText={setConfirmPassword}
                secureTextEntry={!showPassword}
              />
            </View>

            {/* Register Button */}
            <Button
              title={loading ? "" : t("auth.registerButton")}
              variant="primary"
              size="lg"
              fullWidth
              onPress={handleRegister}
              disabled={loading}
              style={styles.registerButton}
            >
              {loading && (
                <ActivityIndicator color="#fff" style={styles.loader} />
              )}
            </Button>

            {/* Terms */}
            <ThemedText variant="muted" size="xs" style={styles.terms}>
              {t("auth.termsText")}
            </ThemedText>
          </Card>

          {/* Login Link */}
          <View style={styles.loginSection}>
            <ThemedText variant="secondary">{t("auth.haveAccount")}</ThemedText>
            <TouchableOpacity onPress={() => router.back()}>
              <ThemedText variant="primary" weight="semibold">
                {" "}
                {t("auth.loginNow")}
              </ThemedText>
            </TouchableOpacity>
          </View>

          {/* Benefits */}
          <Card variant="outlined" padding="md" style={styles.benefitsCard}>
            <ThemedText weight="semibold" style={styles.benefitsTitle}>
              🎁 {t("auth.benefits")}
            </ThemedText>
            <View style={styles.benefitsList}>
              <View style={styles.benefitItem}>
                <ThemedText>✅</ThemedText>
                <ThemedText variant="secondary" size="sm">
                  {t("auth.benefit1")}
                </ThemedText>
              </View>
              <View style={styles.benefitItem}>
                <ThemedText>✅</ThemedText>
                <ThemedText variant="secondary" size="sm">
                  {t("auth.benefit2")}
                </ThemedText>
              </View>
              <View style={styles.benefitItem}>
                <ThemedText>✅</ThemedText>
                <ThemedText variant="secondary" size="sm">
                  {t("auth.benefit3")}
                </ThemedText>
              </View>
            </View>
          </Card>
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
    padding: 24,
  },
  header: {
    alignItems: "center",
    marginBottom: 24,
    marginTop: 20,
  },
  logo: {
    fontSize: 48,
    marginBottom: 8,
  },
  subtitle: {
    marginTop: 8,
    textAlign: "center",
  },
  formCard: {
    marginBottom: 20,
  },
  errorBox: {
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  inputGroup: {
    marginBottom: 16,
  },
  label: {
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
    fontSize: 16,
  },
  passwordContainer: {
    position: "relative",
  },
  passwordInput: {
    paddingRight: 50,
  },
  eyeButton: {
    position: "absolute",
    right: 12,
    top: 12,
    padding: 4,
  },
  hint: {
    marginTop: 4,
  },
  registerButton: {
    marginTop: 8,
  },
  loader: {
    marginLeft: 8,
  },
  terms: {
    textAlign: "center",
    marginTop: 16,
    lineHeight: 18,
  },
  loginSection: {
    flexDirection: "row",
    justifyContent: "center",
    marginBottom: 20,
  },
  benefitsCard: {
    marginBottom: 20,
  },
  benefitsTitle: {
    marginBottom: 12,
  },
  benefitsList: {
    gap: 8,
  },
  benefitItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
});

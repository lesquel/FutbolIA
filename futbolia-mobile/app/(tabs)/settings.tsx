/**
 * FutbolIA - Settings Screen
 * App preferences: theme, language, account, and about
 */
import { useState } from "react";
import {
  ScrollView,
  View,
  StyleSheet,
  Switch,
  TouchableOpacity,
  Alert,
} from "react-native";
import { useTranslation } from "react-i18next";
import { useRouter } from "expo-router";
import {
  Wrench,
  Atom,
  Smartphone,
  Zap,
  Brain,
  Database,
  Search,
} from "lucide-react-native";

import { useTheme } from "@/src/theme";
import { useAuth } from "@/src/context";
import { changeLanguage, getCurrentLanguage } from "@/src/i18n/i18n";
import { ThemedView, ThemedText, Card, Icon } from "@/src/components/ui";

export default function SettingsScreen() {
  const { theme, isDark, toggleTheme } = useTheme();
  const { t, i18n } = useTranslation();
  const { user, isAuthenticated, logout } = useAuth();
  const router = useRouter();

  const [currentLang, setCurrentLang] = useState(getCurrentLanguage());

  const handleLanguageChange = (lang: "es" | "en") => {
    changeLanguage(lang);
    setCurrentLang(lang);
  };

  const handleLogout = () => {
    Alert.alert(t("profile.logoutTitle"), t("profile.logoutMessage"), [
      { text: t("common.cancel"), style: "cancel" },
      {
        text: t("profile.logout"),
        style: "destructive",
        onPress: async () => {
          await logout();
        },
      },
    ]);
  };

  const SettingRow = ({
    icon,
    title,
    subtitle,
    right,
    onPress,
  }: {
    icon: string;
    title: string;
    subtitle?: string;
    right?: React.ReactNode;
    onPress?: () => void;
  }) => (
    <TouchableOpacity
      onPress={onPress}
      disabled={!onPress}
      activeOpacity={onPress ? 0.7 : 1}
    >
      <View style={styles.settingRow}>
        <ThemedText size="xl">{icon}</ThemedText>
        <View style={styles.settingInfo}>
          <ThemedText weight="medium">{title}</ThemedText>
          {subtitle && (
            <ThemedText variant="muted" size="sm">
              {subtitle}
            </ThemedText>
          )}
        </View>
        {right}
      </View>
    </TouchableOpacity>
  );

  return (
    <ThemedView variant="background" style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Account Section */}
        <View style={styles.section}>
          <ThemedText variant="secondary" size="sm" style={styles.sectionTitle}>
            CUENTA
          </ThemedText>

          <Card variant="default" padding="none">
            {isAuthenticated ? (
              <>
                <TouchableOpacity
                  onPress={() => router.push("/profile")}
                  activeOpacity={0.7}
                >
                  <View style={styles.settingRow}>
                    <View
                      style={[
                        styles.avatar,
                        { backgroundColor: theme.colors.primary },
                      ]}
                    >
                      <ThemedText
                        size="lg"
                        weight="bold"
                        style={{ color: "#fff" }}
                      >
                        {user?.username?.[0]?.toUpperCase() || "U"}
                      </ThemedText>
                    </View>
                    <View style={styles.settingInfo}>
                      <ThemedText weight="semibold">
                        {user?.username}
                      </ThemedText>
                      <ThemedText variant="muted" size="sm">
                        {user?.email}
                      </ThemedText>
                    </View>
                    <ThemedText variant="muted">→</ThemedText>
                  </View>
                </TouchableOpacity>

                <View
                  style={[
                    styles.divider,
                    { backgroundColor: theme.colors.border },
                  ]}
                />

                <SettingRow
                  icon="❤️"
                  title={t("profile.favoriteTeams")}
                  subtitle="Gestiona tus equipos favoritos"
                  onPress={() => router.push("/teams")}
                  right={<ThemedText variant="muted">→</ThemedText>}
                />

                <View
                  style={[
                    styles.divider,
                    { backgroundColor: theme.colors.border },
                  ]}
                />

                <SettingRow
                  icon="🚪"
                  title={t("profile.logout")}
                  onPress={handleLogout}
                  right={
                    <ThemedText style={{ color: theme.colors.error }}>
                      →
                    </ThemedText>
                  }
                />
              </>
            ) : (
              <>
                <SettingRow
                  icon="👤"
                  title={t("auth.login")}
                  subtitle="Inicia sesión para guardar predicciones"
                  onPress={() => router.push("/login")}
                  right={<ThemedText variant="muted">→</ThemedText>}
                />

                <View
                  style={[
                    styles.divider,
                    { backgroundColor: theme.colors.border },
                  ]}
                />

                <SettingRow
                  icon="📝"
                  title={t("auth.register")}
                  subtitle="Crea una cuenta nueva"
                  onPress={() => router.push("/register")}
                  right={<ThemedText variant="muted">→</ThemedText>}
                />
              </>
            )}
          </Card>
        </View>

        {/* Appearance Section */}
        <View style={styles.section}>
          <ThemedText variant="secondary" size="sm" style={styles.sectionTitle}>
            {t("settings.appearance").toUpperCase()}
          </ThemedText>

          <Card variant="default" padding="none">
            <SettingRow
              icon="🌙"
              title={isDark ? t("settings.darkMode") : t("settings.lightMode")}
              subtitle="Cambia el tema de la aplicación"
              right={
                <Switch
                  value={isDark}
                  onValueChange={toggleTheme}
                  trackColor={{
                    false: theme.colors.border,
                    true: theme.colors.primary + "50",
                  }}
                  thumbColor={
                    isDark ? theme.colors.primary : theme.colors.textMuted
                  }
                />
              }
            />
          </Card>
        </View>

        {/* Language Section */}
        <View style={styles.section}>
          <ThemedText variant="secondary" size="sm" style={styles.sectionTitle}>
            {t("settings.language").toUpperCase()}
          </ThemedText>

          <Card variant="default" padding="none">
            <TouchableOpacity
              onPress={() => handleLanguageChange("es")}
              style={[
                styles.languageOption,
                currentLang === "es" && {
                  backgroundColor: theme.colors.primary + "15",
                },
              ]}
            >
              <ThemedText size="xl">🇪🇸</ThemedText>
              <ThemedText weight={currentLang === "es" ? "semibold" : "normal"}>
                {t("settings.spanish")}
              </ThemedText>
              {currentLang === "es" && (
                <ThemedText variant="primary" style={styles.checkmark}>
                  ✓
                </ThemedText>
              )}
            </TouchableOpacity>

            <View
              style={[styles.divider, { backgroundColor: theme.colors.border }]}
            />

            <TouchableOpacity
              onPress={() => handleLanguageChange("en")}
              style={[
                styles.languageOption,
                currentLang === "en" && {
                  backgroundColor: theme.colors.primary + "15",
                },
              ]}
            >
              <ThemedText size="xl">🇺🇸</ThemedText>
              <ThemedText weight={currentLang === "en" ? "semibold" : "normal"}>
                {t("settings.english")}
              </ThemedText>
              {currentLang === "en" && (
                <ThemedText variant="primary" style={styles.checkmark}>
                  ✓
                </ThemedText>
              )}
            </TouchableOpacity>
          </Card>
        </View>

        {/* About Section */}
        <View style={styles.section}>
          <ThemedText variant="secondary" size="sm" style={styles.sectionTitle}>
            {t("settings.about").toUpperCase()}
          </ThemedText>

          <Card variant="default" padding="none">
            <SettingRow
              icon="🏆"
              title="FutbolIA"
              subtitle="Tu oráculo deportivo con IA"
            />

            <View
              style={[styles.divider, { backgroundColor: theme.colors.border }]}
            />

            <SettingRow
              icon="📱"
              title={t("settings.version")}
              right={<ThemedText variant="muted">1.0.0</ThemedText>}
            />

            <View
              style={[styles.divider, { backgroundColor: theme.colors.border }]}
            />

            <SettingRow
              icon="🧠"
              title="Dixie AI"
              subtitle="Powered by DeepSeek"
            />
          </Card>
        </View>

        {/* Tech Stack Info */}
        <Card variant="outlined" padding="md" style={styles.techCard}>
          <View style={styles.techTitleRow}>
            <Icon icon={Wrench} size={20} variant="primary" />
            <ThemedText weight="semibold" style={styles.techTitle}>
              Stack Tecnológico
            </ThemedText>
          </View>

          <View style={styles.techGrid}>
            <View style={styles.techItem}>
              <Icon icon={Atom} size={24} variant="primary" />
              <ThemedText variant="muted" size="xs">
                React Native
              </ThemedText>
            </View>
            <View style={styles.techItem}>
              <Icon icon={Smartphone} size={24} variant="primary" />
              <ThemedText variant="muted" size="xs">
                Expo
              </ThemedText>
            </View>
            <View style={styles.techItem}>
              <Icon icon={Zap} size={24} variant="primary" />
              <ThemedText variant="muted" size="xs">
                FastAPI
              </ThemedText>
            </View>
            <View style={styles.techItem}>
              <Icon icon={Brain} size={24} variant="primary" />
              <ThemedText variant="muted" size="xs">
                DeepSeek
              </ThemedText>
            </View>
            <View style={styles.techItem}>
              <Icon icon={Database} size={24} variant="primary" />
              <ThemedText variant="muted" size="xs">
                MongoDB
              </ThemedText>
            </View>
            <View style={styles.techItem}>
              <Icon icon={Search} size={24} variant="primary" />
              <ThemedText variant="muted" size="xs">
                ChromaDB
              </ThemedText>
            </View>
          </View>
        </Card>

        {/* Footer */}
        <View style={styles.footer}>
          <ThemedText variant="muted" size="sm">
            Hecho con 💚 para Casa Abierta ULEAM 2025
          </ThemedText>
        </View>
      </ScrollView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 32,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    marginBottom: 12,
    marginLeft: 4,
    letterSpacing: 1,
  },
  settingRow: {
    flexDirection: "row",
    alignItems: "center",
    padding: 16,
    gap: 16,
  },
  settingInfo: {
    flex: 1,
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: "center",
    justifyContent: "center",
  },
  divider: {
    height: 1,
    marginLeft: 56,
  },
  languageOption: {
    flexDirection: "row",
    alignItems: "center",
    padding: 16,
    gap: 16,
  },
  checkmark: {
    marginLeft: "auto",
  },
  techCard: {
    marginBottom: 24,
  },
  techTitle: {
    marginBottom: 16,
  },
  techGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12,
  },
  techItem: {
    alignItems: "center",
    width: "30%",
    paddingVertical: 8,
  },
  footer: {
    alignItems: "center",
    paddingVertical: 20,
  },
});

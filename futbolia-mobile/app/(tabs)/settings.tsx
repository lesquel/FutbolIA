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
  useWindowDimensions,
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
  Trophy,
  User,
  Heart,
  LogOut,
  UserPlus,
  Moon,
  Sun,
  ChevronRight,
  Check,
  type LucideIcon,
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
  const { width: screenWidth } = useWindowDimensions();
  const isTablet = screenWidth >= 768;
  const isDesktop = screenWidth >= 1024;
  const isLargeScreen = isTablet || isDesktop;

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
    iconVariant = "secondary",
  }: {
    icon: LucideIcon;
    title: string;
    subtitle?: string;
    right?: React.ReactNode;
    onPress?: () => void;
    iconVariant?: "primary" | "secondary" | "muted" | "error";
  }) => (
    <TouchableOpacity
      onPress={onPress}
      disabled={!onPress}
      activeOpacity={onPress ? 0.7 : 1}
    >
      <View
        style={[styles.settingRow, isLargeScreen && styles.settingRowLarge]}
      >
        <Icon
          icon={icon}
          size={isLargeScreen ? 26 : 22}
          variant={iconVariant}
        />
        <View style={styles.settingInfo}>
          <ThemedText weight="medium" size={isLargeScreen ? "lg" : "base"}>
            {title}
          </ThemedText>
          {subtitle && (
            <ThemedText variant="muted" size={isLargeScreen ? "base" : "sm"}>
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
                  icon={LogOut}
                  title={t("profile.logout")}
                  onPress={handleLogout}
                  iconVariant="error"
                  right={<Icon icon={ChevronRight} size={18} variant="error" />}
                />
              </>
            ) : (
              <>
                <SettingRow
                  icon={User}
                  title={t("auth.login")}
                  subtitle="Inicia sesión para guardar predicciones"
                  onPress={() => router.push("/login")}
                  right={<Icon icon={ChevronRight} size={18} variant="muted" />}
                />

                <View
                  style={[
                    styles.divider,
                    { backgroundColor: theme.colors.border },
                  ]}
                />

                <SettingRow
                  icon={UserPlus}
                  title={t("auth.register")}
                  subtitle="Crea una cuenta nueva"
                  onPress={() => router.push("/register")}
                  right={<Icon icon={ChevronRight} size={18} variant="muted" />}
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
            <View style={styles.settingRow}>
              <Icon icon={isDark ? Moon : Sun} size={22} variant="primary" />
              <View style={styles.settingInfo}>
                <ThemedText weight="medium">
                  {isDark ? t("settings.darkMode") : t("settings.lightMode")}
                </ThemedText>
                <ThemedText variant="muted" size="sm">
                  Cambia el tema de la aplicación
                </ThemedText>
              </View>
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
            </View>
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
              <View style={styles.flagContainer}>
                <ThemedText
                  size="lg"
                  weight="bold"
                  style={{ color: theme.colors.primary }}
                >
                  ES
                </ThemedText>
              </View>
              <ThemedText weight={currentLang === "es" ? "semibold" : "normal"}>
                {t("settings.spanish")}
              </ThemedText>
              {currentLang === "es" && (
                <Icon icon={Check} size={20} variant="primary" />
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
              <View style={styles.flagContainer}>
                <ThemedText
                  size="lg"
                  weight="bold"
                  style={{ color: theme.colors.primary }}
                >
                  EN
                </ThemedText>
              </View>
              <ThemedText weight={currentLang === "en" ? "semibold" : "normal"}>
                {t("settings.english")}
              </ThemedText>
              {currentLang === "en" && (
                <Icon icon={Check} size={20} variant="primary" />
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
            <View style={styles.settingRow}>
              <Icon icon={Trophy} size={22} variant="primary" />
              <View style={styles.settingInfo}>
                <ThemedText weight="medium">
                  GoalMind: El Oráculo del Fútbol
                </ThemedText>
                <ThemedText variant="muted" size="sm">
                  Tu oráculo deportivo con IA
                </ThemedText>
              </View>
            </View>

            <View
              style={[styles.divider, { backgroundColor: theme.colors.border }]}
            />

            <View style={styles.settingRow}>
              <Icon icon={Smartphone} size={22} variant="secondary" />
              <View style={styles.settingInfo}>
                <ThemedText weight="medium">{t("settings.version")}</ThemedText>
              </View>
              <ThemedText variant="muted">1.0.0</ThemedText>
            </View>

            <View
              style={[styles.divider, { backgroundColor: theme.colors.border }]}
            />

            <View style={styles.settingRow}>
              <Icon icon={Brain} size={22} variant="secondary" />
              <View style={styles.settingInfo}>
                <ThemedText weight="medium">GoalMind AI</ThemedText>
                <ThemedText variant="muted" size="sm">
                  Powered by DeepSeek
                </ThemedText>
              </View>
            </View>
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
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 40,
  },
  section: {
    marginBottom: 28,
  },
  sectionTitle: {
    marginBottom: 14,
    marginLeft: 4,
    letterSpacing: 1,
  },
  settingRow: {
    flexDirection: "row",
    alignItems: "center",
    padding: 18,
    gap: 18,
  },
  settingInfo: {
    flex: 1,
  },
  avatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: "center",
    justifyContent: "center",
  },
  divider: {
    height: 1,
    marginLeft: 60,
  },
  languageOption: {
    flexDirection: "row",
    alignItems: "center",
    padding: 18,
    gap: 18,
  },
  flagContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "rgba(16, 185, 129, 0.1)",
    alignItems: "center",
    justifyContent: "center",
  },
  techCard: {
    marginBottom: 28,
    paddingVertical: 20,
  },
  techTitleRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    marginBottom: 8,
  },
  techTitle: {
    marginBottom: 18,
  },
  techGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 14,
    justifyContent: "space-around",
  },
  techItem: {
    alignItems: "center",
    width: "28%",
    minWidth: 80,
    paddingVertical: 10,
  },
  footer: {
    alignItems: "center",
    paddingVertical: 24,
  },
  // ==========================================
  // RESPONSIVE STYLES FOR TABLETS AND DESKTOP
  // ==========================================
  settingRowLarge: {
    padding: 22,
    gap: 22,
  },
});

/**
 * FutbolIA - Profile Screen
 * User profile management with favorite teams
 */
import React, { useState } from "react";
import {
  View,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Image,
} from "react-native";
import { useRouter } from "expo-router";
import { useTranslation } from "react-i18next";

import { useTheme } from "@/src/theme";
import { useAuth, FavoriteTeam } from "@/src/context";
import { ThemedView, ThemedText, Card, Button } from "@/src/components/ui";

export default function ProfileScreen() {
  const { theme } = useTheme();
  const { t } = useTranslation();
  const { user, isAuthenticated, favoriteTeams, removeFavoriteTeam, logout } =
    useAuth();
  const router = useRouter();

  const [stats] = useState({
    totalPredictions: 47,
    correctPredictions: 32,
    streak: 5,
    favoriteLeague: "La Liga",
  });

  const accuracy =
    stats.totalPredictions > 0
      ? Math.round((stats.correctPredictions / stats.totalPredictions) * 100)
      : 0;

  const handleLogout = () => {
    Alert.alert(t("profile.logoutTitle"), t("profile.logoutMessage"), [
      { text: t("common.cancel"), style: "cancel" },
      {
        text: t("profile.logout"),
        style: "destructive",
        onPress: () => {
          void logout().then(() => {
            router.replace("/login");
          });
        },
      },
    ]);
  };

  const handleRemoveTeam = (team: FavoriteTeam) => {
    Alert.alert(
      t("profile.removeTeamTitle"),
      t("profile.removeTeamMessage", { team: team.name }),
      [
        { text: t("common.cancel"), style: "cancel" },
        {
          text: t("common.remove"),
          style: "destructive",
          onPress: () => {
            void removeFavoriteTeam(team.id);
          },
        },
      ]
    );
  };

  // If not authenticated, show login prompt
  if (!isAuthenticated) {
    return (
      <ThemedView variant="background" style={styles.container}>
        <View style={styles.notAuthContainer}>
          <ThemedText size="3xl" style={styles.notAuthEmoji}>
            👤
          </ThemedText>
          <ThemedText size="xl" weight="semibold" style={styles.notAuthTitle}>
            {t("profile.notLoggedIn")}
          </ThemedText>
          <ThemedText variant="secondary" style={styles.notAuthSubtitle}>
            {t("profile.loginPrompt")}
          </ThemedText>
          <Button
            title={t("auth.login")}
            variant="primary"
            size="lg"
            onPress={() => router.push("/login")}
            style={styles.loginButton}
          />
          <TouchableOpacity onPress={() => router.push("/register")}>
            <ThemedText variant="primary">
              {t("auth.noAccount")} {t("auth.registerNow")}
            </ThemedText>
          </TouchableOpacity>
        </View>
      </ThemedView>
    );
  }

  return (
    <ThemedView variant="background" style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Profile Header */}
        <Card variant="elevated" padding="lg" style={styles.profileCard}>
          <View style={styles.avatarContainer}>
            <View
              style={[styles.avatar, { backgroundColor: theme.colors.primary }]}
            >
              <ThemedText size="3xl" weight="bold" style={{ color: "#fff" }}>
                {user?.username?.[0]?.toUpperCase() || "U"}
              </ThemedText>
            </View>
            <View style={styles.userInfo}>
              <ThemedText size="xl" weight="bold">
                {user?.username || "Usuario"}
              </ThemedText>
              <ThemedText variant="secondary">
                {user?.email || "email@example.com"}
              </ThemedText>
              <View style={styles.memberBadge}>
                <ThemedText size="xs" style={{ color: theme.colors.primary }}>
                  ⭐ {t("profile.member")}
                </ThemedText>
              </View>
            </View>
          </View>
        </Card>

        {/* Stats Section */}
        <View style={styles.section}>
          <View style={styles.statsTitleRow}>
            <Icon icon={BarChart3} size={18} variant="primary" />
            <ThemedText size="lg" weight="semibold" style={styles.sectionTitle}>
              {t("profile.statistics")}
            </ThemedText>
          </View>

          <View style={styles.statsGrid}>
            <Card variant="outlined" padding="md" style={styles.statCard}>
              <ThemedText
                size="2xl"
                weight="bold"
                style={{ color: theme.colors.primary }}
              >
                {stats.totalPredictions}
              </ThemedText>
              <ThemedText variant="secondary" size="sm">
                {t("profile.totalPredictions")}
              </ThemedText>
            </Card>

            <Card variant="outlined" padding="md" style={styles.statCard}>
              <ThemedText
                size="2xl"
                weight="bold"
                style={{ color: theme.colors.success }}
              >
                {accuracy}%
              </ThemedText>
              <ThemedText variant="secondary" size="sm">
                {t("profile.accuracy")}
              </ThemedText>
            </Card>

            <Card variant="outlined" padding="md" style={styles.statCard}>
              <ThemedText
                size="2xl"
                weight="bold"
                style={{ color: theme.colors.warning }}
              >
                🔥 {stats.streak}
              </ThemedText>
              <ThemedText variant="secondary" size="sm">
                {t("profile.streak")}
              </ThemedText>
            </Card>

            <Card variant="outlined" padding="md" style={styles.statCard}>
              <ThemedText size="xl" weight="bold">
                🏆
              </ThemedText>
              <ThemedText variant="secondary" size="sm" numberOfLines={1}>
                {stats.favoriteLeague}
              </ThemedText>
            </Card>
          </View>
        </View>

        {/* Favorite Teams Section */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <ThemedText size="lg" weight="semibold">
              ❤️ {t("profile.favoriteTeams")}
            </ThemedText>
            <TouchableOpacity onPress={() => router.push("/teams")}>
              <ThemedText variant="primary" size="sm">
                + {t("profile.addTeam")}
              </ThemedText>
            </TouchableOpacity>
          </View>

          {favoriteTeams.length > 0 ? (
            <View style={styles.teamsList}>
              {favoriteTeams.map((team) => (
                <Card
                  key={team.id}
                  variant="default"
                  padding="sm"
                  style={styles.teamCard}
                >
                  <View style={styles.teamRow}>
                    <View
                      style={[
                        styles.teamLogo,
                        { backgroundColor: theme.colors.surfaceSecondary },
                      ]}
                    >
                      {team.logoUrl ? (
                        <Image
                          source={{ uri: team.logoUrl }}
                          style={styles.teamLogoImage}
                          resizeMode="contain"
                        />
                      ) : (
                        <ThemedText size="lg">⚽</ThemedText>
                      )}
                    </View>
                    <View style={styles.teamInfo}>
                      <ThemedText weight="semibold">{team.name}</ThemedText>
                      {team.league && (
                        <ThemedText variant="muted" size="sm">
                          {team.league}
                        </ThemedText>
                      )}
                    </View>
                    <TouchableOpacity
                      onPress={() => handleRemoveTeam(team)}
                      style={styles.removeButton}
                    >
                      <ThemedText style={{ color: theme.colors.error }}>
                        ✕
                      </ThemedText>
                    </TouchableOpacity>
                  </View>
                </Card>
              ))}
            </View>
          ) : (
            <Card variant="outlined" padding="lg">
              <View style={styles.emptyTeams}>
                <ThemedText size="3xl">⚽</ThemedText>
                <ThemedText variant="secondary" style={styles.emptyText}>
                  {t("profile.noFavoriteTeams")}
                </ThemedText>
                <Button
                  title={t("profile.searchTeams")}
                  variant="outline"
                  size="sm"
                  onPress={() => router.push("/teams")}
                />
              </View>
            </Card>
          )}
        </View>

        {/* Account Actions */}
        <View style={styles.section}>
          <ThemedText size="lg" weight="semibold" style={styles.sectionTitle}>
            ⚙️ {t("profile.account")}
          </ThemedText>

          <Card variant="default" padding="none">
            <TouchableOpacity
              style={styles.actionRow}
              onPress={() => {
                /* Edit profile */
              }}
            >
              <ThemedText>✏️</ThemedText>
              <ThemedText style={styles.actionText}>
                {t("profile.editProfile")}
              </ThemedText>
              <ThemedText variant="muted">→</ThemedText>
            </TouchableOpacity>

            <View
              style={[styles.divider, { backgroundColor: theme.colors.border }]}
            />

            <TouchableOpacity
              style={styles.actionRow}
              onPress={() => router.push("/settings")}
            >
              <ThemedText>⚙️</ThemedText>
              <ThemedText style={styles.actionText}>
                {t("profile.settings")}
              </ThemedText>
              <ThemedText variant="muted">→</ThemedText>
            </TouchableOpacity>

            <View
              style={[styles.divider, { backgroundColor: theme.colors.border }]}
            />

            <TouchableOpacity style={styles.actionRow} onPress={handleLogout}>
              <ThemedText>🚪</ThemedText>
              <ThemedText
                style={[styles.actionText, { color: theme.colors.error }]}
              >
                {t("profile.logout")}
              </ThemedText>
              <ThemedText style={{ color: theme.colors.error }}>→</ThemedText>
            </TouchableOpacity>
          </Card>
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
  },
  notAuthContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 32,
  },
  notAuthEmoji: {
    marginBottom: 16,
  },
  notAuthTitle: {
    marginBottom: 8,
    textAlign: "center",
  },
  notAuthSubtitle: {
    marginBottom: 24,
    textAlign: "center",
  },
  loginButton: {
    marginBottom: 16,
    minWidth: 200,
  },
  profileCard: {
    marginBottom: 20,
  },
  avatarContainer: {
    flexDirection: "row",
    alignItems: "center",
  },
  avatar: {
    width: 70,
    height: 70,
    borderRadius: 35,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 16,
  },
  userInfo: {
    flex: 1,
  },
  memberBadge: {
    marginTop: 4,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    marginBottom: 12,
    flex: 1,
  },
  statsTitleRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 12,
  },
  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  statsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12,
  },
  statCard: {
    flex: 1,
    minWidth: "45%",
    alignItems: "center",
  },
  teamsList: {
    gap: 8,
  },
  teamCard: {
    marginBottom: 0,
  },
  teamRow: {
    flexDirection: "row",
    alignItems: "center",
  },
  teamLogo: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 12,
  },
  teamLogoImage: {
    width: 32,
    height: 32,
  },
  teamInfo: {
    flex: 1,
  },
  removeButton: {
    padding: 8,
  },
  emptyTeams: {
    alignItems: "center",
    gap: 12,
  },
  emptyText: {
    textAlign: "center",
  },
  actionRow: {
    flexDirection: "row",
    alignItems: "center",
    padding: 16,
    gap: 12,
  },
  actionText: {
    flex: 1,
  },
  divider: {
    height: 1,
  },
});

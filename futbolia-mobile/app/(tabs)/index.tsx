/**
 * FutbolIA - Home Screen
 * Main dashboard with upcoming matches and quick prediction
 */
import { useState, useEffect } from "react";
import {
  ScrollView,
  View,
  StyleSheet,
  RefreshControl,
  Dimensions,
} from "react-native";
import { useRouter } from "expo-router";
import { useTranslation } from "react-i18next";

import { useTheme } from "@/src/theme";
import { ThemedView, ThemedText, Card, Button } from "@/src/components/ui";
import { MatchCard, DixieChat } from "@/src/components/features";
import { predictionsApi, Match } from "@/src/services/api";

const { width } = Dimensions.get("window");
const isTablet = width >= 768;

export default function HomeScreen() {
  const { theme, isDark } = useTheme();
  const { t } = useTranslation();
  const router = useRouter();

  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadMatches();
  }, []);

  const loadMatches = async () => {
    try {
      const response = await predictionsApi.getUpcomingMatches();
      if (response.success && response.data?.matches) {
        setMatches(response.data.matches);
      }
    } catch (error) {
      console.log("Error loading matches:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadMatches();
  };

  const handleMatchPress = (match: Match) => {
    // Navigate to prediction screen with pre-selected teams
    router.push({
      pathname: "/predict",
      params: {
        homeTeam: match.home_team.name,
        awayTeam: match.away_team.name,
      },
    });
  };

  const featuredMatch = matches[0];
  const otherMatches = matches.slice(1, 4);

  return (
    <ThemedView variant="background" style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={theme.colors.primary}
          />
        }
      >
        {/* Responsive Layout Container */}
        <View style={[styles.content, isTablet && styles.contentTablet]}>
          {/* Left Column (or full width on mobile) */}
          <View
            style={[styles.mainColumn, isTablet && styles.mainColumnTablet]}
          >
            {/* Welcome Header */}
            <View style={styles.header}>
              <ThemedText size="3xl" weight="bold">
                {t("home.welcome")} 🏆
              </ThemedText>
              <ThemedText variant="secondary" size="lg">
                {t("home.subtitle")}
              </ThemedText>
            </View>

            {/* Dixie Greeting */}
            <DixieChat showGreeting={true} />

            {/* Featured Match */}
            {featuredMatch && (
              <View style={styles.section}>
                <ThemedText
                  size="lg"
                  weight="semibold"
                  style={styles.sectionTitle}
                >
                  ⚽ {t("home.featuredMatch")}
                </ThemedText>
                <MatchCard
                  match={featuredMatch}
                  onPress={() => handleMatchPress(featuredMatch)}
                  featured={true}
                />
              </View>
            )}

            {/* Quick Predict Button */}
            <View style={styles.quickPredictContainer}>
              <Button
                title={`🔮 ${t("home.quickPredict")}`}
                variant="primary"
                size="lg"
                fullWidth
                onPress={() => router.push("/predict")}
              />
            </View>
          </View>

          {/* Right Column (only on tablet) */}
          {isTablet && (
            <View style={styles.sideColumn}>
              {/* Upcoming Matches */}
              <View style={styles.section}>
                <ThemedText
                  size="lg"
                  weight="semibold"
                  style={styles.sectionTitle}
                >
                  📅 {t("home.upcomingMatches")}
                </ThemedText>

                {otherMatches.map((match) => (
                  <MatchCard
                    key={match.id}
                    match={match}
                    onPress={() => handleMatchPress(match)}
                  />
                ))}

                {otherMatches.length === 0 && (
                  <Card padding="md">
                    <ThemedText variant="muted" style={{ textAlign: "center" }}>
                      {t("common.noResults")}
                    </ThemedText>
                  </Card>
                )}
              </View>
            </View>
          )}
        </View>

        {/* Upcoming Matches (Mobile only) */}
        {!isTablet && otherMatches.length > 0 && (
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <ThemedText size="lg" weight="semibold">
                📅 {t("home.upcomingMatches")}
              </ThemedText>
              <ThemedText
                variant="primary"
                size="sm"
                onPress={() => {
                  /* Navigate to all matches */
                }}
              >
                {t("home.viewAll")} →
              </ThemedText>
            </View>

            {otherMatches.map((match) => (
              <MatchCard
                key={match.id}
                match={match}
                onPress={() => handleMatchPress(match)}
              />
            ))}
          </View>
        )}

        {/* Stats Card */}
        <Card variant="outlined" padding="md" style={styles.statsCard}>
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <ThemedText
                size="2xl"
                weight="bold"
                style={{ color: theme.colors.primary }}
              >
                {matches.length}
              </ThemedText>
              <ThemedText variant="muted" size="xs">
                Partidos Disponibles
              </ThemedText>
            </View>
            <View
              style={[
                styles.statDivider,
                { backgroundColor: theme.colors.border },
              ]}
            />
            <View style={styles.statItem}>
              <ThemedText
                size="2xl"
                weight="bold"
                style={{ color: theme.colors.accentGold }}
              >
                10
              </ThemedText>
              <ThemedText variant="muted" size="xs">
                Equipos con Datos
              </ThemedText>
            </View>
            <View
              style={[
                styles.statDivider,
                { backgroundColor: theme.colors.border },
              ]}
            />
            <View style={styles.statItem}>
              <ThemedText
                size="2xl"
                weight="bold"
                style={{ color: theme.colors.secondary }}
              >
                45+
              </ThemedText>
              <ThemedText variant="muted" size="xs">
                Jugadores FIFA
              </ThemedText>
            </View>
          </View>
        </Card>
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
  content: {
    flex: 1,
  },
  contentTablet: {
    flexDirection: "row",
    gap: 24,
  },
  mainColumn: {
    flex: 1,
  },
  mainColumnTablet: {
    flex: 0.6,
  },
  sideColumn: {
    flex: 0.4,
  },
  header: {
    marginBottom: 20,
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    marginBottom: 12,
  },
  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  quickPredictContainer: {
    marginVertical: 16,
  },
  statsCard: {
    marginTop: 8,
  },
  statsRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-around",
  },
  statItem: {
    alignItems: "center",
    flex: 1,
  },
  statDivider: {
    width: 1,
    height: 40,
  },
});

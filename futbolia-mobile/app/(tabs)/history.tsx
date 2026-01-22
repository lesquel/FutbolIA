/**
 * FutbolIA - History Screen
 * User's prediction history and statistics
 */
import { useState, useEffect, useCallback } from "react";
import {
  ScrollView,
  View,
  StyleSheet,
  RefreshControl,
  FlatList,
  TouchableOpacity,
  useWindowDimensions,
} from "react-native";
import { useFocusEffect, useRouter } from "expo-router";
import { useTranslation } from "react-i18next";
import { ClipboardList, BarChart3, Trophy } from "lucide-react-native";

import { useTheme } from "@/src/theme";
import {
  ThemedView,
  ThemedText,
  Card,
  Button,
  TeamBadge,
  Icon,
} from "@/src/components/ui";
import {
  predictionsApi,
  Prediction,
  PredictionStats,
} from "@/src/services/api";

export default function HistoryScreen() {
  const { theme } = useTheme();
  const { t } = useTranslation();
  const router = useRouter();
  const { width: screenWidth } = useWindowDimensions();
  const isTablet = screenWidth >= 768;
  const isDesktop = screenWidth >= 1024;
  const isLargeScreen = isTablet || isDesktop;

  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [stats, setStats] = useState<PredictionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Reload data when screen comes into focus
  useFocusEffect(
    useCallback(() => {
      loadHistory();
    }, []),
  );

  const loadHistory = async () => {
    try {
      const response = await predictionsApi.getHistory(20);
      if (response.success && response.data) {
        setPredictions(response.data.predictions || []);
        setStats(response.data.stats || null);
      }
    } catch (error) {
      console.log("Error loading history:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadHistory();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("es-ES", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const renderPredictionItem = ({ item }: { item: Prediction }) => (
    <TouchableOpacity
      activeOpacity={0.7}
      onPress={() => router.push(`/prediction/${item.id}`)}
    >
      <Card
        variant="default"
        padding={isLargeScreen ? "lg" : "md"}
        style={[
          styles.predictionCard,
          isLargeScreen && styles.predictionCardLarge,
        ]}
      >
        {/* Match Header */}
        <View
          style={[styles.cardHeader, isLargeScreen && styles.cardHeaderLarge]}
        >
          <ThemedText variant="muted" size={isLargeScreen ? "sm" : "xs"}>
            {item.match?.league || "Liga"}
          </ThemedText>
          <ThemedText variant="muted" size={isLargeScreen ? "sm" : "xs"}>
            {formatDate(item.created_at)}
          </ThemedText>
        </View>

        {/* Teams */}
        <View style={[styles.teamsRow, isLargeScreen && styles.teamsRowLarge]}>
          <View style={styles.teamInfo}>
            <ThemedText
              weight="semibold"
              size={isLargeScreen ? "base" : "sm"}
              numberOfLines={1}
            >
              {item.match?.home_team?.name || "Local"}
            </ThemedText>
          </View>

          <View
            style={[styles.scoreBox, isLargeScreen && styles.scoreBoxLarge]}
          >
            <ThemedText
              size={isLargeScreen ? "xl" : "lg"}
              weight="bold"
              style={{ color: theme.colors.primary }}
            >
              {item.result?.predicted_score || "?-?"}
            </ThemedText>
          </View>

          <View style={[styles.teamInfo, { alignItems: "flex-end" }]}>
            <ThemedText
              weight="semibold"
              size={isLargeScreen ? "base" : "sm"}
              numberOfLines={1}
            >
              {item.match?.away_team?.name || "Visitante"}
            </ThemedText>
          </View>
        </View>

        {/* Prediction Result */}
        <View
          style={[
            styles.resultBadge,
            isLargeScreen && styles.resultBadgeLarge,
            {
              backgroundColor: theme.colors.primary + "15",
              borderColor: theme.colors.primary + "30",
            },
          ]}
        >
          <View
            style={{
              flexDirection: "row",
              alignItems: "center",
              gap: isLargeScreen ? 10 : 6,
            }}
          >
            <Icon
              icon={Trophy}
              size={isLargeScreen ? 20 : 16}
              variant="primary"
            />
            <ThemedText
              variant="primary"
              size={isLargeScreen ? "base" : "sm"}
              weight="semibold"
            >
              {item.result?.winner || "Sin resultado"}
            </ThemedText>
          </View>
          <ThemedText variant="muted" size={isLargeScreen ? "sm" : "xs"}>
            {item.result?.confidence || 0}% confianza
          </ThemedText>
        </View>
      </Card>
    </TouchableOpacity>
  );

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
        {/* Stats Cards */}
        <View style={styles.statsContainer}>
          <Card variant="elevated" padding="md" style={styles.statCard}>
            <ThemedText
              size="2xl"
              weight="bold"
              style={{ color: theme.colors.primary }}
            >
              {stats?.total_predictions || 0}
            </ThemedText>
            <ThemedText variant="muted" size="xs">
              {t("history.totalPredictions")}
            </ThemedText>
          </Card>

          <Card variant="elevated" padding="md" style={styles.statCard}>
            <ThemedText
              size="2xl"
              weight="bold"
              style={{ color: theme.colors.success }}
            >
              {stats?.correct_predictions || 0}
            </ThemedText>
            <ThemedText variant="muted" size="xs">
              {t("history.correctPredictions")}
            </ThemedText>
          </Card>

          <Card variant="elevated" padding="md" style={styles.statCard}>
            <ThemedText
              size="2xl"
              weight="bold"
              style={{ color: theme.colors.accentGold }}
            >
              {stats?.accuracy || 0}%
            </ThemedText>
            <ThemedText variant="muted" size="xs">
              {t("history.accuracy")}
            </ThemedText>
          </Card>
        </View>

        {/* Predictions List */}
        <View style={styles.listHeader}>
          <View style={styles.listHeaderRow}>
            <Icon icon={ClipboardList} size={20} variant="primary" />
            <ThemedText size="lg" weight="semibold">
              {t("history.title")}
            </ThemedText>
          </View>
        </View>

        {predictions.length > 0 ? (
          predictions.map((prediction) => (
            <View key={prediction.id}>
              {renderPredictionItem({ item: prediction })}
            </View>
          ))
        ) : (
          <Card variant="outlined" padding="lg" style={styles.emptyCard}>
            <Icon icon={BarChart3} size={64} variant="muted" />
            <ThemedText variant="muted" style={styles.emptyText}>
              {t("history.noPredictions")}
            </ThemedText>
            <ThemedText variant="secondary" size="sm">
              {t("history.startPredicting")}
            </ThemedText>
          </Card>
        )}
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
  statsContainer: {
    flexDirection: "row",
    gap: 10,
    marginBottom: 24,
    flexWrap: "wrap",
  },
  statCard: {
    flex: 1,
    minWidth: 100,
    alignItems: "center",
    paddingVertical: 16,
    paddingHorizontal: 8,
  },
  listHeader: {
    marginBottom: 16,
  },
  listHeaderRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  predictionCard: {
    marginBottom: 14,
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 14,
    flexWrap: "wrap",
    gap: 6,
  },
  teamsRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 14,
    gap: 8,
  },
  teamInfo: {
    flex: 1,
    minWidth: 0,
  },
  scoreBox: {
    paddingHorizontal: 16,
    alignItems: "center",
    flexShrink: 0,
  },
  resultBadge: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 12,
    borderRadius: 10,
    borderWidth: 1,
    flexWrap: "wrap",
    gap: 8,
  },
  emptyCard: {
    alignItems: "center",
    paddingVertical: 48,
    paddingHorizontal: 24,
  },
  emptyIcon: {
    marginBottom: 16,
  },
  emptyText: {
    marginBottom: 10,
    textAlign: "center",
  },
  // ==========================================
  // RESPONSIVE STYLES FOR TABLETS AND DESKTOP
  // ==========================================
  predictionCardLarge: {
    borderRadius: 18,
    marginBottom: 18,
  },
  cardHeaderLarge: {
    marginBottom: 18,
    gap: 10,
  },
  teamsRowLarge: {
    marginBottom: 18,
    gap: 12,
  },
  scoreBoxLarge: {
    paddingHorizontal: 24,
  },
  resultBadgeLarge: {
    padding: 16,
    borderRadius: 14,
    gap: 12,
  },
});

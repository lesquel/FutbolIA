/**
 * GoalMind - Home Screen
 * Dashboard principal con scroll para móvil, layout de dos columnas para tablet
 */
import { useState, useEffect } from "react";
import {
  View,
  StyleSheet,
  Dimensions,
  Image,
  ActivityIndicator,
  TouchableOpacity,
  ScrollView,
  Platform,
} from "react-native";
import { useRouter } from "expo-router";
import { useTranslation } from "react-i18next";
import { Sparkles, Trophy, ChevronRight } from "lucide-react-native";

import { useTheme } from "@/src/theme";
import { ThemedView, ThemedText, Card, Button, Icon, TeamBadge } from "@/src/components/ui";
import { GoalMindChat, LeagueTable } from "@/src/components/features";
import { predictionsApi, Match } from "@/src/services/api";

const { width } = Dimensions.get("window");
const isTablet = width >= 768;

export default function HomeScreen() {
  const { theme } = useTheme();
  const { t } = useTranslation();
  const router = useRouter();

  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [showLeagueTable, setShowLeagueTable] = useState(false);

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
    }
  };

  const handleMatchPress = (match: Match) => {
    router.push({
      pathname: "/predict",
      params: {
        homeTeam: match.home_team.name,
        awayTeam: match.away_team.name,
      },
    });
  };

  const featuredMatch = matches[0];
  // Mostrar los siguientes 5 partidos
  const otherMatches = matches.slice(1, 6);

  /**
   * Formatea la fecha del partido a zona horaria de Ecuador (UTC-5) en formato compacto
   */
  const formatMatchDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return "";
      return date.toLocaleDateString("es-EC", {
        weekday: "short",
        day: "numeric",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "America/Guayaquil",
      });
    } catch {
      return "";
    }
  };

  if (loading) {
    return (
      <ThemedView variant="background" style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
        </View>
      </ThemedView>
    );
  }

  // En móvil usamos ScrollView, en tablet layout de dos columnas sin scroll
  const ContentWrapper = isTablet ? View : ScrollView;
  const contentWrapperProps = isTablet ? {} : { showsVerticalScrollIndicator: false };

  return (
    <ThemedView variant="background" style={styles.container}>
      <ContentWrapper 
        style={[styles.content, isTablet && styles.contentTablet]} 
        {...contentWrapperProps}
      >
        {/* Columna Principal */}
        <View style={[styles.mainColumn, isTablet && styles.mainColumnTablet]}>
          {/* Header */}
          <View style={styles.header}>
            <Image
              source={require("../../assets/images/GoalMind.png")}
              style={[styles.logoImage, isTablet && { width: 60, height: 60 }]}
              resizeMode="contain"
            />
            <View style={styles.headerText}>
              <ThemedText size="lg" weight="bold">{t("home.welcome")}</ThemedText>
              <ThemedText variant="secondary" size="xs">{t("home.subtitle")}</ThemedText>
            </View>
          </View>

          {/* GoalMind Compacto */}
          <GoalMindChat showGreeting={true} compact={true} />

          {/* Partido Destacado */}
          {featuredMatch && (
            <TouchableOpacity 
              style={[styles.featuredMatch, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}
              onPress={() => handleMatchPress(featuredMatch)}
              activeOpacity={0.7}
            >
              <View style={styles.matchHeader}>
                <ThemedText variant="muted" size="xs">{featuredMatch.league}</ThemedText>
                <ThemedText variant="muted" size="xs">
                  {new Date(featuredMatch.date).toLocaleDateString("es-EC", { 
                    weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
                    timeZone: "America/Guayaquil"
                  })}
                </ThemedText>
              </View>
              <View style={styles.matchTeams}>
                <TeamBadge name={featuredMatch.home_team.name} logoUrl={featuredMatch.home_team.logo_url} size="md" />
                <ThemedText variant="primary" weight="bold" size="lg">VS</ThemedText>
                <TeamBadge name={featuredMatch.away_team.name} logoUrl={featuredMatch.away_team.logo_url} size="md" />
              </View>
              <View style={[styles.predictBadge, { backgroundColor: theme.colors.primary + "20" }]}>
                <Icon icon={Sparkles} size={14} variant="primary" />
                <ThemedText variant="primary" size="xs" weight="semibold">Predecir</ThemedText>
              </View>
            </TouchableOpacity>
          )}

          {/* Botones de Acción */}
          <View style={styles.actionButtons}>
            <Button
              title={t("home.quickPredict")}
              variant="primary"
              size="sm"
              fullWidth
              onPress={() => router.push("/predict")}
              icon={Sparkles}
            />
            <Button
              title="Tabla de Posiciones"
              variant="outline"
              size="sm"
              fullWidth
              onPress={() => setShowLeagueTable(true)}
              icon={Trophy}
            />
          </View>
        </View>

        {/* Sección Próximos Partidos */}
        <View style={[styles.sideColumn, isTablet && styles.sideColumnTablet]}>
          <View style={styles.sideHeader}>
            <ThemedText size="sm" weight="semibold">Próximos Partidos</ThemedText>
            <TouchableOpacity onPress={() => router.push("/predict")}>
              <ThemedText variant="primary" size="xs">Ver más</ThemedText>
            </TouchableOpacity>
          </View>
          
          {otherMatches.map((match) => (
            <TouchableOpacity
              key={match.id}
              style={[styles.miniMatch, { backgroundColor: theme.colors.surface, borderColor: theme.colors.border }]}
              onPress={() => handleMatchPress(match)}
              activeOpacity={0.7}
            >
              <View style={styles.miniMatchInfo}>
                <View style={styles.miniMatchHeader}>
                  <ThemedText variant="muted" size="xs">{match.league}</ThemedText>
                  <ThemedText variant="primary" size="xs">{formatMatchDate(match.date)}</ThemedText>
                </View>
                <View style={styles.miniMatchTeams}>
                  <ThemedText size="sm" weight="medium" numberOfLines={1} style={{ flex: 1 }}>
                    {match.home_team.name.replace(" FC", "")}
                  </ThemedText>
                  <ThemedText variant="primary" size="xs" weight="bold">vs</ThemedText>
                  <ThemedText size="sm" weight="medium" numberOfLines={1} style={{ flex: 1, textAlign: "right" }}>
                    {match.away_team.name.replace(" FC", "")}
                  </ThemedText>
                </View>
              </View>
              <Icon icon={ChevronRight} size={16} variant="muted" />
            </TouchableOpacity>
          ))}

          {otherMatches.length === 0 && (
            <Card padding="sm">
              <ThemedText variant="muted" size="xs" style={{ textAlign: "center" }}>
                No hay más partidos
              </ThemedText>
            </Card>
          )}
        </View>
      </ContentWrapper>

      {/* League Table Modal */}
      <LeagueTable
        visible={showLeagueTable}
        onClose={() => setShowLeagueTable(false)}
      />
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  content: {
    flex: 1,
    padding: 12,
    flexDirection: "column",
  },
  contentTablet: {
    flexDirection: "row",
    gap: 16,
  },
  mainColumn: {
    flex: 1,
  },
  mainColumnTablet: {
    flex: 0.6,
  },
  sideColumn: {
    marginTop: 8,
  },
  sideColumnTablet: {
    flex: 0.4,
    marginTop: 0,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    marginBottom: 8,
  },
  headerText: {
    flex: 1,
  },
  logoImage: {
    width: 40,
    height: 40,
  },
  featuredMatch: {
    borderRadius: 12,
    borderWidth: 1,
    padding: 12,
    marginBottom: 10,
  },
  matchHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 8,
  },
  matchTeams: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-around",
    marginBottom: 8,
  },
  predictBadge: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 4,
    paddingVertical: 6,
    borderRadius: 8,
  },
  actionButtons: {
    gap: 8,
    marginBottom: 8,
  },
  sideHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  miniMatch: {
    flexDirection: "row",
    alignItems: "center",
    borderRadius: 8,
    borderWidth: 1,
    padding: 8,
    marginBottom: 4,
  },
  miniMatchInfo: {
    flex: 1,
  },
  miniMatchHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 2,
  },
  miniMatchTeams: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
});

/**
 * PredictionCard - Display GoalMind's prediction with analysis and player details
 */
import { memo, useMemo } from "react";
import {
  View,
  StyleSheet,
  ScrollView,
  useWindowDimensions,
} from "react-native";
import {
  Sparkles,
  BarChart3,
  Target,
  Star,
  Brain,
  Home,
  Bus,
  Trophy,
} from "lucide-react-native";
import { useTheme } from "@/src/theme";
import { useTranslation } from "@/src/i18n/i18n";
import {
  ThemedText,
  Card,
  ConfidenceRing,
  TeamBadge,
  Button,
  Icon,
} from "@/src/components/ui";
import { Prediction, Player } from "@/src/services/api";

interface PredictionCardProps {
  prediction: Prediction;
  onSave?: () => void;
  onShare?: () => void;
  onNewPrediction?: () => void;
}

// Helper to get position color
const getPositionColor = (position: string, theme: any) => {
  if (position === "GK") return "#FFA500"; // Orange
  if (["CB", "LB", "RB", "LWB", "RWB"].includes(position)) return "#3498db"; // Blue
  if (["CDM", "CM", "CAM"].includes(position)) return "#27ae60"; // Green
  return "#e74c3c"; // Red for attackers
};

// Player Row Component - Memoized for performance
const PlayerRow = memo(({ player, theme }: { player: Player; theme: any }) => (
  <View style={styles.playerRow}>
    <View
      style={[
        styles.positionBadge,
        { backgroundColor: getPositionColor(player.position, theme) },
      ]}
    >
      <ThemedText size="xs" style={{ color: "#fff", fontWeight: "bold" }}>
        {player.position}
      </ThemedText>
    </View>
    <ThemedText size="sm" weight="medium" style={styles.playerName}>
      {player.name}
    </ThemedText>
    <View
      style={[
        styles.ovrBadge,
        { backgroundColor: theme.colors.primary + "20" },
      ]}
    >
      <ThemedText
        size="xs"
        weight="bold"
        style={{ color: theme.colors.primary }}
      >
        {player.overall_rating}
      </ThemedText>
    </View>
  </View>
));
PlayerRow.displayName = "PlayerRow";

// Team Squad Section - Memoized for performance
const TeamSquadSection = memo(
  ({
    teamName,
    players,
    theme,
    icon: IconComponent,
  }: {
    teamName: string;
    players: Player[];
    theme: any;
    icon: any;
  }) => {
    const avgOvr = useMemo(() => {
      if (players.length === 0) return 0;
      return Math.round(
        players.reduce((a, p) => a + p.overall_rating, 0) / players.length,
      );
    }, [players]);

    return (
      <View style={styles.squadSection}>
        <View style={styles.squadTitleRow}>
          <Icon icon={IconComponent} size={20} variant="primary" />
          <ThemedText size="md" weight="semibold" style={styles.squadTitle}>
            {teamName}
          </ThemedText>
        </View>
        <View
          style={[
            styles.squadBox,
            { backgroundColor: theme.colors.surfaceSecondary },
          ]}
        >
          {players.length > 0 ? (
            players
              .slice(0, 11)
              .map((player, index) => (
                <PlayerRow key={index} player={player} theme={theme} />
              ))
          ) : (
            <ThemedText variant="muted" size="sm">
              Sin datos de jugadores
            </ThemedText>
          )}
        </View>
        {players.length > 0 && (
          <View style={styles.statsRow}>
            <Icon icon={BarChart3} size={14} variant="muted" />
            <ThemedText variant="muted" size="xs" style={styles.statsText}>
              Promedio OVR: {avgOvr}
            </ThemedText>
          </View>
        )}
      </View>
    );
  },
);
TeamSquadSection.displayName = "TeamSquadSection";

export const PredictionCard = memo(function PredictionCard({
  prediction,
  onSave,
  onShare,
  onNewPrediction,
}: PredictionCardProps) {
  const { theme, isDark } = useTheme();
  const { t } = useTranslation();

  // Responsive breakpoints
  const { width: screenWidth } = useWindowDimensions();
  const isTablet = screenWidth >= 768;
  const isDesktop = screenWidth >= 1024;
  const isLargeScreen = isTablet || isDesktop;

  const { result, match } = prediction;

  const isHomeWinner = result.winner === match.home_team.name;
  const isAwayWinner = result.winner === match.away_team.name;
  const isDraw =
    result.winner.toLowerCase().includes("empate") ||
    result.winner.toLowerCase().includes("draw");

  return (
    <Card variant="elevated" padding="lg">
      {/* Header - GoalMind's Title */}
      <View style={[styles.header, isLargeScreen && styles.headerLarge]}>
        <View style={styles.goalMindIcon}>
          <Icon
            icon={Sparkles}
            size={isLargeScreen ? 40 : 24}
            variant="primary"
          />
        </View>
        <View style={styles.headerText}>
          <ThemedText size={isLargeScreen ? "2xl" : "lg"} weight="bold">
            {t("prediction.title")}
          </ThemedText>
          <ThemedText variant="muted" size={isLargeScreen ? "base" : "xs"}>
            Análisis táctico con IA
          </ThemedText>
        </View>
      </View>

      {/* Match Overview */}
      <View
        style={[
          styles.matchOverview,
          isLargeScreen && styles.matchOverviewLarge,
        ]}
      >
        <TeamBadge
          name={match.home_team.name}
          logoUrl={match.home_team.logo_url}
          size={isLargeScreen ? "lg" : "sm"}
        />

        <View
          style={[
            styles.scoreContainer,
            isLargeScreen && styles.scoreContainerLarge,
          ]}
        >
          <ThemedText
            size={isLargeScreen ? "3xl" : "2xl"}
            weight="bold"
            style={{ color: theme.colors.primary }}
          >
            {result.predicted_score}
          </ThemedText>
          <ThemedText variant="muted" size={isLargeScreen ? "sm" : "xs"}>
            {t("prediction.score")}
          </ThemedText>
        </View>

        <TeamBadge
          name={match.away_team.name}
          logoUrl={match.away_team.logo_url}
          size={isLargeScreen ? "lg" : "sm"}
        />
      </View>

      {/* Winner Badge */}
      <View
        style={[
          styles.winnerBadge,
          isLargeScreen && styles.winnerBadgeLarge,
          {
            backgroundColor: isDraw
              ? theme.colors.warning + "20"
              : theme.colors.primary + "20",
            borderColor: isDraw ? theme.colors.warning : theme.colors.primary,
          },
        ]}
      >
        <Icon icon={Trophy} size={isLargeScreen ? 26 : 16} variant="primary" />
        <ThemedText
          variant="primary"
          weight="bold"
          size={isLargeScreen ? "lg" : "sm"}
          style={styles.winnerText}
        >
          {t("prediction.winner")}: {result.winner}
        </ThemedText>
      </View>

      {/* Confidence Ring */}
      <View
        style={[
          styles.confidenceSection,
          isLargeScreen && styles.confidenceSectionLarge,
        ]}
      >
        <ConfidenceRing
          percentage={result.confidence}
          size={isLargeScreen ? 180 : 110}
          label={t("prediction.confidence")}
        />
      </View>

      {/* Tactical Analysis */}
      <View
        style={[
          styles.analysisSection,
          isLargeScreen && styles.analysisSectionLarge,
        ]}
      >
        <View style={styles.sectionTitleRow}>
          <Icon
            icon={BarChart3}
            size={isLargeScreen ? 24 : 16}
            variant="primary"
          />
          <ThemedText
            size={isLargeScreen ? "xl" : "base"}
            weight="semibold"
            style={styles.sectionTitle}
          >
            {t("prediction.analysis")}
          </ThemedText>
        </View>
        <View
          style={[
            styles.analysisBox,
            isLargeScreen && styles.analysisBoxLarge,
            { backgroundColor: theme.colors.surfaceSecondary },
          ]}
        >
          <ThemedText
            variant="secondary"
            size={isLargeScreen ? "base" : "sm"}
            style={[
              styles.analysisText,
              isLargeScreen && styles.analysisTextLarge,
            ]}
          >
            {result.reasoning}
          </ThemedText>
        </View>
      </View>

      {/* Key Factors */}
      {result.key_factors && result.key_factors.length > 0 && (
        <View style={styles.factorsSection}>
          <View style={styles.sectionTitleRow}>
            <Icon
              icon={Target}
              size={isLargeScreen ? 20 : 16}
              variant="primary"
            />
            <ThemedText
              size={isLargeScreen ? "lg" : "base"}
              weight="semibold"
              style={styles.sectionTitle}
            >
              {t("prediction.keyFactors")}
            </ThemedText>
          </View>
          {result.key_factors.map((factor, index) => (
            <View
              key={index}
              style={[
                styles.factorItem,
                { borderLeftColor: theme.colors.primary },
              ]}
            >
              <ThemedText variant="secondary" size="sm">
                {factor}
              </ThemedText>
            </View>
          ))}
        </View>
      )}

      {/* Star Players */}
      <View style={styles.starsSection}>
        <View style={styles.starPlayer}>
          <View style={styles.starPlayerHeader}>
            <Icon icon={Star} size={16} variant="warning" />
            <ThemedText variant="muted" size="xs">
              {t("prediction.starPlayerHome")}
            </ThemedText>
          </View>
          <ThemedText weight="semibold">
            {result.star_player_home || "N/A"}
          </ThemedText>
        </View>

        <View
          style={[styles.divider, { backgroundColor: theme.colors.border }]}
        />

        <View style={styles.starPlayer}>
          <View style={styles.starPlayerHeader}>
            <Icon icon={Star} size={16} variant="warning" />
            <ThemedText variant="muted" size="xs">
              {t("prediction.starPlayerAway")}
            </ThemedText>
          </View>
          <ThemedText weight="semibold">
            {result.star_player_away || "N/A"}
          </ThemedText>
        </View>
      </View>

      {/* Team Squads - Detailed Player Analytics */}
      {prediction.context && (
        <View
          style={[
            styles.squadsContainer,
            isLargeScreen && styles.squadsContainerLarge,
          ]}
        >
          <ThemedText
            size={isLargeScreen ? "xl" : "base"}
            weight="semibold"
            style={styles.sectionTitle}
          >
            👥 Plantillas Analizadas
          </ThemedText>

          <View
            style={[styles.squadsGrid, isLargeScreen && styles.squadsGridLarge]}
          >
            <TeamSquadSection
              teamName={match.home_team.name}
              players={prediction.context.home_players || []}
              theme={theme}
              icon={Home}
            />
            <TeamSquadSection
              teamName={match.away_team.name}
              players={prediction.context.away_players || []}
              theme={theme}
              icon={Bus}
            />
          </View>
        </View>
      )}

      {/* Tactical Insight */}
      {result.tactical_insight && (
        <View style={styles.insightSection}>
          <View style={styles.sectionTitleRow}>
            <Icon
              icon={Brain}
              size={isLargeScreen ? 20 : 16}
              variant="primary"
            />
            <ThemedText
              size={isLargeScreen ? "lg" : "base"}
              weight="semibold"
              style={styles.sectionTitle}
            >
              Insight Táctico
            </ThemedText>
          </View>
          <View
            style={[
              styles.analysisBox,
              { backgroundColor: theme.colors.primary + "10" },
            ]}
          >
            <ThemedText variant="secondary" size="sm">
              {result.tactical_insight}
            </ThemedText>
          </View>
        </View>
      )}

      {/* Action Buttons */}
      <View style={[styles.actions, isLargeScreen && styles.actionsLarge]}>
        {onSave && (
          <Button
            title={t("prediction.savePrediction")}
            variant="primary"
            size={isLargeScreen ? "lg" : "md"}
            onPress={onSave}
            style={styles.actionButton}
          />
        )}
        {onNewPrediction && (
          <Button
            title={t("prediction.newPrediction")}
            variant="outline"
            size={isLargeScreen ? "lg" : "md"}
            onPress={onNewPrediction}
            style={styles.actionButton}
          />
        )}
      </View>
    </Card>
  );
});

const styles = StyleSheet.create({
  header: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 10,
  },
  goalMindIcon: {
    marginRight: 8,
  },
  headerText: {
    flex: 1,
  },
  matchOverview: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 0,
    marginBottom: 10,
  },
  scoreContainer: {
    alignItems: "center",
    paddingHorizontal: 8,
  },
  winnerBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 10,
    borderWidth: 1,
    justifyContent: "center",
    marginBottom: 12,
  },
  winnerText: {
    marginLeft: 4,
    flexShrink: 1,
  },
  sectionTitleRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    marginBottom: 8,
  },
  squadTitleRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 8,
  },
  statsRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    marginTop: 8,
  },
  statsText: {
    marginLeft: 4,
  },
  starPlayerHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    marginBottom: 4,
  },
  confidenceSection: {
    alignItems: "center",
    marginVertical: 10,
  },
  analysisSection: {
    marginTop: 6,
  },
  sectionTitle: {
    marginBottom: 6,
    flexShrink: 1,
  },
  analysisBox: {
    padding: 10,
    borderRadius: 10,
  },
  analysisText: {
    lineHeight: 20,
  },
  factorsSection: {
    marginTop: 10,
  },
  factorItem: {
    paddingLeft: 10,
    paddingVertical: 4,
    borderLeftWidth: 3,
    marginBottom: 4,
  },
  starsSection: {
    flexDirection: "row",
    marginTop: 10,
    paddingTop: 10,
  },
  starPlayer: {
    flex: 1,
    alignItems: "center",
    paddingHorizontal: 6,
  },
  divider: {
    width: 1,
    height: "100%",
    marginHorizontal: 6,
  },
  // Squad styles
  squadsContainer: {
    marginTop: 12,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: "rgba(0,0,0,0.1)",
  },
  squadsGrid: {
    gap: 8,
  },
  squadSection: {
    marginBottom: 6,
  },
  squadTitle: {
    marginBottom: 8,
  },
  squadBox: {
    padding: 8,
    borderRadius: 10,
  },
  playerRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 4,
    borderBottomWidth: 1,
    borderBottomColor: "rgba(0,0,0,0.05)",
  },
  positionBadge: {
    width: 32,
    height: 18,
    borderRadius: 4,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 6,
  },
  playerName: {
    flex: 1,
  },
  ovrBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 5,
  },
  insightSection: {
    marginTop: 10,
  },
  actions: {
    flexDirection: "column",
    gap: 8,
    marginTop: 12,
  },
  actionButton: {
    flex: 1,
  },
  // ==========================================
  // RESPONSIVE STYLES FOR TABLETS AND DESKTOP
  // ==========================================
  headerLarge: {
    marginBottom: 28,
  },
  matchOverviewLarge: {
    paddingHorizontal: 24,
    marginBottom: 28,
  },
  scoreContainerLarge: {
    paddingHorizontal: 24,
  },
  winnerBadgeLarge: {
    paddingVertical: 18,
    paddingHorizontal: 28,
    borderRadius: 18,
    marginBottom: 32,
  },
  confidenceSectionLarge: {
    marginVertical: 32,
  },
  analysisSectionLarge: {
    marginTop: 20,
  },
  analysisBoxLarge: {
    padding: 24,
    borderRadius: 18,
  },
  analysisTextLarge: {
    lineHeight: 28,
  },
  squadsContainerLarge: {
    marginTop: 36,
    paddingTop: 28,
  },
  squadsGridLarge: {
    flexDirection: "row",
    gap: 24,
  },
  actionsLarge: {
    flexDirection: "row",
    gap: 16,
    marginTop: 36,
  },
});

/**
 * PredictionCard - Display Dixie's prediction with analysis and player details
 */
import { View, StyleSheet, ScrollView } from "react-native";
import { useTheme } from "@/src/theme";
import { useTranslation } from "@/src/i18n/i18n";
import {
  ThemedText,
  Card,
  ConfidenceRing,
  TeamBadge,
  Button,
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

// Player Row Component
const PlayerRow = ({ player, theme }: { player: Player; theme: any }) => (
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
);

// Team Squad Section
const TeamSquadSection = ({
  teamName,
  players,
  theme,
  emoji,
}: {
  teamName: string;
  players: Player[];
  theme: any;
  emoji: string;
}) => (
  <View style={styles.squadSection}>
    <ThemedText size="md" weight="semibold" style={styles.squadTitle}>
      {emoji} {teamName}
    </ThemedText>
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
        <ThemedText variant="muted" size="xs">
          📊 Promedio OVR:{" "}
          {Math.round(
            players.reduce((a, p) => a + p.overall_rating, 0) / players.length
          )}
        </ThemedText>
      </View>
    )}
  </View>
);

export function PredictionCard({
  prediction,
  onSave,
  onShare,
  onNewPrediction,
}: PredictionCardProps) {
  const { theme, isDark } = useTheme();
  const { t } = useTranslation();

  const { result, match } = prediction;

  const isHomeWinner = result.winner === match.home_team.name;
  const isAwayWinner = result.winner === match.away_team.name;
  const isDraw =
    result.winner.toLowerCase().includes("empate") ||
    result.winner.toLowerCase().includes("draw");

  return (
    <Card variant="elevated" padding="lg">
      {/* Header - Dixie's Title */}
      <View style={styles.header}>
        <View style={styles.dixieIcon}>
          <ThemedText size="2xl">🔮</ThemedText>
        </View>
        <View style={styles.headerText}>
          <ThemedText size="xl" weight="bold">
            {t("prediction.title")}
          </ThemedText>
          <ThemedText variant="muted" size="sm">
            Análisis táctico con IA
          </ThemedText>
        </View>
      </View>

      {/* Match Overview */}
      <View style={styles.matchOverview}>
        <TeamBadge
          name={match.home_team.name}
          logoUrl={match.home_team.logo_url}
          size="md"
        />

        <View style={styles.scoreContainer}>
          <ThemedText
            size="3xl"
            weight="bold"
            style={{ color: theme.colors.primary }}
          >
            {result.predicted_score}
          </ThemedText>
          <ThemedText variant="muted" size="xs">
            {t("prediction.score")}
          </ThemedText>
        </View>

        <TeamBadge
          name={match.away_team.name}
          logoUrl={match.away_team.logo_url}
          size="md"
        />
      </View>

      {/* Winner Badge */}
      <View
        style={[
          styles.winnerBadge,
          {
            backgroundColor: isDraw
              ? theme.colors.warning + "20"
              : theme.colors.primary + "20",
            borderColor: isDraw ? theme.colors.warning : theme.colors.primary,
          },
        ]}
      >
        <ThemedText variant="primary" weight="bold">
          🏆 {t("prediction.winner")}: {result.winner}
        </ThemedText>
      </View>

      {/* Confidence Ring */}
      <View style={styles.confidenceSection}>
        <ConfidenceRing
          percentage={result.confidence}
          size={140}
          label={t("prediction.confidence")}
        />
      </View>

      {/* Tactical Analysis */}
      <View style={styles.analysisSection}>
        <ThemedText size="lg" weight="semibold" style={styles.sectionTitle}>
          📊 {t("prediction.analysis")}
        </ThemedText>
        <View
          style={[
            styles.analysisBox,
            { backgroundColor: theme.colors.surfaceSecondary },
          ]}
        >
          <ThemedText variant="secondary" size="sm" style={styles.analysisText}>
            {result.reasoning}
          </ThemedText>
        </View>
      </View>

      {/* Key Factors */}
      {result.key_factors && result.key_factors.length > 0 && (
        <View style={styles.factorsSection}>
          <ThemedText size="lg" weight="semibold" style={styles.sectionTitle}>
            🎯 {t("prediction.keyFactors")}
          </ThemedText>
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
          <ThemedText variant="muted" size="xs">
            ⭐ {t("prediction.starPlayerHome")}
          </ThemedText>
          <ThemedText weight="semibold">
            {result.star_player_home || "N/A"}
          </ThemedText>
        </View>

        <View
          style={[styles.divider, { backgroundColor: theme.colors.border }]}
        />

        <View style={styles.starPlayer}>
          <ThemedText variant="muted" size="xs">
            ⭐ {t("prediction.starPlayerAway")}
          </ThemedText>
          <ThemedText weight="semibold">
            {result.star_player_away || "N/A"}
          </ThemedText>
        </View>
      </View>

      {/* Team Squads - Detailed Player Analytics */}
      {prediction.context && (
        <View style={styles.squadsContainer}>
          <ThemedText size="lg" weight="semibold" style={styles.sectionTitle}>
            👥 Plantillas Analizadas
          </ThemedText>

          <View style={styles.squadsGrid}>
            <TeamSquadSection
              teamName={match.home_team.name}
              players={prediction.context.home_players || []}
              theme={theme}
              emoji="🏠"
            />
            <TeamSquadSection
              teamName={match.away_team.name}
              players={prediction.context.away_players || []}
              theme={theme}
              emoji="🚌"
            />
          </View>
        </View>
      )}

      {/* Tactical Insight */}
      {result.tactical_insight && (
        <View style={styles.insightSection}>
          <ThemedText size="lg" weight="semibold" style={styles.sectionTitle}>
            🧠 Insight Táctico
          </ThemedText>
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
      <View style={styles.actions}>
        {onSave && (
          <Button
            title={t("prediction.savePrediction")}
            variant="primary"
            size="md"
            onPress={onSave}
            style={styles.actionButton}
          />
        )}
        {onNewPrediction && (
          <Button
            title={t("prediction.newPrediction")}
            variant="outline"
            size="md"
            onPress={onNewPrediction}
            style={styles.actionButton}
          />
        )}
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 20,
  },
  dixieIcon: {
    marginRight: 12,
  },
  headerText: {
    flex: 1,
  },
  matchOverview: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 16,
    marginBottom: 16,
  },
  scoreContainer: {
    alignItems: "center",
  },
  winnerBadge: {
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 12,
    borderWidth: 1,
    alignItems: "center",
    marginBottom: 20,
  },
  confidenceSection: {
    alignItems: "center",
    marginVertical: 20,
  },
  analysisSection: {
    marginTop: 8,
  },
  sectionTitle: {
    marginBottom: 12,
  },
  analysisBox: {
    padding: 16,
    borderRadius: 12,
  },
  analysisText: {
    lineHeight: 22,
  },
  factorsSection: {
    marginTop: 20,
  },
  factorItem: {
    paddingLeft: 12,
    paddingVertical: 8,
    borderLeftWidth: 3,
    marginBottom: 8,
  },
  starsSection: {
    flexDirection: "row",
    marginTop: 20,
    paddingTop: 16,
  },
  starPlayer: {
    flex: 1,
    alignItems: "center",
  },
  divider: {
    width: 1,
    height: "100%",
    marginHorizontal: 8,
  },
  // Squad styles
  squadsContainer: {
    marginTop: 24,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: "rgba(0,0,0,0.1)",
  },
  squadsGrid: {
    gap: 16,
  },
  squadSection: {
    marginBottom: 12,
  },
  squadTitle: {
    marginBottom: 8,
  },
  squadBox: {
    padding: 12,
    borderRadius: 12,
  },
  playerRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: "rgba(0,0,0,0.05)",
  },
  positionBadge: {
    width: 32,
    height: 20,
    borderRadius: 4,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 8,
  },
  playerName: {
    flex: 1,
  },
  ovrBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 8,
  },
  statsRow: {
    marginTop: 8,
    alignItems: "flex-end",
  },
  insightSection: {
    marginTop: 20,
  },
  actions: {
    flexDirection: "row",
    gap: 12,
    marginTop: 24,
  },
  actionButton: {
    flex: 1,
  },
});

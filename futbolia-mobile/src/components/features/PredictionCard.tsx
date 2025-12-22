/**
 * PredictionCard - Display Dixie's prediction with analysis
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
import { Prediction } from "@/src/services/api";

interface PredictionCardProps {
  prediction: Prediction;
  onSave?: () => void;
  onShare?: () => void;
  onNewPrediction?: () => void;
}

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
  actions: {
    flexDirection: "row",
    gap: 12,
    marginTop: 24,
  },
  actionButton: {
    flex: 1,
  },
});

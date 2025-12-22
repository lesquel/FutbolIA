/**
 * FutbolIA - Predict Screen
 * Main prediction interface with team selection
 */
import { useState } from "react";
import {
  ScrollView,
  View,
  StyleSheet,
  ActivityIndicator,
  Dimensions,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { useLocalSearchParams } from "expo-router";
import { useTranslation } from "react-i18next";

import { useTheme } from "@/src/theme";
import { ThemedView, ThemedText, Card, Button } from "@/src/components/ui";
import {
  TeamSelector,
  PredictionCard,
  DixieChat,
} from "@/src/components/features";
import { predictionsApi, Prediction } from "@/src/services/api";

const { width } = Dimensions.get("window");
const isTablet = width >= 768;

export default function PredictScreen() {
  const { theme } = useTheme();
  const { t } = useTranslation();
  const params = useLocalSearchParams();

  // State
  const [homeTeam, setHomeTeam] = useState<string | null>(
    (params.homeTeam as string) || null
  );
  const [awayTeam, setAwayTeam] = useState<string | null>(
    (params.awayTeam as string) || null
  );
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canPredict = homeTeam && awayTeam && homeTeam !== awayTeam;

  const handlePredict = async () => {
    if (!homeTeam || !awayTeam) return;

    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const response = await predictionsApi.predict(homeTeam, awayTeam, "es");

      if (response.success && response.data?.prediction) {
        setPrediction(response.data.prediction);
      } else {
        setError(response.error || "Error generando predicción");
      }
    } catch (err) {
      setError("Error de conexión. Verifica que el servidor esté activo.");
      console.log("Prediction error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleNewPrediction = () => {
    setPrediction(null);
    setHomeTeam(null);
    setAwayTeam(null);
    setError(null);
  };

  return (
    <ThemedView variant="background" style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={styles.container}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          {/* Responsive Layout */}
          <View style={[styles.content, isTablet && styles.contentTablet]}>
            {/* Left Column - Team Selection */}
            <View style={[styles.column, isTablet && styles.columnTablet]}>
              {/* Header */}
              <View style={styles.header}>
                <ThemedText size="2xl" weight="bold">
                  🔮 {t("prediction.newPrediction")}
                </ThemedText>
                <ThemedText variant="secondary">
                  {t("home.selectTeams")}
                </ThemedText>
              </View>

              {/* Dixie Chat */}
              <DixieChat
                isLoading={loading}
                message={prediction?.result?.reasoning}
                showGreeting={!prediction && !loading}
              />

              {/* Team Selection (only show if no prediction yet) */}
              {!prediction && (
                <Card
                  variant="default"
                  padding="lg"
                  style={styles.selectionCard}
                >
                  {/* Home Team */}
                  <TeamSelector
                    label={`🏠 ${t("prediction.selectHomeTeam")}`}
                    selectedTeam={homeTeam}
                    onSelectTeam={setHomeTeam}
                    excludeTeam={awayTeam}
                  />

                  {/* VS Indicator */}
                  <View style={styles.vsIndicator}>
                    <View
                      style={[
                        styles.vsLine,
                        { backgroundColor: theme.colors.border },
                      ]}
                    />
                    <ThemedText
                      variant="primary"
                      size="xl"
                      weight="bold"
                      style={styles.vsText}
                    >
                      {t("prediction.vs")}
                    </ThemedText>
                    <View
                      style={[
                        styles.vsLine,
                        { backgroundColor: theme.colors.border },
                      ]}
                    />
                  </View>

                  {/* Away Team */}
                  <TeamSelector
                    label={`🚌 ${t("prediction.selectAwayTeam")}`}
                    selectedTeam={awayTeam}
                    onSelectTeam={setAwayTeam}
                    excludeTeam={homeTeam}
                  />

                  {/* Error Message */}
                  {error && (
                    <View
                      style={[
                        styles.errorBox,
                        { backgroundColor: theme.colors.error + "20" },
                      ]}
                    >
                      <ThemedText variant="error" size="sm">
                        ⚠️ {error}
                      </ThemedText>
                    </View>
                  )}

                  {/* Predict Button */}
                  <Button
                    title={
                      loading
                        ? t("prediction.generating")
                        : `🔮 ${t("prediction.predict")}`
                    }
                    variant="primary"
                    size="lg"
                    fullWidth
                    disabled={!canPredict || loading}
                    loading={loading}
                    onPress={handlePredict}
                    style={styles.predictButton}
                  />
                </Card>
              )}
            </View>

            {/* Right Column - Prediction Result (or second column on tablet) */}
            <View style={[styles.column, isTablet && styles.columnTablet]}>
              {/* Loading State */}
              {loading && (
                <Card
                  variant="outlined"
                  padding="lg"
                  style={styles.loadingCard}
                >
                  <ActivityIndicator
                    size="large"
                    color={theme.colors.primary}
                  />
                  <ThemedText variant="secondary" style={styles.loadingText}>
                    {t("prediction.generating")}
                  </ThemedText>
                  <ThemedText variant="muted" size="sm">
                    Analizando estadísticas y atributos de jugadores...
                  </ThemedText>
                </Card>
              )}

              {/* Prediction Result */}
              {prediction && !loading && (
                <PredictionCard
                  prediction={prediction}
                  onNewPrediction={handleNewPrediction}
                  onSave={() => {
                    // Already saved by backend
                    console.log("Prediction saved:", prediction.id);
                  }}
                />
              )}

              {/* Empty State (Tablet only) */}
              {isTablet && !prediction && !loading && (
                <Card variant="outlined" padding="lg" style={styles.emptyCard}>
                  <ThemedText size="3xl" style={styles.emptyIcon}>
                    ⚽
                  </ThemedText>
                  <ThemedText variant="muted" style={styles.emptyText}>
                    Selecciona dos equipos para ver la predicción de Dixie
                  </ThemedText>
                </Card>
              )}
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
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
  column: {
    flex: 1,
  },
  columnTablet: {
    flex: 0.5,
  },
  header: {
    marginBottom: 16,
  },
  selectionCard: {
    marginTop: 8,
  },
  vsIndicator: {
    flexDirection: "row",
    alignItems: "center",
    marginVertical: 16,
  },
  vsLine: {
    flex: 1,
    height: 1,
  },
  vsText: {
    marginHorizontal: 16,
  },
  errorBox: {
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  predictButton: {
    marginTop: 8,
  },
  loadingCard: {
    alignItems: "center",
    justifyContent: "center",
    minHeight: 200,
  },
  loadingText: {
    marginTop: 16,
    marginBottom: 8,
  },
  emptyCard: {
    alignItems: "center",
    justifyContent: "center",
    minHeight: 300,
  },
  emptyIcon: {
    marginBottom: 16,
  },
  emptyText: {
    textAlign: "center",
  },
});

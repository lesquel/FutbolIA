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
  TouchableOpacity,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useTranslation } from "react-i18next";
import { FontAwesome } from "@expo/vector-icons";

import { useTheme } from "@/src/theme";
import { useAuth } from "@/src/context";
import { ThemedView, ThemedText, Card, Button } from "@/src/components/ui";
import {
  TeamSelector,
  TeamStatsCard,
  PredictionCard,
  DixieChat,
} from "@/src/components/features";
import { predictionsApi, Prediction } from "@/src/services/api";

const { width } = Dimensions.get("window");
const isTablet = width >= 768;

export default function PredictScreen() {
  const { theme } = useTheme();
  const { t } = useTranslation();
  const { user } = useAuth();
  const router = useRouter();
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
  const [showAuthPrompt, setShowAuthPrompt] = useState(false);

  const canPredict = homeTeam && awayTeam && homeTeam !== awayTeam;

  const handlePredict = async () => {
    if (!homeTeam || !awayTeam) return;

    // Check if user is authenticated
    if (!user) {
      setShowAuthPrompt(true);
      return;
    }

    setLoading(true);
    setError(null);
    setPrediction(null);
    setShowAuthPrompt(false);

    try {
      const response = await predictionsApi.predict(homeTeam, awayTeam, "es");

      if (response.success && response.data?.prediction) {
        // Include player context in the prediction object
        const predictionWithContext = {
          ...response.data.prediction,
          context: response.data.context,
        };
        setPrediction(predictionWithContext);
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
    setShowAuthPrompt(false);
  };

  // Auth Prompt Component
  const AuthPrompt = () => (
    <Card variant="outlined" padding="lg" style={styles.authCard}>
      <View
        style={[
          styles.authIconContainer,
          { backgroundColor: theme.colors.primary + "20" },
        ]}
      >
        <FontAwesome name="lock" size={32} color={theme.colors.primary} />
      </View>
      <ThemedText size="xl" weight="bold" style={styles.authTitle}>
        {t("auth.loginRequired")}
      </ThemedText>
      <ThemedText variant="secondary" style={styles.authDescription}>
        {t("auth.loginToPredict")}
      </ThemedText>
      <View style={styles.authButtons}>
        <Button
          title={t("auth.login")}
          variant="primary"
          size="lg"
          fullWidth
          onPress={() => router.push("/login")}
          style={styles.authButton}
        />
        <Button
          title={t("auth.createAccount")}
          variant="outline"
          size="md"
          fullWidth
          onPress={() => router.push("/register")}
        />
      </View>
      <TouchableOpacity
        onPress={() => setShowAuthPrompt(false)}
        style={styles.dismissButton}
      >
        <ThemedText variant="muted" size="sm">
          {t("common.cancel")}
        </ThemedText>
      </TouchableOpacity>
    </Card>
  );

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

              {/* Team Selection (only show if no prediction yet and no auth prompt) */}
              {!prediction && !showAuthPrompt && (
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

                  {/* Home Team Stats */}
                  <TeamStatsCard teamName={homeTeam} emoji="🏠" />

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

                  {/* Away Team Stats */}
                  <TeamStatsCard teamName={awayTeam} emoji="🚌" />

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
              {/* Auth Prompt */}
              {showAuthPrompt && <AuthPrompt />}

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
  authCard: {
    alignItems: "center",
    justifyContent: "center",
    marginTop: 16,
  },
  authIconContainer: {
    width: 64,
    height: 64,
    borderRadius: 32,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 16,
  },
  authTitle: {
    textAlign: "center",
    marginBottom: 8,
  },
  authDescription: {
    textAlign: "center",
    marginBottom: 24,
  },
  authButtons: {
    width: "100%",
    gap: 12,
  },
  authButton: {
    marginBottom: 0,
  },
  dismissButton: {
    marginTop: 16,
    padding: 8,
  },
});

/**
 * FutbolIA - Predict Screen
 * Main prediction interface with team selection
 */
import { useState, useCallback, useMemo } from "react";
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
import { Lock, Sparkles, Home, Bus, AlertCircle } from "lucide-react-native";

import { useTheme } from "@/src/theme";
import { useAuth } from "@/src/context";
import { ThemedView, ThemedText, Card, Button, Icon } from "@/src/components/ui";
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
  const [homeTeamData, setHomeTeamData] = useState<{ logo_url?: string; league?: string } | null>(null);
  const [awayTeamData, setAwayTeamData] = useState<{ logo_url?: string; league?: string } | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAuthPrompt, setShowAuthPrompt] = useState(false);

  const canPredict = useMemo(
    () => homeTeam && awayTeam && homeTeam !== awayTeam,
    [homeTeam, awayTeam]
  );

  const handlePredict = useCallback(async () => {
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
  }, [homeTeam, awayTeam, user]);

  const handleNewPrediction = useCallback(() => {
    setPrediction(null);
    setHomeTeam(null);
    setAwayTeam(null);
    setError(null);
    setShowAuthPrompt(false);
  }, []);

  // Auth Prompt Component
  const AuthPrompt = () => (
    <Card variant="outlined" padding="lg" style={styles.authCard}>
      <View
        style={[
          styles.authIconContainer,
          { backgroundColor: theme.colors.primary + "20" },
        ]}
      >
        <Icon icon={Lock} size={32} variant="primary" />
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
                <View style={styles.headerRow}>
                  <Icon icon={Sparkles} size={28} variant="primary" />
                  <ThemedText size="2xl" weight="bold">
                    {t("prediction.newPrediction")}
                  </ThemedText>
                </View>
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
                    label={t("prediction.selectHomeTeam")}
                    selectedTeam={homeTeam}
                    onSelectTeam={(team, data) => {
                      setHomeTeam(team);
                      setHomeTeamData(data || null);
                    }}
                    excludeTeam={awayTeam}
                    icon={Home}
                  />

                  {/* Home Team Stats */}
                  <TeamStatsCard teamName={homeTeam} icon={Home} />

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
                    label={t("prediction.selectAwayTeam")}
                    selectedTeam={awayTeam}
                    onSelectTeam={(team, data) => {
                      setAwayTeam(team);
                      setAwayTeamData(data || null);
                    }}
                    excludeTeam={homeTeam}
                    icon={Bus}
                  />

                  {/* Away Team Stats */}
                  <TeamStatsCard teamName={awayTeam} icon={Bus} />

                  {/* Error Message */}
                  {error && (
                    <View
                      style={[
                        styles.errorBox,
                        { backgroundColor: theme.colors.error + "20" },
                      ]}
                    >
                      <Icon icon={AlertCircle} size={18} variant="error" />
                      <ThemedText variant="error" size="sm" style={styles.errorText}>
                        {error}
                      </ThemedText>
                    </View>
                  )}

                  {/* Predict Button */}
                  <Button
                    title={
                      loading
                        ? t("prediction.generating")
                        : t("prediction.predict")
                    }
                    icon={loading ? undefined : Sparkles}
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
                  <Icon icon={Sparkles} size={64} variant="muted" />
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
  headerRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  errorBox: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  errorText: {
    flex: 1,
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

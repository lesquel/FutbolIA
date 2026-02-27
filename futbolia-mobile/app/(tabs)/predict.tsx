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
  useWindowDimensions,
  KeyboardAvoidingView,
  Platform,
  TouchableOpacity,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useTranslation } from "react-i18next";
import { Lock, Sparkles, Home, Bus, AlertCircle } from "lucide-react-native";

import { useTheme } from "@/src/theme";
import { useAuth } from "@/src/context";
import {
  ThemedView,
  ThemedText,
  Card,
  Button,
  Icon,
} from "@/src/components/ui";
import {
  TeamSelector,
  TeamStatsCard,
  PredictionCard,
  GoalMindChat,
} from "@/src/components/features";
import { predictionsApi, Prediction } from "@/src/services/api";

export default function PredictScreen() {
  const { theme } = useTheme();
  const { t } = useTranslation();
  const { user } = useAuth();
  const router = useRouter();
  const params = useLocalSearchParams();

  // Responsive breakpoints - usando useWindowDimensions para reactividad
  const { width: screenWidth, height: screenHeight } = useWindowDimensions();
  const isTablet = screenWidth >= 768;
  const isDesktop = screenWidth >= 1024;
  const isLargeScreen = isTablet || isDesktop;

  // Calcular padding dinámico basado en tamaño de pantalla
  const responsivePadding = useMemo(() => {
    if (isDesktop) return { horizontal: 40, top: 24, bottom: 48 };
    if (isTablet) return { horizontal: 28, top: 20, bottom: 44 };
    return { horizontal: 12, top: 10, bottom: 24 };
  }, [isTablet, isDesktop]);

  // State
  const [homeTeam, setHomeTeam] = useState<string | null>(
    (params.homeTeam as string) || null,
  );
  const [awayTeam, setAwayTeam] = useState<string | null>(
    (params.awayTeam as string) || null,
  );
  const [homeTeamData, setHomeTeamData] = useState<{
    logo_url?: string;
    league?: string;
  } | null>(null);
  const [awayTeamData, setAwayTeamData] = useState<{
    logo_url?: string;
    league?: string;
  } | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAuthPrompt, setShowAuthPrompt] = useState(false);

  const canPredict = useMemo(
    () => homeTeam && awayTeam && homeTeam !== awayTeam,
    [homeTeam, awayTeam],
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
    <Card
      variant="outlined"
      padding="lg"
      style={[styles.authCard, isLargeScreen && styles.authCardLarge]}
    >
      <View
        style={[
          styles.authIconContainer,
          isLargeScreen && styles.authIconContainerLarge,
          { backgroundColor: theme.colors.primary + "20" },
        ]}
      >
        <Icon icon={Lock} size={isLargeScreen ? 40 : 32} variant="primary" />
      </View>
      <ThemedText
        size={isLargeScreen ? "2xl" : "xl"}
        weight="bold"
        style={styles.authTitle}
      >
        {t("auth.loginRequired")}
      </ThemedText>
      <ThemedText
        variant="secondary"
        size={isLargeScreen ? "lg" : "base"}
        style={[
          styles.authDescription,
          isLargeScreen && styles.authDescriptionLarge,
        ]}
      >
        {t("auth.loginToPredict")}
      </ThemedText>
      <View
        style={[styles.authButtons, isLargeScreen && styles.authButtonsLarge]}
      >
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
        behavior={Platform.OS === "ios" ? "padding" : Platform.OS === "android" ? "height" : undefined}
        style={styles.container}
        enabled={Platform.OS !== 'web'}
      >
        <ScrollView
          contentContainerStyle={[
            styles.scrollContent,
            {
              paddingHorizontal: responsivePadding.horizontal,
              paddingTop: responsivePadding.top,
              paddingBottom: responsivePadding.bottom,
            },
          ]}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          {/* Responsive Layout */}
          <View
            style={[
              styles.content,
              isTablet && styles.contentTablet,
              isDesktop && styles.contentDesktop,
            ]}
          >
            {/* Left Column - Team Selection */}
            <View
              style={[
                styles.column,
                isTablet && styles.columnTablet,
                isDesktop && styles.columnDesktop,
              ]}
            >
              {/* Header */}
              <View
                style={[styles.header, isLargeScreen && styles.headerLarge]}
              >
                <View style={styles.headerRow}>
                  <Icon
                    icon={Sparkles}
                    size={isLargeScreen ? 36 : 28}
                    variant="primary"
                  />
                  <ThemedText
                    size={isLargeScreen ? "3xl" : "2xl"}
                    weight="bold"
                  >
                    {t("prediction.newPrediction")}
                  </ThemedText>
                </View>
                <ThemedText
                  variant="secondary"
                  size={isLargeScreen ? "lg" : "base"}
                >
                  {t("home.selectTeams")}
                </ThemedText>
              </View>

              {/* GoalMind Chat */}
              <GoalMindChat
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
                  {/* Home Team Selector */}
                  <View style={styles.teamSelectorWrapper}>
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
                  </View>

                  {/* Home Team Stats - con overflow hidden para no bloquear */}
                  <View style={styles.statsWrapper}>
                    <TeamStatsCard teamName={homeTeam} icon={Home} />
                  </View>

                  {/* VS Indicator - sin interacción */}
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

                  {/* Away Team Selector - con zIndex mayor */}
                  <View style={styles.teamSelectorWrapper}>
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
                  </View>

                  {/* Away Team Stats */}
                  <View style={styles.statsWrapper}>
                    <TeamStatsCard teamName={awayTeam} icon={Bus} />
                  </View>

                  {/* Error Message */}
                  {error && (
                    <View
                      style={[
                        styles.errorBox,
                        { backgroundColor: theme.colors.error + "20" },
                      ]}
                    >
                      <Icon icon={AlertCircle} size={18} variant="error" />
                      <ThemedText
                        variant="error"
                        size="sm"
                        style={styles.errorText}
                      >
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

            {/* Right Column - Prediction Result (only render when there's content or on tablet) */}
            {(isTablet || showAuthPrompt || loading || prediction) && (
              <View
                style={[
                  styles.column,
                  isTablet && styles.columnTablet,
                  isDesktop && styles.columnDesktop,
                ]}
              >
                {/* Auth Prompt */}
                {showAuthPrompt && <AuthPrompt />}

                {/* Loading State */}
                {loading && (
                  <Card
                    variant="outlined"
                    padding="lg"
                    style={[
                      styles.loadingCard,
                      isLargeScreen && styles.loadingCardLarge,
                    ]}
                  >
                    <ActivityIndicator
                      size="large"
                      color={theme.colors.primary}
                    />
                    <ThemedText
                      variant="secondary"
                      size={isLargeScreen ? "lg" : "base"}
                      style={styles.loadingText}
                    >
                      {t("prediction.generating")}
                    </ThemedText>
                    <ThemedText
                      variant="muted"
                      size={isLargeScreen ? "base" : "sm"}
                    >
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
                {isTablet && !prediction && !loading && !showAuthPrompt && (
                  <Card
                    variant="outlined"
                    padding="lg"
                    style={[
                      styles.emptyCard,
                      isDesktop && styles.emptyCardDesktop,
                    ]}
                  >
                    <Icon
                      icon={Sparkles}
                      size={isDesktop ? 80 : 64}
                      variant="muted"
                    />
                    <ThemedText
                      variant="muted"
                      size={isDesktop ? "lg" : "base"}
                      style={styles.emptyText}
                    >
                      Selecciona dos equipos para ver la predicción de GoalMind
                    </ThemedText>
                  </Card>
                )}
              </View>
            )}
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
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 40,
  },
  content: {
    // No flex: 1 on mobile - let content determine height
  },
  contentTablet: {
    flexDirection: "row",
    gap: 24,
    flex: 1,
  },
  column: {
    // No flex on mobile - natural height
  },
  columnTablet: {
    flex: 0.5,
  },
  header: {
    marginBottom: 10,
  },
  headerRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 2,
  },
  errorBox: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    padding: 12,
    borderRadius: 10,
    marginBottom: 12,
  },
  errorText: {
    flex: 1,
    lineHeight: 20,
  },
  selectionCard: {
    marginTop: 4,
  },
  teamSelectorWrapper: {
    position: "relative",
    zIndex: 10,
  },
  statsWrapper: {
    position: "relative",
    zIndex: 1,
    overflow: "hidden",
  },
  vsIndicator: {
    flexDirection: "row",
    alignItems: "center",
    marginVertical: 12,
    paddingHorizontal: 6,
    zIndex: 1,
  },
  vsLine: {
    flex: 1,
    height: 1,
  },
  vsText: {
    marginHorizontal: 16,
  },
  predictButton: {
    marginTop: 8,
  },
  loadingCard: {
    alignItems: "center",
    justifyContent: "center",
    minHeight: 160,
    paddingVertical: 24,
  },
  loadingText: {
    marginTop: 12,
    marginBottom: 6,
  },
  emptyCard: {
    alignItems: "center",
    justifyContent: "center",
    minHeight: 200,
    paddingVertical: 28,
  },
  emptyIcon: {
    marginBottom: 16,
  },
  emptyText: {
    textAlign: "center",
    paddingHorizontal: 16,
  },
  authCard: {
    alignItems: "center",
    justifyContent: "center",
    marginTop: 16,
    paddingVertical: 24,
  },
  authIconContainer: {
    width: 72,
    height: 72,
    borderRadius: 36,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 20,
  },
  authTitle: {
    textAlign: "center",
    marginBottom: 10,
  },
  authDescription: {
    textAlign: "center",
    marginBottom: 24,
    paddingHorizontal: 16,
    lineHeight: 22,
  },
  authButtons: {
    width: "100%",
    gap: 12,
    paddingHorizontal: 8,
  },
  authButton: {
    marginBottom: 0,
  },
  dismissButton: {
    marginTop: 20,
    padding: 12,
  },
  // ==========================================
  // RESPONSIVE STYLES FOR TABLETS AND DESKTOP
  // ==========================================
  contentDesktop: {
    flexDirection: "row",
    gap: 40,
    maxWidth: 1400,
    alignSelf: "center",
    width: "100%",
  },
  columnDesktop: {
    flex: 0.5,
  },
  headerLarge: {
    marginBottom: 24,
  },
  loadingCardLarge: {
    minHeight: 280,
    paddingVertical: 48,
  },
  emptyCardDesktop: {
    minHeight: 400,
    paddingVertical: 60,
  },
  authCardLarge: {
    paddingVertical: 36,
    paddingHorizontal: 32,
    maxWidth: 480,
    alignSelf: "center",
  },
  authIconContainerLarge: {
    width: 88,
    height: 88,
    borderRadius: 44,
    marginBottom: 28,
  },
  authDescriptionLarge: {
    lineHeight: 26,
    paddingHorizontal: 24,
    marginBottom: 32,
  },
  authButtonsLarge: {
    gap: 16,
    paddingHorizontal: 16,
  },
});

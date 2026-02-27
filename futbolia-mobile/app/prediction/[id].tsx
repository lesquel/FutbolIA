/**
 * FutbolIA - Prediction Detail Screen
 * Shows full analysis for a specific prediction from history
 */
import { useState, useEffect } from "react";
import {
  ScrollView,
  View,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
} from "react-native";
import { useLocalSearchParams, useRouter, Stack } from "expo-router";
import { useTranslation } from "react-i18next";
import { Ionicons } from "@expo/vector-icons";

import { useTheme } from "@/src/theme";
import { ThemedView, ThemedText, Card, Button } from "@/src/components/ui";
import { PredictionCard } from "@/src/components/features";
import { predictionsApi, Prediction } from "@/src/services/api";

export default function PredictionDetailScreen() {
  const { theme } = useTheme();
  const { t } = useTranslation();
  const router = useRouter();
  const { id } = useLocalSearchParams();

  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadPredictionDetail();
    }
  }, [id]);

  const loadPredictionDetail = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await predictionsApi.getPredictionDetail(id as string);
      if (response.success && response.data) {
        setPrediction(response.data);
      } else {
        setError(
          response.error || "No se pudo cargar el detalle de la predicción"
        );
      }
    } catch (err) {
      setError("Error de conexión al cargar el detalle");
      console.log("Error loading prediction detail:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ThemedView variant="background" style={styles.container}>
      <Stack.Screen
        options={{
          title: t("prediction.detailTitle") || "Detalle de Predicción",
          headerLeft: () => (
            <TouchableOpacity
              onPress={() => router.back()}
              style={styles.backButton}
            >
              <Ionicons name="arrow-back" size={24} color={theme.colors.text} />
            </TouchableOpacity>
          ),
        }}
      />

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {loading ? (
          <View style={styles.centerContainer}>
            <ActivityIndicator size="large" color={theme.colors.primary} />
            <ThemedText variant="secondary" style={styles.loadingText}>
              Cargando análisis detallado...
            </ThemedText>
          </View>
        ) : error ? (
          <View style={styles.centerContainer}>
            <ThemedText size="3xl">⚠️</ThemedText>
            <ThemedText variant="error" style={styles.errorText}>
              {error}
            </ThemedText>
            <Button
              title="Reintentar"
              onPress={loadPredictionDetail}
              variant="outline"
              style={styles.retryButton}
            />
          </View>
        ) : prediction ? (
          <PredictionCard
            prediction={prediction}
            onNewPrediction={() => router.push("/predict")}
          />
        ) : null}
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
    paddingBottom: 48,
  },
  centerContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingTop: 80,
    paddingHorizontal: 24,
  },
  loadingText: {
    marginTop: 20,
    textAlign: "center",
  },
  errorText: {
    marginTop: 20,
    textAlign: "center",
    marginBottom: 28,
    lineHeight: 22,
  },
  retryButton: {
    minWidth: 160,
  },
  backButton: {
    marginLeft: 10,
    padding: 6,
  },
});

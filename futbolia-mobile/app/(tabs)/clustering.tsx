/**
 * Clustering Screen - Análisis de Minería de Datos
 * Visualización de clustering jerárquico de equipos con dendrogramas
 */
import { useState, useEffect } from "react";
import {
  View,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  TouchableOpacity,
  Platform,
} from "react-native";
import { useTranslation } from "react-i18next";
import { Database, TrendingUp, RefreshCw } from "lucide-react-native";

import { useTheme } from "@/src/theme";
import {
  ThemedView,
  ThemedText,
  Card,
  Button,
  Icon,
} from "@/src/components/ui";
import { DendrogramChart } from "@/src/components/features";
import { leaguesApi } from "@/src/services/api";

export default function ClusteringScreen() {
  const { theme } = useTheme();
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [clusteringData, setClusteringData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [nClusters, setNClusters] = useState(4);
  const [method, setMethod] = useState("ward");

  useEffect(() => {
    loadClustering();
  }, [nClusters, method]);

  const loadClustering = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await leaguesApi.getPremierLeagueClustering(
        nClusters,
        method
      );
      if (response.success && response.data) {
        setClusteringData(response.data);
      } else {
        setError(response.error || "Error al obtener datos de clustering");
      }
    } catch (err: any) {
      console.error("Error loading clustering:", err);
      setError(err.message || "Error al cargar clustering");
    } finally {
      setLoading(false);
    }
  };

  const renderControls = () => (
    <Card padding="md" style={styles.controlsCard}>
      <ThemedText size="sm" weight="semibold" style={styles.controlsTitle}>
        Parámetros de Clustering
      </ThemedText>

      {/* Selector de número de clusters */}
      <View style={styles.controlGroup}>
        <ThemedText size="xs" variant="muted" style={styles.controlLabel}>
          Número de Clusters: {nClusters}
        </ThemedText>
        <View style={styles.buttonRow}>
          {[2, 3, 4, 5, 6].map((num) => (
            <TouchableOpacity
              key={num}
              style={[
                styles.controlButton,
                {
                  backgroundColor:
                    nClusters === num
                      ? theme.colors.primary
                      : theme.colors.surfaceSecondary,
                  borderColor: theme.colors.border,
                },
              ]}
              onPress={() => setNClusters(num)}
            >
              <ThemedText
                size="xs"
                weight={nClusters === num ? "bold" : "normal"}
                style={{
                  color:
                    nClusters === num ? "#fff" : theme.colors.text,
                }}
              >
                {num}
              </ThemedText>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Selector de método */}
      <View style={styles.controlGroup}>
        <ThemedText size="xs" variant="muted" style={styles.controlLabel}>
          Método de Linkage:
        </ThemedText>
        <View style={styles.buttonRow}>
          {[
            { value: "ward", label: "Ward" },
            { value: "complete", label: "Complete" },
            { value: "average", label: "Average" },
            { value: "single", label: "Single" },
          ].map((m) => (
            <TouchableOpacity
              key={m.value}
              style={[
                styles.controlButton,
                {
                  backgroundColor:
                    method === m.value
                      ? theme.colors.primary
                      : theme.colors.surfaceSecondary,
                  borderColor: theme.colors.border,
                },
              ]}
              onPress={() => setMethod(m.value)}
            >
              <ThemedText
                size="xs"
                weight={method === m.value ? "bold" : "normal"}
                style={{
                  color: method === m.value ? "#fff" : theme.colors.text,
                }}
              >
                {m.label}
              </ThemedText>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <Button
        title="Recalcular"
        variant="outline"
        size="sm"
        onPress={loadClustering}
        icon={RefreshCw}
        style={styles.recalculateButton}
      />
    </Card>
  );

  const renderInfoCard = () => (
    <Card padding="md" style={styles.infoCard}>
      <View style={styles.infoHeader}>
        <Icon icon={Database} size={24} variant="primary" />
        <ThemedText size="lg" weight="bold" style={styles.infoTitle}>
          Minería de Datos: Clustering Jerárquico
        </ThemedText>
      </View>
      <ThemedText size="sm" variant="secondary" style={styles.infoText}>
        Este análisis utiliza técnicas de clustering jerárquico para agrupar
        equipos según sus características de rendimiento en la tabla de
        posiciones.
      </ThemedText>
      <View style={styles.infoSection}>
        <ThemedText size="xs" weight="semibold" style={styles.infoSubtitle}>
          Características Analizadas:
        </ThemedText>
        <ThemedText size="xs" variant="muted" style={styles.infoList}>
          • Puntos por partido jugado{'\n'}
          • Diferencia de goles por partido{'\n'}
          • Goles a favor/contra por partido{'\n'}
          • Tasas de victoria, empate y derrota
        </ThemedText>
      </View>
      <View style={styles.infoSection}>
        <ThemedText size="xs" weight="semibold" style={styles.infoSubtitle}>
          Métodos de Linkage:
        </ThemedText>
        <ThemedText size="xs" variant="muted" style={styles.infoList}>
          • <ThemedText size="xs" weight="semibold">Ward:</ThemedText> Minimiza varianza (recomendado){'\n'}
          • <ThemedText size="xs" weight="semibold">Complete:</ThemedText> Distancia máxima{'\n'}
          • <ThemedText size="xs" weight="semibold">Average:</ThemedText> Distancia promedio{'\n'}
          • <ThemedText size="xs" weight="semibold">Single:</ThemedText> Distancia mínima
        </ThemedText>
      </View>
    </Card>
  );

  if (loading && !clusteringData) {
    return (
      <ThemedView variant="background" style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
          <ThemedText variant="muted" style={styles.loadingText}>
            Analizando equipos...
          </ThemedText>
        </View>
      </ThemedView>
    );
  }

  return (
    <ThemedView variant="background" style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <Icon icon={TrendingUp} size={32} variant="primary" />
          <View style={styles.headerText}>
            <ThemedText size="xl" weight="bold">
              Análisis de Clustering
            </ThemedText>
            <ThemedText size="sm" variant="muted">
              Minería de Datos - Premier League
            </ThemedText>
          </View>
        </View>

        {/* Información educativa */}
        {renderInfoCard()}

        {/* Controles */}
        {renderControls()}

        {/* Resultados */}
        {error ? (
          <Card padding="md" style={styles.errorCard}>
            <ThemedText size="sm" style={{ color: theme.colors.error }}>
              {error}
            </ThemedText>
            <Button
              title="Reintentar"
              variant="outline"
              size="sm"
              onPress={loadClustering}
              style={styles.retryButton}
            />
          </Card>
        ) : clusteringData ? (
          <>
            {/* Estadísticas generales */}
            <Card padding="md" style={styles.statsCard}>
              <ThemedText size="sm" weight="semibold" style={styles.statsTitle}>
                Resumen del Análisis
              </ThemedText>
              <View style={styles.statsGrid}>
                <View style={styles.statItem}>
                  <ThemedText size="xs" variant="muted">
                    Equipos Analizados
                  </ThemedText>
                  <ThemedText size="lg" weight="bold" style={{ color: theme.colors.primary }}>
                    {clusteringData.n_teams}
                  </ThemedText>
                </View>
                <View style={styles.statItem}>
                  <ThemedText size="xs" variant="muted">
                    Clusters Generados
                  </ThemedText>
                  <ThemedText size="lg" weight="bold" style={{ color: theme.colors.primary }}>
                    {clusteringData.n_clusters}
                  </ThemedText>
                </View>
                <View style={styles.statItem}>
                  <ThemedText size="xs" variant="muted">
                    Método
                  </ThemedText>
                  <ThemedText size="lg" weight="bold" style={{ color: theme.colors.primary }}>
                    {clusteringData.method.toUpperCase()}
                  </ThemedText>
                </View>
              </View>
            </Card>

            {/* Dendrograma */}
            {clusteringData.dendrogram && (
              <View style={styles.chartSection}>
                <ThemedText size="lg" weight="bold" style={styles.sectionTitle}>
                  Dendrograma Jerárquico
                </ThemedText>
                <ThemedText size="xs" variant="muted" style={styles.sectionSubtitle}>
                  Visualización de la estructura jerárquica de clusters
                </ThemedText>
                <DendrogramChart
                  data={clusteringData.dendrogram}
                />
              </View>
            )}

            {/* Tabla de equipos por cluster */}
            {clusteringData.teams && (
              <Card padding="md" style={styles.teamsCard}>
                <ThemedText size="lg" weight="bold" style={styles.sectionTitle}>
                  Distribución por Clusters
                </ThemedText>
                {clusteringData.cluster_info?.map((cluster: any) => (
                  <View
                    key={cluster.cluster_id}
                    style={[
                      styles.clusterGroup,
                      { borderColor: theme.colors.border },
                    ]}
                  >
                    <View
                      style={[
                        styles.clusterHeader,
                        { backgroundColor: theme.colors.primary + "20" },
                      ]}
                    >
                      <ThemedText
                        size="sm"
                        weight="bold"
                        style={{ color: theme.colors.primary }}
                      >
                        Cluster {cluster.cluster_id} - {cluster.n_teams}{" "}
                        equipos
                      </ThemedText>
                    </View>
                    <ThemedText size="sm" weight="semibold" style={styles.clusterDescription}>
                      {cluster.description}
                    </ThemedText>
                    <ThemedText size="xs" variant="secondary" style={styles.clusterTeams}>
                      Equipos: {cluster.teams.join(", ")}
                    </ThemedText>
                    <View style={styles.clusterStats}>
                      <ThemedText size="xs" weight="medium">
                        Puntos promedio: {cluster.avg_points.toFixed(1)}
                      </ThemedText>
                      <ThemedText size="xs" weight="medium">
                        DG promedio: {cluster.avg_goal_difference.toFixed(1)}
                      </ThemedText>
                    </View>
                  </View>
                ))}
              </Card>
            )}
          </>
        ) : null}
      </ScrollView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 32,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  loadingText: {
    marginTop: 12,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    marginBottom: 16,
  },
  headerText: {
    flex: 1,
  },
  infoCard: {
    marginBottom: 16,
  },
  infoHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    marginBottom: 12,
  },
  infoTitle: {
    flex: 1,
  },
  infoText: {
    marginBottom: 12,
    lineHeight: 20,
  },
  infoSection: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: "rgba(0,0,0,0.1)",
  },
  infoSubtitle: {
    marginBottom: 6,
  },
  infoList: {
    lineHeight: 18,
  },
  controlsCard: {
    marginBottom: 16,
  },
  controlsTitle: {
    marginBottom: 16,
  },
  controlGroup: {
    marginBottom: 16,
  },
  controlLabel: {
    marginBottom: 8,
  },
  buttonRow: {
    flexDirection: "row",
    gap: 8,
    flexWrap: "wrap",
  },
  controlButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
    minWidth: 60,
    alignItems: "center",
  },
  recalculateButton: {
    marginTop: 8,
  },
  errorCard: {
    marginBottom: 16,
    alignItems: "center",
  },
  retryButton: {
    marginTop: 12,
  },
  statsCard: {
    marginBottom: 16,
  },
  statsTitle: {
    marginBottom: 12,
  },
  statsGrid: {
    flexDirection: "row",
    justifyContent: "space-around",
  },
  statItem: {
    alignItems: "center",
  },
  chartSection: {
    marginBottom: 16,
  },
  sectionTitle: {
    marginBottom: 8,
  },
  sectionSubtitle: {
    marginBottom: 12,
  },
  teamsCard: {
    marginBottom: 16,
  },
  clusterGroup: {
    borderRadius: 8,
    borderWidth: 1,
    marginBottom: 12,
    overflow: "hidden",
  },
  clusterHeader: {
    padding: 10,
  },
  clusterDescription: {
    padding: 10,
    paddingTop: 8,
    paddingBottom: 4,
  },
  clusterTeams: {
    paddingHorizontal: 10,
    paddingBottom: 8,
  },
  clusterStats: {
    flexDirection: "row",
    justifyContent: "space-between",
    padding: 10,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: "rgba(0,0,0,0.1)",
  },
});

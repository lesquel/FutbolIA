/**
 * DendrogramChart - Componente para visualizar dendrograma de clustering jerárquico
 * Muestra la estructura jerárquica de clusters de equipos
 */
import React, { useMemo } from "react";
import {
  View,
  StyleSheet,
  ScrollView,
  useWindowDimensions,
} from "react-native";
import Svg, { Line, Text as SvgText, Circle, Rect } from "react-native-svg";
import { useTheme } from "@/src/theme";
import { ThemedText } from "@/src/components/ui";

interface DendrogramData {
  icoord: number[][];
  dcoord: number[][];
  ivl: string[];
  leaves: number[];
  leaf_x_positions?: { [key: number]: number }; // Mapeo de índice de hoja -> posición X
}

interface DendrogramChartProps {
  data: DendrogramData;
  clusterInfo?: Array<{
    cluster_id: number;
    n_teams: number;
    description: string;
    teams: string[];
  }>;
}

export function DendrogramChart({ data, clusterInfo }: DendrogramChartProps) {
  const { theme } = useTheme();
  const { width: screenWidth } = useWindowDimensions();

  // Responsive breakpoints
  const isTablet = screenWidth >= 768;
  const isDesktop = screenWidth >= 1024;
  const isLargeScreen = isTablet || isDesktop;

  // Responsive chart dimensions
  const chartDimensions = useMemo(() => {
    const padding = isDesktop ? 64 : isTablet ? 48 : 32;
    const chartWidth = Math.min(
      screenWidth - padding,
      isDesktop ? 900 : isTablet ? 700 : screenWidth - padding,
    );
    const chartHeight = isDesktop ? 650 : isTablet ? 600 : 550;
    const marginLeft = isLargeScreen ? 15 : 10;
    const marginTop = isLargeScreen ? 25 : 20;
    const marginBottom = isDesktop ? 140 : isTablet ? 130 : 120;
    const marginRight = isLargeScreen ? 15 : 10;

    return {
      chartWidth,
      chartHeight,
      marginLeft,
      marginTop,
      marginBottom,
      marginRight,
    };
  }, [screenWidth, isTablet, isDesktop, isLargeScreen]);

  const {
    chartWidth: CHART_WIDTH,
    chartHeight: CHART_HEIGHT,
    marginLeft: MARGIN_LEFT,
    marginTop: MARGIN_TOP,
    marginBottom: MARGIN_BOTTOM,
    marginRight: MARGIN_RIGHT,
  } = chartDimensions;

  // Normalizar coordenadas del dendrograma para el viewport
  const normalizedCoords = useMemo(() => {
    if (!data.icoord || !data.dcoord || data.icoord.length === 0) {
      return { lines: [], labels: [] };
    }

    // Encontrar los valores máximos y mínimos
    let maxX = 0;
    let minY = Infinity;
    let maxY = 0;

    data.icoord.forEach((coord) => {
      coord.forEach((x) => {
        maxX = Math.max(maxX, x);
      });
    });

    data.dcoord.forEach((coord) => {
      coord.forEach((y) => {
        minY = Math.min(minY, y);
        maxY = Math.max(maxY, y);
      });
    });

    // Calcular escalas con mejor distribución
    const availableWidth = CHART_WIDTH - MARGIN_LEFT - MARGIN_RIGHT;
    const availableHeight = CHART_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM;
    const nLeaves = data.leaves?.length || 1;

    // Mejorar el espaciado: distribuir uniformemente las hojas
    const spacing = availableWidth / (nLeaves - 1 || 1); // Espaciado uniforme entre hojas

    // Función para mapear posiciones X originales a nuevas posiciones distribuidas
    const mapXToLeafIndex = (x: number): number => {
      const normalizedX = (x / maxX) * (nLeaves - 1);
      return Math.max(0, Math.min(Math.round(normalizedX), nLeaves - 1));
    };

    const scaleY = availableHeight / (maxY - minY || 1);
    const offsetY = minY;

    // Normalizar líneas (GIRO 180 GRADOS: invertir Y)
    const lines: Array<{
      x1: number;
      y1: number;
      x2: number;
      y2: number;
    }> = [];

    data.icoord.forEach((icoord, idx) => {
      const dcoord = data.dcoord[idx];
      if (icoord.length === 4 && dcoord.length === 4) {
        // Invertir Y para girar 180 grados: las hojas arriba, raíz abajo
        const y0 =
          CHART_HEIGHT - MARGIN_BOTTOM - (dcoord[0] - offsetY) * scaleY;
        const y1 =
          CHART_HEIGHT - MARGIN_BOTTOM - (dcoord[1] - offsetY) * scaleY;
        const y2 =
          CHART_HEIGHT - MARGIN_BOTTOM - (dcoord[2] - offsetY) * scaleY;
        const y3 =
          CHART_HEIGHT - MARGIN_BOTTOM - (dcoord[3] - offsetY) * scaleY;

        // Mapear las posiciones X originales a las nuevas posiciones distribuidas uniformemente
        const leafIdx0 = mapXToLeafIndex(icoord[0]);
        const leafIdx2 = mapXToLeafIndex(icoord[2]);

        const x0 = MARGIN_LEFT + leafIdx0 * spacing;
        const x2 = MARGIN_LEFT + leafIdx2 * spacing;

        // Cada merge tiene 3 líneas (└ ─ ┘)
        // Línea vertical izquierda
        lines.push({
          x1: x0,
          y1: y0,
          x2: x0,
          y2: y1,
        });
        // Línea horizontal
        lines.push({
          x1: x0,
          y1: y1,
          x2: x2,
          y2: y2,
        });
        // Línea vertical derecha
        lines.push({
          x1: x2,
          y1: y2,
          x2: x2,
          y2: y3,
        });
      }
    });

    // Preparar etiquetas - Mapear hojas a posiciones X
    const labels: Array<{
      x: number;
      y: number;
      text: string;
      index: number;
      leafPosition: number;
    }> = [];

    if (data.ivl && data.leaves && data.leaves.length > 0) {
      // Usar el mapeo del backend si está disponible, sino calcularlo
      let leafXMap: { [key: number]: number } = {};

      if (data.leaf_x_positions) {
        // Usar las posiciones proporcionadas por el backend
        leafXMap = data.leaf_x_positions;
      } else {
        // Fallback: calcular posiciones basándose en el orden de las hojas
        const allXValues: number[] = [];
        data.icoord.forEach((icoord) => {
          icoord.forEach((x) => {
            allXValues.push(x);
          });
        });
        const uniqueX = Array.from(new Set(allXValues)).sort((a, b) => a - b);

        data.leaves.forEach((leafIdx, posIdx) => {
          leafXMap[leafIdx] =
            uniqueX[posIdx] !== undefined
              ? uniqueX[posIdx]
              : posIdx * (maxX / data.leaves.length);
        });
      }

      // Crear etiquetas para cada hoja (en la parte inferior)
      // Distribuir uniformemente para mejor espaciado
      const nLeaves = data.leaves.length;
      const totalWidth = availableWidth;
      const spacing = totalWidth / (nLeaves - 1 || 1); // Espaciado uniforme

      data.leaves.forEach((leafIdx, posIdx) => {
        // Usar distribución uniforme en lugar de las posiciones originales para mejor espaciado
        const xPosition = posIdx * spacing;
        const x = MARGIN_LEFT + xPosition;

        labels.push({
          x,
          y: CHART_HEIGHT - MARGIN_BOTTOM + 50, // Posición abajo para las etiquetas
          text: data.ivl[posIdx] || `Team ${leafIdx}`,
          index: leafIdx,
          leafPosition: xPosition,
        });
      });
    }

    return { lines, labels };
  }, [
    data,
    CHART_WIDTH,
    CHART_HEIGHT,
    MARGIN_LEFT,
    MARGIN_TOP,
    MARGIN_BOTTOM,
    MARGIN_RIGHT,
  ]);

  return (
    <View style={[styles.container, isLargeScreen && styles.containerLarge]}>
      <View
        style={[
          styles.chartContainer,
          isLargeScreen && styles.chartContainerLarge,
          {
            backgroundColor: theme.colors.surface,
            borderColor: theme.colors.border,
          },
        ]}
      >
        <Svg width={CHART_WIDTH} height={CHART_HEIGHT}>
          {/* Renderizar líneas del dendrograma */}
          {normalizedCoords.lines.map((line, idx) => (
            <Line
              key={`line-${idx}`}
              x1={line.x1}
              y1={line.y1}
              x2={line.x2}
              y2={line.y2}
              stroke={theme.colors.primary}
              strokeWidth={isLargeScreen ? 3 : 2.5}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          ))}

          {/* Renderizar puntos de conexión en las hojas (parte superior después del giro) */}
          {normalizedCoords.labels.map((label, idx) => {
            // La hoja está en la parte superior después del giro 180°
            // Usar la misma posición Y que las líneas del dendrograma terminan
            const leafY = CHART_HEIGHT - MARGIN_BOTTOM;
            return (
              <Circle
                key={`point-${idx}`}
                cx={label.x}
                cy={leafY}
                r={isLargeScreen ? 6 : 5}
                fill={theme.colors.primary}
                stroke={theme.colors.background}
                strokeWidth={isLargeScreen ? 3 : 2.5}
              />
            );
          })}

          {/* Renderizar etiquetas de equipos en la parte inferior con texto inclinado */}
          {normalizedCoords.labels.map((label, idx) => {
            const maxLength = isDesktop ? 25 : isTablet ? 22 : 20;
            const shortName =
              label.text.length > maxLength
                ? label.text.substring(0, maxLength) + "..."
                : label.text;

            // Calcular posición Y de la hoja (parte inferior del dendrograma)
            const leafY = CHART_HEIGHT - MARGIN_BOTTOM;

            return (
              <React.Fragment key={`label-group-${idx}`}>
                {/* Línea conectora desde la hoja hasta la etiqueta */}
                <Line
                  x1={label.x}
                  y1={leafY}
                  x2={label.x}
                  y2={label.y - (isLargeScreen ? 30 : 25)}
                  stroke={theme.colors.primary}
                  strokeWidth={isLargeScreen ? 2 : 1.5}
                  strokeDasharray={isLargeScreen ? "5,5" : "4,4"}
                  opacity={0.4}
                />
                {/* Fondo transparente */}
                <Rect
                  x={label.x - (isLargeScreen ? 70 : 55)}
                  y={label.y - (isLargeScreen ? 22 : 18)}
                  width={isLargeScreen ? 140 : 110}
                  height={isLargeScreen ? 44 : 36}
                  rx={isLargeScreen ? 8 : 6}
                  fill="transparent"
                />
                {/* Texto del equipo inclinado (-45 grados) */}
                <SvgText
                  x={label.x}
                  y={label.y + (isLargeScreen ? 10 : 8)}
                  fontSize={isDesktop ? 14 : isTablet ? 13 : 12}
                  fontWeight="600"
                  fill={theme.colors.text}
                  textAnchor="middle"
                  rotation={-45}
                  origin={`${label.x}, ${label.y + (isLargeScreen ? 10 : 8)}`}
                >
                  {shortName}
                </SvgText>
              </React.Fragment>
            );
          })}
        </Svg>

        {/* Información del dendrograma */}
        <View
          style={[styles.chartInfo, isLargeScreen && styles.chartInfoLarge]}
        >
          <ThemedText
            size={isLargeScreen ? "sm" : "xs"}
            variant="muted"
            style={[styles.infoText, isLargeScreen && styles.infoTextLarge]}
          >
            El dendrograma muestra la similitud entre equipos. Equipos más
            cercanos tienen características más similares.
          </ThemedText>
        </View>
      </View>

      {/* Información de clusters */}
      {clusterInfo && clusterInfo.length > 0 && (
        <View
          style={[styles.clusterInfo, isLargeScreen && styles.clusterInfoLarge]}
        >
          <ThemedText
            size={isLargeScreen ? "xl" : "lg"}
            weight="bold"
            style={[
              styles.sectionTitle,
              isLargeScreen && styles.sectionTitleLarge,
            ]}
          >
            Análisis de Clusters
          </ThemedText>
          <ScrollView
            horizontal={!isDesktop}
            showsHorizontalScrollIndicator={false}
            style={styles.clusterScroll}
            contentContainerStyle={isDesktop && styles.clusterScrollDesktop}
          >
            {clusterInfo.map((cluster) => (
              <View
                key={cluster.cluster_id}
                style={[
                  styles.clusterCard,
                  isLargeScreen && styles.clusterCardLarge,
                  {
                    backgroundColor: theme.colors.surface,
                    borderColor: theme.colors.border,
                  },
                ]}
              >
                <View
                  style={[
                    styles.clusterBadge,
                    isLargeScreen && styles.clusterBadgeLarge,
                    { backgroundColor: theme.colors.primary + "20" },
                  ]}
                >
                  <ThemedText
                    size={isLargeScreen ? "base" : "sm"}
                    weight="bold"
                    style={{ color: theme.colors.primary }}
                  >
                    Cluster {cluster.cluster_id}
                  </ThemedText>
                </View>
                <ThemedText
                  size={isLargeScreen ? "sm" : "xs"}
                  variant="muted"
                  style={[
                    styles.clusterDesc,
                    isLargeScreen && styles.clusterDescLarge,
                  ]}
                >
                  {cluster.description}
                </ThemedText>
                <ThemedText
                  size={isLargeScreen ? "sm" : "xs"}
                  style={[
                    styles.clusterTeams,
                    isLargeScreen && styles.clusterTeamsLarge,
                  ]}
                >
                  {cluster.n_teams} equipos:{" "}
                  {cluster.teams.slice(0, isDesktop ? 5 : 3).join(", ")}
                  {cluster.teams.length > (isDesktop ? 5 : 3) && "..."}
                </ThemedText>
              </View>
            ))}
          </ScrollView>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: "100%",
  },
  chartContainer: {
    borderRadius: 14,
    borderWidth: 1,
    padding: 18,
    marginBottom: 18,
    overflow: "visible", // Cambiado a visible para que las etiquetas no se corten
  },
  chartInfo: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: "rgba(0,0,0,0.1)",
  },
  infoText: {
    textAlign: "center",
    lineHeight: 20,
    paddingHorizontal: 8,
  },
  clusterInfo: {
    marginTop: 12,
  },
  sectionTitle: {
    marginBottom: 14,
  },
  clusterScroll: {
    flexDirection: "row",
    paddingVertical: 4,
  },
  clusterCard: {
    minWidth: 220,
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    marginRight: 14,
  },
  clusterBadge: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 6,
    marginBottom: 10,
    alignSelf: "flex-start",
  },
  clusterDesc: {
    marginBottom: 10,
    lineHeight: 20,
  },
  clusterTeams: {
    fontSize: 12,
    opacity: 0.8,
    lineHeight: 18,
  },
  // ==========================================
  // RESPONSIVE STYLES FOR TABLETS AND DESKTOP
  // ==========================================
  containerLarge: {
    alignItems: "center",
  },
  chartContainerLarge: {
    borderRadius: 18,
    padding: 24,
    marginBottom: 24,
  },
  chartInfoLarge: {
    marginTop: 18,
    paddingTop: 18,
  },
  infoTextLarge: {
    lineHeight: 24,
    paddingHorizontal: 16,
  },
  clusterInfoLarge: {
    marginTop: 20,
    width: "100%",
  },
  sectionTitleLarge: {
    marginBottom: 20,
  },
  clusterScrollDesktop: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 16,
  },
  clusterCardLarge: {
    minWidth: 280,
    padding: 20,
    borderRadius: 16,
    marginRight: 18,
  },
  clusterBadgeLarge: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 8,
    marginBottom: 14,
  },
  clusterDescLarge: {
    marginBottom: 14,
    lineHeight: 24,
  },
  clusterTeamsLarge: {
    fontSize: 14,
    lineHeight: 22,
  },
});

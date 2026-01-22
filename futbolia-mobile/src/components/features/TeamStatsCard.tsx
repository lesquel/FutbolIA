/**
 * TeamStatsCard - Shows team players and stats after selection
 */
import {
  View,
  StyleSheet,
  ActivityIndicator,
  useWindowDimensions,
} from "react-native";
import { useState, useEffect, memo } from "react";
import { LucideIcon, Users } from "lucide-react-native";
import { useTheme } from "@/src/theme";
import { ThemedText, Card, Icon } from "@/src/components/ui";
import { teamsApi, Player } from "@/src/services/api";

interface TeamStats {
  overall: number;
  pace: number;
  shooting: number;
  passing: number;
  defending: number;
  physical: number;
}

interface TeamStatsCardProps {
  readonly teamName: string | null;
  readonly icon?: LucideIcon;
}

// Helper to get position color
const getPositionColor = (position: string) => {
  if (position === "GK") return "#FFA500"; // Orange
  if (["CB", "LB", "RB", "LWB", "RWB"].includes(position)) return "#3498db"; // Blue
  if (["CDM", "CM", "CAM"].includes(position)) return "#27ae60"; // Green
  return "#e74c3c"; // Red for attackers
};

// Stat bar component
const StatBar = ({
  label,
  value,
  color,
  isLargeScreen = false,
}: {
  label: string;
  value: number;
  color: string;
  isLargeScreen?: boolean;
}) => (
  <View style={[styles.statRow, isLargeScreen && styles.statRowLarge]}>
    <ThemedText
      size={isLargeScreen ? "sm" : "xs"}
      style={[styles.statLabel, isLargeScreen && styles.statLabelLarge]}
    >
      {label}
    </ThemedText>
    <View
      style={[
        styles.statBarContainer,
        isLargeScreen && styles.statBarContainerLarge,
      ]}
    >
      <View
        style={[
          styles.statBarFill,
          { width: `${value}%`, backgroundColor: color },
        ]}
      />
    </View>
    <ThemedText
      size={isLargeScreen ? "sm" : "xs"}
      weight="bold"
      style={[styles.statValue, isLargeScreen && styles.statValueLarge]}
    >
      {value}
    </ThemedText>
  </View>
);

export const TeamStatsCard = memo(function TeamStatsCard({
  teamName,
  icon: IconComponent = Users,
}: TeamStatsCardProps) {
  const { theme } = useTheme();
  const { width: screenWidth } = useWindowDimensions();
  const isTablet = screenWidth >= 768;
  const isDesktop = screenWidth >= 1024;
  const isLargeScreen = isTablet || isDesktop;
  const [loading, setLoading] = useState(false);
  const [players, setPlayers] = useState<Player[]>([]);
  const [stats, setStats] = useState<TeamStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!teamName) {
      setPlayers([]);
      setStats(null);
      return;
    }

    const loadTeamData = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await teamsApi.getTeamPlayers(teamName);

        if (response.success && response.data) {
          setPlayers(response.data.players || []);
          setStats(response.data.stats || null);
        } else {
          setError("No se pudieron cargar los datos");
        }
      } catch (err) {
        setError("Error de conexión");
        console.log("Error loading team data:", err);
      } finally {
        setLoading(false);
      }
    };

    loadTeamData();
  }, [teamName]);

  if (!teamName) return null;

  if (loading) {
    return (
      <Card
        variant="outlined"
        padding={isLargeScreen ? "lg" : "md"}
        style={[styles.card, isLargeScreen && styles.cardLarge]}
      >
        <View
          style={[
            styles.loadingContainer,
            isLargeScreen && styles.loadingContainerLarge,
          ]}
        >
          <ActivityIndicator
            size={isLargeScreen ? "large" : "small"}
            color={theme.colors.primary}
          />
          <ThemedText
            variant="muted"
            size={isLargeScreen ? "base" : "sm"}
            style={styles.loadingText}
          >
            Cargando datos de {teamName}...
          </ThemedText>
        </View>
      </Card>
    );
  }

  if (error || (!players.length && !stats)) {
    return (
      <Card
        variant="outlined"
        padding={isLargeScreen ? "lg" : "md"}
        style={[styles.card, isLargeScreen && styles.cardLarge]}
      >
        <ThemedText variant="muted" size={isLargeScreen ? "base" : "sm"}>
          {error || `Sin datos disponibles para ${teamName}`}
        </ThemedText>
      </Card>
    );
  }

  return (
    <Card
      variant="outlined"
      padding={isLargeScreen ? "lg" : "md"}
      style={[styles.card, isLargeScreen && styles.cardLarge]}
    >
      {/* Header */}
      <View style={[styles.header, isLargeScreen && styles.headerLarge]}>
        <View style={styles.headerRow}>
          <Icon
            icon={IconComponent}
            size={isLargeScreen ? 26 : 20}
            variant="primary"
          />
          <ThemedText size={isLargeScreen ? "lg" : "base"} weight="bold">
            {teamName}
          </ThemedText>
        </View>
        {stats && (
          <View
            style={[
              styles.ovrBadge,
              isLargeScreen && styles.ovrBadgeLarge,
              { backgroundColor: theme.colors.primary + "20" },
            ]}
          >
            <ThemedText
              size={isLargeScreen ? "base" : "sm"}
              weight="bold"
              style={{ color: theme.colors.primary }}
            >
              OVR {stats.overall}
            </ThemedText>
          </View>
        )}
      </View>

      {/* Team Stats */}
      {stats && (
        <View
          style={[
            styles.statsSection,
            isLargeScreen && styles.statsSectionLarge,
          ]}
        >
          <StatBar
            label="PAC"
            value={stats.pace}
            color={stats.pace > 75 ? "#27ae60" : "#f39c12"}
            isLargeScreen={isLargeScreen}
          />
          <StatBar
            label="SHO"
            value={stats.shooting}
            color={stats.shooting > 75 ? "#27ae60" : "#f39c12"}
            isLargeScreen={isLargeScreen}
          />
          <StatBar
            label="PAS"
            value={stats.passing}
            color={stats.passing > 75 ? "#27ae60" : "#f39c12"}
            isLargeScreen={isLargeScreen}
          />
          <StatBar
            label="DEF"
            value={stats.defending}
            color={stats.defending > 75 ? "#27ae60" : "#f39c12"}
            isLargeScreen={isLargeScreen}
          />
          <StatBar
            label="PHY"
            value={stats.physical}
            color={stats.physical > 75 ? "#27ae60" : "#f39c12"}
            isLargeScreen={isLargeScreen}
          />
        </View>
      )}

      {/* Players List */}
      {players.length > 0 && (
        <View
          style={[
            styles.playersSection,
            isLargeScreen && styles.playersSectionLarge,
          ]}
        >
          <View style={styles.playersTitleRow}>
            <Icon icon={Users} size={isLargeScreen ? 18 : 14} variant="muted" />
            <ThemedText
              variant="muted"
              size={isLargeScreen ? "sm" : "xs"}
              style={styles.playersTitle}
            >
              Plantilla ({players.length} jugadores)
            </ThemedText>
          </View>
          <View
            style={[
              styles.playersGrid,
              isLargeScreen && styles.playersGridLarge,
            ]}
          >
            {players.slice(0, isDesktop ? 15 : 11).map((player) => (
              <View
                key={`${player.name}-${player.position}`}
                style={[
                  styles.playerChip,
                  isLargeScreen && styles.playerChipLarge,
                  { backgroundColor: theme.colors.surfaceSecondary },
                ]}
              >
                <View
                  style={[
                    styles.positionDot,
                    isLargeScreen && styles.positionDotLarge,
                    { backgroundColor: getPositionColor(player.position) },
                  ]}
                />
                <ThemedText
                  size={isLargeScreen ? "sm" : "xs"}
                  numberOfLines={1}
                  style={[
                    styles.playerName,
                    isLargeScreen && styles.playerNameLarge,
                  ]}
                >
                  {player.name.split(" ").pop()}
                </ThemedText>
                <ThemedText
                  size={isLargeScreen ? "sm" : "xs"}
                  weight="bold"
                  style={{ color: theme.colors.primary }}
                >
                  {player.overall_rating}
                </ThemedText>
              </View>
            ))}
          </View>
        </View>
      )}
    </Card>
  );
});

const styles = StyleSheet.create({
  card: {
    marginTop: 12,
  },
  loadingContainer: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 12,
  },
  loadingText: {
    marginLeft: 10,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 14,
    flexWrap: "wrap",
    gap: 8,
  },
  headerRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    flex: 1,
    minWidth: 0,
  },
  playersTitleRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 10,
  },
  ovrBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 10,
    flexShrink: 0,
  },
  statsSection: {
    marginBottom: 14,
  },
  statRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 6,
  },
  statLabel: {
    width: 34,
  },
  statBarContainer: {
    flex: 1,
    height: 8,
    backgroundColor: "rgba(0,0,0,0.1)",
    borderRadius: 4,
    marginHorizontal: 10,
  },
  statBarFill: {
    height: "100%",
    borderRadius: 4,
  },
  statValue: {
    width: 28,
    textAlign: "right",
  },
  playersSection: {
    borderTopWidth: 1,
    borderTopColor: "rgba(0,0,0,0.1)",
    paddingTop: 12,
  },
  playersTitle: {
    marginBottom: 10,
  },
  playersGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
  },
  playerChip: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 8,
    paddingVertical: 5,
    borderRadius: 14,
    gap: 5,
  },
  positionDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  playerName: {
    maxWidth: 70,
  },
  // ==========================================
  // RESPONSIVE STYLES FOR TABLETS AND DESKTOP
  // ==========================================
  cardLarge: {
    marginTop: 16,
    borderRadius: 16,
  },
  loadingContainerLarge: {
    paddingVertical: 20,
  },
  headerLarge: {
    marginBottom: 20,
  },
  ovrBadgeLarge: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 12,
  },
  statsSectionLarge: {
    marginBottom: 20,
  },
  statRowLarge: {
    marginBottom: 10,
  },
  statLabelLarge: {
    width: 45,
  },
  statBarContainerLarge: {
    height: 12,
    borderRadius: 6,
    marginHorizontal: 14,
  },
  statValueLarge: {
    width: 36,
  },
  playersSectionLarge: {
    paddingTop: 18,
  },
  playersGridLarge: {
    gap: 10,
  },
  playerChipLarge: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 18,
    gap: 8,
  },
  positionDotLarge: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  playerNameLarge: {
    maxWidth: 90,
  },
});

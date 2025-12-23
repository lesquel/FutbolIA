/**
 * TeamStatsCard - Shows team players and stats after selection
 */
import { View, StyleSheet, ActivityIndicator } from "react-native";
import { useState, useEffect } from "react";
import { useTheme } from "@/src/theme";
import { ThemedText, Card } from "@/src/components/ui";
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
  readonly emoji?: string;
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
}: {
  label: string;
  value: number;
  color: string;
}) => (
  <View style={styles.statRow}>
    <ThemedText size="xs" style={styles.statLabel}>
      {label}
    </ThemedText>
    <View style={styles.statBarContainer}>
      <View
        style={[
          styles.statBarFill,
          { width: `${value}%`, backgroundColor: color },
        ]}
      />
    </View>
    <ThemedText size="xs" weight="bold" style={styles.statValue}>
      {value}
    </ThemedText>
  </View>
);

export function TeamStatsCard({ teamName, emoji = "⚽" }: TeamStatsCardProps) {
  const { theme } = useTheme();
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
      <Card variant="outlined" padding="md" style={styles.card}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="small" color={theme.colors.primary} />
          <ThemedText variant="muted" size="sm" style={styles.loadingText}>
            Cargando datos de {teamName}...
          </ThemedText>
        </View>
      </Card>
    );
  }

  if (error || (!players.length && !stats)) {
    return (
      <Card variant="outlined" padding="md" style={styles.card}>
        <ThemedText variant="muted" size="sm">
          {error || `Sin datos disponibles para ${teamName}`}
        </ThemedText>
      </Card>
    );
  }

  return (
    <Card variant="outlined" padding="md" style={styles.card}>
      {/* Header */}
      <View style={styles.header}>
        <ThemedText size="base" weight="bold">
          {emoji} {teamName}
        </ThemedText>
        {stats && (
          <View
            style={[
              styles.ovrBadge,
              { backgroundColor: theme.colors.primary + "20" },
            ]}
          >
            <ThemedText
              size="sm"
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
        <View style={styles.statsSection}>
          <StatBar
            label="PAC"
            value={stats.pace}
            color={stats.pace > 75 ? "#27ae60" : "#f39c12"}
          />
          <StatBar
            label="SHO"
            value={stats.shooting}
            color={stats.shooting > 75 ? "#27ae60" : "#f39c12"}
          />
          <StatBar
            label="PAS"
            value={stats.passing}
            color={stats.passing > 75 ? "#27ae60" : "#f39c12"}
          />
          <StatBar
            label="DEF"
            value={stats.defending}
            color={stats.defending > 75 ? "#27ae60" : "#f39c12"}
          />
          <StatBar
            label="PHY"
            value={stats.physical}
            color={stats.physical > 75 ? "#27ae60" : "#f39c12"}
          />
        </View>
      )}

      {/* Players List */}
      {players.length > 0 && (
        <View style={styles.playersSection}>
          <ThemedText variant="muted" size="xs" style={styles.playersTitle}>
            👥 Plantilla ({players.length} jugadores)
          </ThemedText>
          <View style={styles.playersGrid}>
            {players.slice(0, 11).map((player) => (
              <View
                key={`${player.name}-${player.position}`}
                style={[
                  styles.playerChip,
                  { backgroundColor: theme.colors.surfaceSecondary },
                ]}
              >
                <View
                  style={[
                    styles.positionDot,
                    { backgroundColor: getPositionColor(player.position) },
                  ]}
                />
                <ThemedText size="xs" numberOfLines={1} style={styles.playerName}>
                  {player.name.split(" ").pop()}
                </ThemedText>
                <ThemedText
                  size="xs"
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
}

const styles = StyleSheet.create({
  card: {
    marginTop: 8,
  },
  loadingContainer: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
  },
  loadingText: {
    marginLeft: 8,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  ovrBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  statsSection: {
    marginBottom: 12,
  },
  statRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 4,
  },
  statLabel: {
    width: 30,
  },
  statBarContainer: {
    flex: 1,
    height: 6,
    backgroundColor: "rgba(0,0,0,0.1)",
    borderRadius: 3,
    marginHorizontal: 8,
  },
  statBarFill: {
    height: "100%",
    borderRadius: 3,
  },
  statValue: {
    width: 24,
    textAlign: "right",
  },
  playersSection: {
    borderTopWidth: 1,
    borderTopColor: "rgba(0,0,0,0.1)",
    paddingTop: 8,
  },
  playersTitle: {
    marginBottom: 8,
  },
  playersGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 4,
  },
  playerChip: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 6,
    paddingVertical: 3,
    borderRadius: 12,
    gap: 4,
  },
  positionDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
  },
  playerName: {
    maxWidth: 60,
  },
});

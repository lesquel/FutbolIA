/**
 * MatchCard - Card displaying match information
 */
import { View, TouchableOpacity, StyleSheet } from "react-native";
import { Sparkles } from "lucide-react-native";
import { useTheme } from "@/src/theme";
import { ThemedText, Card, TeamBadge, Icon } from "@/src/components/ui";
import { Match } from "@/src/services/api";

interface MatchCardProps {
  match: Match;
  onPress?: () => void;
  featured?: boolean;
}

export function MatchCard({
  match,
  onPress,
  featured = false,
}: MatchCardProps) {
  const { theme } = useTheme();

  /**
   * Formatea la fecha/hora del partido a zona horaria de Ecuador (UTC-5)
   * @param dateString - Fecha en formato ISO 8601 (ej: "2025-01-10T19:00:00Z")
   * @returns Fecha formateada en español con hora de Ecuador
   */
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      
      // Verificar si la fecha es válida
      if (isNaN(date.getTime())) {
        return dateString; // Devolver string original si no es parseable
      }
      
      // Formatear a zona horaria de Ecuador (America/Guayaquil = UTC-5)
      return date.toLocaleDateString("es-EC", {
        weekday: "short",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        timeZone: "America/Guayaquil", // Zona horaria de Ecuador
      });
    } catch {
      return dateString;
    }
  };

  return (
    <TouchableOpacity onPress={onPress} activeOpacity={0.7}>
      <Card
        variant={featured ? "elevated" : "default"}
        padding="md"
        style={featured ? styles.featuredCard : undefined}
      >
        {/* League Badge */}
        <View style={styles.header}>
          <ThemedText variant="muted" size="xs">
            {match.league}
          </ThemedText>
          <ThemedText variant="muted" size="xs">
            {formatDate(match.date)}
          </ThemedText>
        </View>

        {/* Teams */}
        <View style={styles.teamsContainer}>
          <TeamBadge
            name={match.home_team.name}
            logoUrl={match.home_team.logo_url}
            form={match.home_team.form}
            size={featured ? "lg" : "md"}
            showForm={featured}
          />

          <View style={styles.vsContainer}>
            <ThemedText
              variant="primary"
              size={featured ? "2xl" : "lg"}
              weight="bold"
            >
              VS
            </ThemedText>
            {match.venue && featured && (
              <ThemedText variant="muted" size="xs" style={styles.venue}>
                📍 {match.venue}
              </ThemedText>
            )}
          </View>

          <TeamBadge
            name={match.away_team.name}
            logoUrl={match.away_team.logo_url}
            form={match.away_team.form}
            size={featured ? "lg" : "md"}
            showForm={featured}
          />
        </View>

        {/* Predict Button Hint */}
        {featured && (
          <View
            style={[
              styles.predictHint,
              { backgroundColor: theme.colors.primary + "20" },
            ]}
          >
            <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
              <Icon icon={Sparkles} size={16} variant="primary" />
              <ThemedText variant="primary" size="sm" weight="semibold">
                Toca para predecir con GoalMind
              </ThemedText>
            </View>
          </View>
        )}
      </Card>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  featuredCard: {
    marginBottom: 8,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 16,
  },
  teamsContainer: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 8,
  },
  vsContainer: {
    alignItems: "center",
  },
  venue: {
    marginTop: 4,
    textAlign: "center",
  },
  predictHint: {
    marginTop: 16,
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: "center",
  },
});

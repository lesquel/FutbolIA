/**
 * MatchCard - Card displaying match information
 */
import {
  View,
  TouchableOpacity,
  StyleSheet,
  useWindowDimensions,
} from "react-native";
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
  const { width: screenWidth } = useWindowDimensions();
  const isTablet = screenWidth >= 768;
  const isDesktop = screenWidth >= 1024;
  const isLargeScreen = isTablet || isDesktop;

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
        padding={isLargeScreen ? "lg" : "md"}
        style={[
          featured && styles.featuredCard,
          isLargeScreen && styles.cardLarge,
        ]}
      >
        {/* League Badge */}
        <View style={[styles.header, isLargeScreen && styles.headerLarge]}>
          <ThemedText variant="muted" size={isLargeScreen ? "sm" : "xs"}>
            {match.league}
          </ThemedText>
          <ThemedText variant="muted" size={isLargeScreen ? "sm" : "xs"}>
            {formatDate(match.date)}
          </ThemedText>
        </View>

        {/* Teams */}
        <View
          style={[
            styles.teamsContainer,
            isLargeScreen && styles.teamsContainerLarge,
          ]}
        >
          <TeamBadge
            name={match.home_team.name}
            logoUrl={match.home_team.logo_url}
            form={match.home_team.form}
            size={
              featured
                ? isLargeScreen
                  ? "xl"
                  : "lg"
                : isLargeScreen
                  ? "lg"
                  : "md"
            }
            showForm={featured}
          />

          <View
            style={[
              styles.vsContainer,
              isLargeScreen && styles.vsContainerLarge,
            ]}
          >
            <ThemedText
              variant="primary"
              size={
                featured
                  ? isLargeScreen
                    ? "3xl"
                    : "2xl"
                  : isLargeScreen
                    ? "xl"
                    : "lg"
              }
              weight="bold"
            >
              VS
            </ThemedText>
            {match.venue && featured && (
              <ThemedText
                variant="muted"
                size={isLargeScreen ? "sm" : "xs"}
                style={[styles.venue, isLargeScreen && styles.venueLarge]}
              >
                📍 {match.venue}
              </ThemedText>
            )}
          </View>

          <TeamBadge
            name={match.away_team.name}
            logoUrl={match.away_team.logo_url}
            form={match.away_team.form}
            size={
              featured
                ? isLargeScreen
                  ? "xl"
                  : "lg"
                : isLargeScreen
                  ? "lg"
                  : "md"
            }
            showForm={featured}
          />
        </View>

        {/* Predict Button Hint */}
        {featured && (
          <View
            style={[
              styles.predictHint,
              isLargeScreen && styles.predictHintLarge,
              { backgroundColor: theme.colors.primary + "20" },
            ]}
          >
            <View
              style={{
                flexDirection: "row",
                alignItems: "center",
                gap: isLargeScreen ? 10 : 6,
              }}
            >
              <Icon
                icon={Sparkles}
                size={isLargeScreen ? 20 : 16}
                variant="primary"
              />
              <ThemedText
                variant="primary"
                size={isLargeScreen ? "base" : "sm"}
                weight="semibold"
              >
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
    marginBottom: 12,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 18,
    flexWrap: "wrap",
    gap: 6,
  },
  teamsContainer: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 12,
  },
  vsContainer: {
    alignItems: "center",
    paddingHorizontal: 8,
  },
  venue: {
    marginTop: 6,
    textAlign: "center",
    maxWidth: 120,
  },
  predictHint: {
    marginTop: 18,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 10,
    alignItems: "center",
  },
  // ==========================================
  // RESPONSIVE STYLES FOR TABLETS AND DESKTOP
  // ==========================================
  cardLarge: {
    borderRadius: 18,
  },
  headerLarge: {
    marginBottom: 24,
    gap: 10,
  },
  teamsContainerLarge: {
    paddingHorizontal: 24,
    paddingVertical: 12,
  },
  vsContainerLarge: {
    paddingHorizontal: 20,
  },
  venueLarge: {
    marginTop: 10,
    maxWidth: 180,
  },
  predictHintLarge: {
    marginTop: 24,
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 14,
  },
});

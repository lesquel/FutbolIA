/**
 * MatchCard - Card displaying match information
 */
import { View, TouchableOpacity, StyleSheet } from 'react-native';
import { useTheme } from '@/src/theme';
import { ThemedText, Card, TeamBadge } from '@/src/components/ui';
import { Match } from '@/src/services/api';

interface MatchCardProps {
  match: Match;
  onPress?: () => void;
  featured?: boolean;
}

export function MatchCard({ match, onPress, featured = false }: MatchCardProps) {
  const { theme } = useTheme();
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };
  
  return (
    <TouchableOpacity onPress={onPress} activeOpacity={0.7}>
      <Card 
        variant={featured ? 'elevated' : 'default'} 
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
            size={featured ? 'lg' : 'md'}
            showForm={featured}
          />
          
          <View style={styles.vsContainer}>
            <ThemedText 
              variant="primary" 
              size={featured ? '2xl' : 'lg'}
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
            size={featured ? 'lg' : 'md'}
            showForm={featured}
          />
        </View>
        
        {/* Predict Button Hint */}
        {featured && (
          <View style={[styles.predictHint, { backgroundColor: theme.colors.primary + '20' }]}>
            <ThemedText variant="primary" size="sm" weight="semibold">
              🔮 Toca para predecir con Dixie
            </ThemedText>
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  teamsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 8,
  },
  vsContainer: {
    alignItems: 'center',
  },
  venue: {
    marginTop: 4,
    textAlign: 'center',
  },
  predictHint: {
    marginTop: 16,
    paddingVertical: 10,
    borderRadius: 8,
    alignItems: 'center',
  },
});

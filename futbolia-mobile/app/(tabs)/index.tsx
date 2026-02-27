/**
 * GoalMind - Home Screen
 * Dashboard principal con scroll para móvil, layout de dos columnas para tablet
 */
import { useState, useEffect, useMemo } from 'react';
import {
  View,
  StyleSheet,
  useWindowDimensions,
  Image,
  ActivityIndicator,
  TouchableOpacity,
  ScrollView,
  Platform,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { Sparkles, Trophy, ChevronRight } from 'lucide-react-native';

import { useTheme } from '@/src/theme';
import { ThemedView, ThemedText, Card, Button, Icon, TeamBadge } from '@/src/components/ui';
import { GoalMindChat, LeagueTable } from '@/src/components/features';
import { predictionsApi, Match } from '@/src/services/api';

export default function HomeScreen() {
  const { theme } = useTheme();
  const { t } = useTranslation();
  const router = useRouter();

  // Responsive breakpoints - usando useWindowDimensions para reactividad
  const { width: screenWidth, height: screenHeight } = useWindowDimensions();
  const isTablet = screenWidth >= 768;
  const isDesktop = screenWidth >= 1024;
  const isLargeScreen = isTablet || isDesktop;

  // Calcular padding dinámico basado en tamaño de pantalla
  const responsiveStyles = useMemo(
    () => ({
      padding: {
        horizontal: isDesktop ? 40 : isTablet ? 24 : 16,
        top: isDesktop ? 24 : isTablet ? 16 : 12,
        bottom: isDesktop ? 32 : 24,
      },
      gap: isDesktop ? 32 : isTablet ? 20 : 16,
      logoSize: isDesktop ? 72 : isTablet ? 60 : 44,
    }),
    [isTablet, isDesktop],
  );

  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [showLeagueTable, setShowLeagueTable] = useState(false);

  useEffect(() => {
    loadMatches();
  }, []);

  const loadMatches = async () => {
    try {
      const response = await predictionsApi.getUpcomingMatches();
      if (response.success && response.data?.matches) {
        setMatches(response.data.matches);
      }
    } catch (error) {
      console.log('Error loading matches:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMatchPress = (match: Match) => {
    router.push({
      pathname: '/predict',
      params: {
        homeTeam: match.home_team.name,
        awayTeam: match.away_team.name,
      },
    });
  };

  const featuredMatch = matches[0];
  // Mostrar los siguientes 5 partidos
  const otherMatches = matches.slice(1, 6);

  /**
   * Formatea la fecha del partido a zona horaria de Ecuador (UTC-5) en formato compacto
   */
  const formatMatchDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return '';
      return date.toLocaleDateString('es-EC', {
        weekday: 'short',
        day: 'numeric',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'America/Guayaquil',
      });
    } catch {
      return '';
    }
  };

  if (loading) {
    return (
      <ThemedView variant="background" style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
        </View>
      </ThemedView>
    );
  }

  // En móvil usamos ScrollView, en tablet layout de dos columnas sin scroll
  const ContentWrapper = isLargeScreen ? View : ScrollView;
  const contentWrapperProps = isLargeScreen ? {} : { showsVerticalScrollIndicator: false };

  return (
    <ThemedView variant="background" style={styles.container}>
      <ContentWrapper
        style={[
          styles.content,
          isTablet && styles.contentTablet,
          isDesktop && styles.contentDesktop,
          {
            paddingHorizontal: responsiveStyles.padding.horizontal,
            paddingTop: responsiveStyles.padding.top,
            paddingBottom: responsiveStyles.padding.bottom,
            gap: responsiveStyles.gap,
          },
        ]}
        {...contentWrapperProps}
      >
        {/* Columna Principal */}
        <View
          style={[
            styles.mainColumn,
            isTablet && styles.mainColumnTablet,
            isDesktop && styles.mainColumnDesktop,
          ]}
        >
          {/* Header */}
          <View style={[styles.header, isLargeScreen && styles.headerLarge]}>
            <Image
              source={require('../../assets/images/GoalMind.png')}
              style={{
                width: responsiveStyles.logoSize,
                height: responsiveStyles.logoSize,
              }}
              resizeMode="contain"
            />
            <View style={styles.headerText}>
              <ThemedText size={isLargeScreen ? 'xl' : 'lg'} weight="bold">
                {t('home.welcome')}
              </ThemedText>
              <ThemedText variant="secondary" size={isLargeScreen ? 'sm' : 'xs'}>
                {t('home.subtitle')}
              </ThemedText>
            </View>
          </View>

          {/* GoalMind Compacto */}
          <GoalMindChat showGreeting={true} compact={true} />

          {/* Partido Destacado */}
          {featuredMatch && (
            <TouchableOpacity
              style={[
                styles.featuredMatch,
                isLargeScreen && styles.featuredMatchLarge,
                {
                  backgroundColor: theme.colors.surface,
                  borderColor: theme.colors.border,
                },
              ]}
              onPress={() => handleMatchPress(featuredMatch)}
              activeOpacity={0.7}
            >
              <View style={styles.matchHeader}>
                <ThemedText variant="muted" size={isLargeScreen ? 'sm' : 'xs'}>
                  {featuredMatch.league}
                </ThemedText>
                <ThemedText variant="muted" size={isLargeScreen ? 'sm' : 'xs'}>
                  {new Date(featuredMatch.date).toLocaleDateString('es-EC', {
                    weekday: 'short',
                    day: 'numeric',
                    month: 'short',
                    hour: '2-digit',
                    minute: '2-digit',
                    timeZone: 'America/Guayaquil',
                  })}
                </ThemedText>
              </View>
              <View style={[styles.matchTeams, isLargeScreen && styles.matchTeamsLarge]}>
                <TeamBadge
                  name={featuredMatch.home_team.name}
                  logoUrl={featuredMatch.home_team.logo_url}
                  size={isLargeScreen ? 'lg' : 'md'}
                />
                <ThemedText variant="primary" weight="bold" size={isLargeScreen ? 'xl' : 'lg'}>
                  VS
                </ThemedText>
                <TeamBadge
                  name={featuredMatch.away_team.name}
                  logoUrl={featuredMatch.away_team.logo_url}
                  size={isLargeScreen ? 'lg' : 'md'}
                />
              </View>
              <View
                style={[
                  styles.predictBadge,
                  isLargeScreen && styles.predictBadgeLarge,
                  { backgroundColor: theme.colors.primary + '20' },
                ]}
              >
                <Icon icon={Sparkles} size={isLargeScreen ? 18 : 14} variant="primary" />
                <ThemedText variant="primary" size={isLargeScreen ? 'sm' : 'xs'} weight="semibold">
                  Predecir
                </ThemedText>
              </View>
            </TouchableOpacity>
          )}

          {/* Botones de Acción */}
          <View style={[styles.actionButtons, isLargeScreen && styles.actionButtonsLarge]}>
            <Button
              title={t('home.quickPredict')}
              variant="primary"
              size={isLargeScreen ? 'lg' : 'sm'}
              fullWidth
              onPress={() => router.push('/predict')}
              icon={Sparkles}
            />
            <Button
              title="Tabla de Posiciones"
              variant="outline"
              size={isLargeScreen ? 'lg' : 'sm'}
              fullWidth
              onPress={() => setShowLeagueTable(true)}
              icon={Trophy}
            />
          </View>
        </View>

        {/* Sección Próximos Partidos */}
        <View
          style={[
            styles.sideColumn,
            isTablet && styles.sideColumnTablet,
            isDesktop && styles.sideColumnDesktop,
          ]}
        >
          <View style={[styles.sideHeader, isLargeScreen && styles.sideHeaderLarge]}>
            <ThemedText size={isLargeScreen ? 'lg' : 'sm'} weight="semibold">
              Próximos Partidos
            </ThemedText>
            <TouchableOpacity onPress={() => router.push('/predict')}>
              <ThemedText variant="primary" size={isLargeScreen ? 'sm' : 'xs'}>
                Ver más
              </ThemedText>
            </TouchableOpacity>
          </View>

          {otherMatches.map((match) => (
            <TouchableOpacity
              key={match.id}
              style={[
                styles.miniMatch,
                isLargeScreen && styles.miniMatchLarge,
                {
                  backgroundColor: theme.colors.surface,
                  borderColor: theme.colors.border,
                },
              ]}
              onPress={() => handleMatchPress(match)}
              activeOpacity={0.7}
            >
              <View style={styles.miniMatchInfo}>
                <View style={styles.miniMatchHeader}>
                  <ThemedText variant="muted" size={isLargeScreen ? 'sm' : 'xs'}>
                    {match.league}
                  </ThemedText>
                  <ThemedText variant="primary" size={isLargeScreen ? 'sm' : 'xs'}>
                    {formatMatchDate(match.date)}
                  </ThemedText>
                </View>
                <View style={styles.miniMatchTeams}>
                  <ThemedText
                    size={isLargeScreen ? 'base' : 'sm'}
                    weight="medium"
                    numberOfLines={1}
                    style={{ flex: 1 }}
                  >
                    {match.home_team.name.replace(' FC', '')}
                  </ThemedText>
                  <ThemedText variant="primary" size={isLargeScreen ? 'sm' : 'xs'} weight="bold">
                    vs
                  </ThemedText>
                  <ThemedText
                    size={isLargeScreen ? 'base' : 'sm'}
                    weight="medium"
                    numberOfLines={1}
                    style={{ flex: 1, textAlign: 'right' }}
                  >
                    {match.away_team.name.replace(' FC', '')}
                  </ThemedText>
                </View>
              </View>
              <Icon icon={ChevronRight} size={isLargeScreen ? 20 : 16} variant="muted" />
            </TouchableOpacity>
          ))}

          {otherMatches.length === 0 && (
            <Card padding="sm">
              <ThemedText variant="muted" size="xs" style={{ textAlign: 'center' }}>
                No hay más partidos
              </ThemedText>
            </Card>
          )}
        </View>
      </ContentWrapper>

      {/* League Table Modal */}
      <LeagueTable visible={showLeagueTable} onClose={() => setShowLeagueTable(false)} />
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    flex: 1,
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 24,
    flexDirection: 'column',
  },
  contentTablet: {
    flexDirection: 'row',
    gap: 16,
  },
  mainColumn: {
    flex: 1,
  },
  mainColumnTablet: {
    flex: 0.6,
  },
  sideColumn: {
    marginTop: 12,
  },
  sideColumnTablet: {
    flex: 0.4,
    marginTop: 0,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 12,
    paddingVertical: 4,
  },
  headerText: {
    flex: 1,
  },
  logoImage: {
    width: 44,
    height: 44,
  },
  featuredMatch: {
    borderRadius: 16,
    borderWidth: 1,
    padding: 16,
    marginBottom: 12,
  },
  matchHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    flexWrap: 'wrap',
    gap: 4,
  },
  matchTeams: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    marginBottom: 12,
    paddingHorizontal: 8,
  },
  predictBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 10,
  },
  actionButtons: {
    gap: 10,
    marginBottom: 12,
  },
  sideHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
    paddingHorizontal: 4,
  },
  miniMatch: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 12,
    borderWidth: 1,
    padding: 12,
    marginBottom: 8,
  },
  miniMatchInfo: {
    flex: 1,
    marginRight: 8,
  },
  miniMatchHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
    flexWrap: 'wrap',
    gap: 4,
  },
  miniMatchTeams: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    flexWrap: 'wrap',
  },
  // ==========================================
  // RESPONSIVE STYLES FOR TABLETS AND DESKTOP
  // ==========================================
  contentDesktop: {
    flexDirection: 'row',
    maxWidth: 1400,
    alignSelf: 'center',
    width: '100%',
  },
  mainColumnDesktop: {
    flex: 0.55,
  },
  sideColumnDesktop: {
    flex: 0.45,
  },
  headerLarge: {
    gap: 16,
    marginBottom: 20,
    paddingVertical: 8,
  },
  featuredMatchLarge: {
    borderRadius: 20,
    padding: 24,
    marginBottom: 20,
  },
  matchTeamsLarge: {
    marginBottom: 16,
    paddingHorizontal: 16,
  },
  predictBadgeLarge: {
    gap: 10,
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 14,
  },
  actionButtonsLarge: {
    gap: 14,
    marginBottom: 16,
  },
  sideHeaderLarge: {
    marginBottom: 16,
    paddingHorizontal: 6,
  },
  miniMatchLarge: {
    borderRadius: 16,
    padding: 18,
    marginBottom: 12,
  },
});

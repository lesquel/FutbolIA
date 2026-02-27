/**
 * FutbolIA - Teams Search Screen
 * Search and add favorite teams from multiple leagues
 * Now with API search for ANY league worldwide!
 */
import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  Image,
  FlatList,
  Alert,
  Modal,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';

import { useTheme } from '@/src/theme';
import { useAuth, FavoriteTeam } from '@/src/context';
import { ThemedView, ThemedText, Button, Icon } from '@/src/components/ui';
import { teamsApi, TeamSearchResult } from '@/src/services/api';
import { Check, Heart, Plus, Search, X, Globe, ArrowLeft, Shield } from 'lucide-react-native';

// Solo Premier League 2025-2026
const LEAGUES = [{ id: 'PL', name: 'Premier League', countryCode: 'ENG', countryName: 'England' }];

// Popular teams data (hardcoded for offline access + quick loading)
const POPULAR_TEAMS: FavoriteTeam[] = [
  // Premier League
  {
    id: 'MCI',
    name: 'Manchester City',
    shortName: 'MCI',
    league: 'Premier League',
    country: 'England',
    logoUrl: 'https://crests.football-data.org/65.png',
  },
  {
    id: 'ARS',
    name: 'Arsenal',
    shortName: 'ARS',
    league: 'Premier League',
    country: 'England',
    logoUrl: 'https://crests.football-data.org/57.png',
  },
  {
    id: 'LIV',
    name: 'Liverpool',
    shortName: 'LIV',
    league: 'Premier League',
    country: 'England',
    logoUrl: 'https://crests.football-data.org/64.png',
  },
  {
    id: 'MUN',
    name: 'Manchester United',
    shortName: 'MUN',
    league: 'Premier League',
    country: 'England',
    logoUrl: 'https://crests.football-data.org/66.png',
  },
  {
    id: 'CHE',
    name: 'Chelsea',
    shortName: 'CHE',
    league: 'Premier League',
    country: 'England',
    logoUrl: 'https://crests.football-data.org/61.png',
  },
  {
    id: 'TOT',
    name: 'Tottenham Hotspur',
    shortName: 'TOT',
    league: 'Premier League',
    country: 'England',
    logoUrl: 'https://crests.football-data.org/73.png',
  },
  {
    id: 'NEW',
    name: 'Newcastle United',
    shortName: 'NEW',
    league: 'Premier League',
    country: 'England',
    logoUrl: 'https://crests.football-data.org/67.png',
  },
  {
    id: 'AVL',
    name: 'Aston Villa',
    shortName: 'AVL',
    league: 'Premier League',
    country: 'England',
    logoUrl: 'https://crests.football-data.org/58.png',
  },
  // La Liga
  {
    id: 'RMA',
    name: 'Real Madrid',
    shortName: 'RMA',
    league: 'La Liga',
    country: 'Spain',
    logoUrl: 'https://crests.football-data.org/86.png',
  },
  {
    id: 'FCB',
    name: 'FC Barcelona',
    shortName: 'FCB',
    league: 'La Liga',
    country: 'Spain',
    logoUrl: 'https://crests.football-data.org/81.png',
  },
  {
    id: 'ATM',
    name: 'Atlético Madrid',
    shortName: 'ATM',
    league: 'La Liga',
    country: 'Spain',
    logoUrl: 'https://crests.football-data.org/78.png',
  },
  {
    id: 'SEV',
    name: 'Sevilla FC',
    shortName: 'SEV',
    league: 'La Liga',
    country: 'Spain',
    logoUrl: 'https://crests.football-data.org/559.png',
  },
  {
    id: 'VIL',
    name: 'Villarreal CF',
    shortName: 'VIL',
    league: 'La Liga',
    country: 'Spain',
    logoUrl: 'https://crests.football-data.org/94.png',
  },
  {
    id: 'RSO',
    name: 'Real Sociedad',
    shortName: 'RSO',
    league: 'La Liga',
    country: 'Spain',
    logoUrl: 'https://crests.football-data.org/92.png',
  },
  // Serie A
  {
    id: 'INT',
    name: 'Inter Milan',
    shortName: 'INT',
    league: 'Serie A',
    country: 'Italy',
    logoUrl: 'https://crests.football-data.org/108.png',
  },
  {
    id: 'ACM',
    name: 'AC Milan',
    shortName: 'ACM',
    league: 'Serie A',
    country: 'Italy',
    logoUrl: 'https://crests.football-data.org/98.png',
  },
  {
    id: 'JUV',
    name: 'Juventus',
    shortName: 'JUV',
    league: 'Serie A',
    country: 'Italy',
    logoUrl: 'https://crests.football-data.org/109.png',
  },
  {
    id: 'NAP',
    name: 'Napoli',
    shortName: 'NAP',
    league: 'Serie A',
    country: 'Italy',
    logoUrl: 'https://crests.football-data.org/113.png',
  },
  {
    id: 'ROM',
    name: 'AS Roma',
    shortName: 'ROM',
    league: 'Serie A',
    country: 'Italy',
    logoUrl: 'https://crests.football-data.org/100.png',
  },
  {
    id: 'LAZ',
    name: 'Lazio',
    shortName: 'LAZ',
    league: 'Serie A',
    country: 'Italy',
    logoUrl: 'https://crests.football-data.org/110.png',
  },
  // Bundesliga
  {
    id: 'FCB_GER',
    name: 'Bayern Munich',
    shortName: 'FCB',
    league: 'Bundesliga',
    country: 'Germany',
    logoUrl: 'https://crests.football-data.org/5.png',
  },
  {
    id: 'BVB',
    name: 'Borussia Dortmund',
    shortName: 'BVB',
    league: 'Bundesliga',
    country: 'Germany',
    logoUrl: 'https://crests.football-data.org/4.png',
  },
  {
    id: 'RBL',
    name: 'RB Leipzig',
    shortName: 'RBL',
    league: 'Bundesliga',
    country: 'Germany',
    logoUrl: 'https://crests.football-data.org/721.png',
  },
  {
    id: 'LEV',
    name: 'Bayer Leverkusen',
    shortName: 'LEV',
    league: 'Bundesliga',
    country: 'Germany',
    logoUrl: 'https://crests.football-data.org/3.png',
  },
  // Ligue 1
  {
    id: 'PSG',
    name: 'Paris Saint-Germain',
    shortName: 'PSG',
    league: 'Ligue 1',
    country: 'France',
    logoUrl: 'https://crests.football-data.org/524.png',
  },
  {
    id: 'OL',
    name: 'Olympique Lyon',
    shortName: 'OL',
    league: 'Ligue 1',
    country: 'France',
    logoUrl: 'https://crests.football-data.org/523.png',
  },
  {
    id: 'OM',
    name: 'Olympique Marseille',
    shortName: 'OM',
    league: 'Ligue 1',
    country: 'France',
    logoUrl: 'https://crests.football-data.org/516.png',
  },
  {
    id: 'ASM',
    name: 'AS Monaco',
    shortName: 'ASM',
    league: 'Ligue 1',
    country: 'France',
    logoUrl: 'https://crests.football-data.org/548.png',
  },
];

export default function TeamsScreen() {
  const { theme } = useTheme();
  const { t } = useTranslation();
  const { favoriteTeams, addFavoriteTeam, removeFavoriteTeam } = useAuth();
  const router = useRouter();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLeague, setSelectedLeague] = useState<string | null>(null);
  const [filteredTeams, setFilteredTeams] = useState<FavoriteTeam[]>(POPULAR_TEAMS);
  const [isSearching, setIsSearching] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [teamToAdd, setTeamToAdd] = useState<FavoriteTeam | null>(null);
  const [isAddingTeam, setIsAddingTeam] = useState(false);
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Convert API team to FavoriteTeam format
  const apiTeamToFavorite = (apiTeam: TeamSearchResult): FavoriteTeam => ({
    id: apiTeam.id || apiTeam.name.replaceAll(/\s+/g, '_').toUpperCase(),
    name: apiTeam.name,
    shortName: apiTeam.short_name || apiTeam.name.substring(0, 3).toUpperCase(),
    league: apiTeam.league || 'Unknown League',
    country: apiTeam.country || 'Unknown',
    logoUrl: apiTeam.logo_url,
  });

  // Search with debounce - now searches API too!
  const performSearch = useCallback(async (query: string, league: string | null) => {
    if (!query.trim()) {
      setFilteredTeams(
        league
          ? POPULAR_TEAMS.filter((t) => t.league === LEAGUES.find((l) => l.id === league)?.name)
          : POPULAR_TEAMS,
      );
      return;
    }

    // First filter local teams
    const lowerQuery = query.toLowerCase();
    let localResults = POPULAR_TEAMS.filter(
      (team) =>
        team.name.toLowerCase().includes(lowerQuery) ||
        team.shortName?.toLowerCase().includes(lowerQuery) ||
        team.country?.toLowerCase().includes(lowerQuery) ||
        team.league?.toLowerCase().includes(lowerQuery),
    );

    if (league) {
      const leagueName = LEAGUES.find((l) => l.id === league)?.name;
      localResults = localResults.filter((t) => t.league === leagueName);
    }

    setFilteredTeams(localResults);

    // Then search API if query is long enough
    if (query.length >= 2) {
      setIsSearching(true);
      try {
        const response = await teamsApi.search(query, true, 30);

        if (response.success && response.data?.teams) {
          const apiResults = response.data.teams;

          // Merge API results with local results (avoid duplicates)
          const localNames = new Set(localResults.map((t) => t.name.toLowerCase()));
          const newApiTeams = apiResults
            .filter((t: TeamSearchResult) => !localNames.has(t.name.toLowerCase()))
            .map(apiTeamToFavorite);

          setFilteredTeams([...localResults, ...newApiTeams]);
        }
      } catch (error) {
        console.log('API search failed, using local only:', error);
        // Keep local results on API error
      } finally {
        setIsSearching(false);
      }
    }
  }, []);

  // Handle adding a new team to the database
  const handleAddNewTeam = async (team: FavoriteTeam) => {
    setTeamToAdd(team);
    setShowAddModal(true);
  };

  const confirmAddTeam = async () => {
    if (!teamToAdd) return;

    setIsAddingTeam(true);
    try {
      await teamsApi.addTeam({
        name: teamToAdd.name,
        short_name: teamToAdd.shortName,
        league: teamToAdd.league,
        country: teamToAdd.country,
        logo_url: teamToAdd.logoUrl,
      });

      // Add to favorites
      addFavoriteTeam(teamToAdd);

      Alert.alert(
        'Equipo Agregado',
        `${teamToAdd.name} ha sido agregado a la base de datos y a tus favoritos.`,
        [{ text: 'OK' }],
      );
    } catch (error: any) {
      // If team already exists, just add to favorites
      if (error.message?.includes('already exists')) {
        addFavoriteTeam(teamToAdd);
        Alert.alert(
          'Equipo Encontrado',
          `${teamToAdd.name} ya existía, se agregó a tus favoritos.`,
        );
      } else {
        Alert.alert('Error', 'No se pudo agregar el equipo. Intenta de nuevo.');
      }
    } finally {
      setIsAddingTeam(false);
      setShowAddModal(false);
      setTeamToAdd(null);
    }
  };

  useEffect(() => {
    // Clear previous timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    // Set new timeout for debounced search
    searchTimeoutRef.current = setTimeout(() => {
      performSearch(searchQuery, selectedLeague);
    }, 300);

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchQuery, selectedLeague, performSearch]);

  useEffect(() => {
    if (selectedLeague) {
      const leagueName = LEAGUES.find((l) => l.id === selectedLeague)?.name;
      setFilteredTeams(POPULAR_TEAMS.filter((t) => t.league === leagueName));
    } else {
      setFilteredTeams(POPULAR_TEAMS);
    }
    setSearchQuery('');
  }, [selectedLeague]);

  const isTeamFavorite = (teamId: string) => {
    return favoriteTeams.some((t) => t.id === teamId);
  };

  // Check if team is from API (not in POPULAR_TEAMS)
  const isFromApi = (team: FavoriteTeam) => {
    return !POPULAR_TEAMS.some((t) => t.id === team.id);
  };

  const toggleFavorite = (team: FavoriteTeam) => {
    if (isTeamFavorite(team.id)) {
      removeFavoriteTeam(team.id);
    } else if (isFromApi(team)) {
      // If team is from API and not in favorites, offer to add to database
      handleAddNewTeam(team);
    } else {
      addFavoriteTeam(team);
    }
  };

  // Helper to get border color for team card
  const getTeamCardBorderColor = (isFavorite: boolean, fromApi: boolean): string => {
    if (isFavorite) return theme.colors.primary;
    if (fromApi) return theme.colors.accent + '50';
    return theme.colors.border;
  };

  // Helper to get favorite icon component
  const renderFavoriteIcon = (isFavorite: boolean, fromApi: boolean) => {
    if (isFavorite) {
      return <Icon icon={Heart} size={16} color="#fff" />;
    }
    if (fromApi) {
      return <Icon icon={Plus} size={16} variant="muted" />;
    }
    return <Icon icon={Heart} size={16} variant="muted" />;
  };

  const renderTeamCard = ({ item: team }: { item: FavoriteTeam }) => {
    const isFavorite = isTeamFavorite(team.id);
    const fromApi = isFromApi(team);

    return (
      <TouchableOpacity
        style={[
          styles.teamCard,
          {
            backgroundColor: isFavorite ? theme.colors.primary + '15' : theme.colors.surface,
            borderColor: getTeamCardBorderColor(isFavorite, fromApi),
          },
        ]}
        onPress={() => toggleFavorite(team)}
        activeOpacity={0.7}
      >
        {/* API Badge */}
        {fromApi && (
          <View style={[styles.apiBadge, { backgroundColor: theme.colors.accent }]}>
            <View style={styles.apiBadgeContent}>
              <Icon icon={Globe} size={10} color="#fff" />
              <ThemedText size="xs" style={{ color: '#fff', marginLeft: 2 }}>
                API
              </ThemedText>
            </View>
          </View>
        )}

        <View style={[styles.teamLogo, { backgroundColor: theme.colors.surfaceSecondary }]}>
          {team.logoUrl ? (
            <Image
              source={{ uri: team.logoUrl }}
              style={styles.teamLogoImage}
              resizeMode="contain"
            />
          ) : (
            <Icon icon={Shield} size={28} variant="muted" />
          )}
        </View>
        <View style={styles.teamInfo}>
          <ThemedText weight="semibold" numberOfLines={1} style={styles.teamName}>
            {team.name}
          </ThemedText>
          <ThemedText variant="muted" size="xs" numberOfLines={1}>
            {team.league || team.country}
          </ThemedText>
        </View>
        <View
          style={[
            styles.favoriteIcon,
            {
              backgroundColor: isFavorite ? theme.colors.primary : theme.colors.surfaceSecondary,
            },
          ]}
        >
          {renderFavoriteIcon(isFavorite, fromApi)}
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <ThemedView variant="background" style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Icon icon={ArrowLeft} size={24} variant="secondary" />
        </TouchableOpacity>
        <ThemedText size="xl" weight="bold">
          {t('teams.title')}
        </ThemedText>
        <View style={styles.backButton} />
      </View>

      {/* Search Bar */}
      <View style={styles.searchContainer}>
        <View
          style={[
            styles.searchBox,
            {
              backgroundColor: theme.colors.surfaceSecondary,
              borderColor: theme.colors.border,
            },
          ]}
        >
          <Icon icon={Search} size={18} variant="muted" />
          <TextInput
            style={[styles.searchInput, { color: theme.colors.text }]}
            placeholder={t('teams.searchPlaceholder')}
            placeholderTextColor={theme.colors.textMuted}
            value={searchQuery}
            onChangeText={setSearchQuery}
            autoCapitalize="none"
          />
          {searchQuery.length > 0 && (
            <TouchableOpacity onPress={() => setSearchQuery('')}>
              <Icon icon={X} size={18} variant="muted" />
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* League Filters */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.leaguesScroll}
        contentContainerStyle={styles.leaguesContainer}
      >
        <TouchableOpacity
          style={[
            styles.leagueChip,
            {
              backgroundColor:
                selectedLeague === null ? theme.colors.primary : theme.colors.surfaceSecondary,
              borderColor: selectedLeague === null ? theme.colors.primary : theme.colors.border,
            },
          ]}
          onPress={() => setSelectedLeague(null)}
        >
          <View style={styles.leagueChipContent}>
            <Icon
              icon={Globe}
              size={14}
              color={selectedLeague === null ? '#fff' : theme.colors.text}
            />
            <ThemedText
              size="sm"
              weight={selectedLeague === null ? 'semibold' : 'normal'}
              style={{
                color: selectedLeague === null ? '#fff' : theme.colors.text,
              }}
            >
              {t('teams.allLeagues')}
            </ThemedText>
          </View>
        </TouchableOpacity>

        {LEAGUES.map((league) => (
          <TouchableOpacity
            key={league.id}
            style={[
              styles.leagueChip,
              {
                backgroundColor:
                  selectedLeague === league.id
                    ? theme.colors.primary
                    : theme.colors.surfaceSecondary,
                borderColor:
                  selectedLeague === league.id ? theme.colors.primary : theme.colors.border,
              },
            ]}
            onPress={() => setSelectedLeague(league.id)}
          >
            <ThemedText
              size="sm"
              weight={selectedLeague === league.id ? 'semibold' : 'normal'}
              style={{
                color: selectedLeague === league.id ? '#fff' : theme.colors.text,
              }}
            >
              {league.countryCode} · {league.name}
            </ThemedText>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Favorites Count */}
      {favoriteTeams.length > 0 && (
        <View style={[styles.favoritesBar, { backgroundColor: theme.colors.primary + '15' }]}>
          <View style={styles.favoritesBarContent}>
            <Icon icon={Heart} size={14} variant="primary" />
            <ThemedText size="sm" variant="primary">
              {favoriteTeams.length} {t('teams.favoriteCount')}
            </ThemedText>
          </View>
        </View>
      )}

      {/* Teams List */}
      <FlatList
        data={filteredTeams}
        renderItem={renderTeamCard}
        keyExtractor={(item) => item.id}
        numColumns={2}
        columnWrapperStyle={styles.teamsRow}
        contentContainerStyle={styles.teamsList}
        showsVerticalScrollIndicator={false}
        ListHeaderComponent={
          isSearching ? (
            <View style={styles.searchingIndicator}>
              <ActivityIndicator size="small" color={theme.colors.primary} />
              <ThemedText variant="muted" size="sm" style={{ marginLeft: 8 }}>
                Buscando en la API...
              </ThemedText>
            </View>
          ) : null
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Icon icon={Search} size={48} variant="muted" />
            <ThemedText variant="secondary" style={styles.emptyText}>
              {searchQuery.length > 0
                ? 'No se encontraron equipos. ¡Prueba con otro nombre!'
                : t('teams.noResults')}
            </ThemedText>
            {searchQuery.length > 0 && (
              <ThemedText variant="muted" size="sm" style={{ marginTop: 8, textAlign: 'center' }}>
                Tip: Escribe al menos 2 letras para buscar en todas las ligas del mundo
              </ThemedText>
            )}
          </View>
        }
      />

      {/* Done Button */}
      {favoriteTeams.length > 0 && (
        <View style={[styles.doneButtonContainer, { backgroundColor: theme.colors.background }]}>
          <Button
            title={`${t('teams.done')} (${favoriteTeams.length})`}
            variant="primary"
            size="lg"
            fullWidth
            onPress={() => router.back()}
            icon={Check}
            iconPosition="left"
          />
        </View>
      )}

      {/* Add Team Confirmation Modal */}
      <Modal
        visible={showAddModal}
        transparent
        animationType="fade"
        onRequestClose={() => setShowAddModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { backgroundColor: theme.colors.surface }]}>
            <View style={styles.modalHeader}>
              <Icon icon={Plus} size={24} variant="primary" />
              <ThemedText size="xl" weight="bold" style={{ marginLeft: 8 }}>
                Agregar Equipo
              </ThemedText>
            </View>

            {teamToAdd && (
              <>
                <View
                  style={[
                    styles.modalTeamPreview,
                    { backgroundColor: theme.colors.surfaceSecondary },
                  ]}
                >
                  {teamToAdd.logoUrl ? (
                    <Image
                      source={{ uri: teamToAdd.logoUrl }}
                      style={{ width: 60, height: 60 }}
                      resizeMode="contain"
                    />
                  ) : (
                    <Icon icon={Shield} size={40} variant="muted" />
                  )}
                  <View style={{ marginLeft: 16, flex: 1 }}>
                    <ThemedText weight="bold" size="lg">
                      {teamToAdd.name}
                    </ThemedText>
                    <ThemedText variant="muted">{teamToAdd.league}</ThemedText>
                    <ThemedText variant="muted" size="sm">
                      {teamToAdd.country}
                    </ThemedText>
                  </View>
                </View>

                <ThemedText
                  variant="secondary"
                  size="sm"
                  style={{ marginTop: 16, textAlign: 'center' }}
                >
                  Este equipo se agregará a la base de datos de GoalMind para futuras predicciones.
                </ThemedText>
              </>
            )}

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, { backgroundColor: theme.colors.surfaceSecondary }]}
                onPress={() => {
                  setShowAddModal(false);
                  setTeamToAdd(null);
                }}
                disabled={isAddingTeam}
              >
                <ThemedText>Cancelar</ThemedText>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.modalButton, { backgroundColor: theme.colors.primary }]}
                onPress={confirmAddTeam}
                disabled={isAddingTeam}
              >
                {isAddingTeam ? (
                  <ActivityIndicator size="small" color="#fff" />
                ) : (
                  <View style={styles.modalButtonContent}>
                    <Icon icon={Plus} size={16} color="#fff" />
                    <ThemedText style={{ color: '#fff', marginLeft: 6 }} weight="semibold">
                      Agregar
                    </ThemedText>
                  </View>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  backButton: {
    width: 40,
    alignItems: 'center',
  },
  searchContainer: {
    paddingHorizontal: 16,
    paddingBottom: 12,
  },
  searchBox: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 10,
    gap: 8,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
  },
  leaguesScroll: {
    maxHeight: 50,
  },
  leaguesContainer: {
    paddingHorizontal: 16,
    gap: 8,
  },
  leagueChip: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
  },
  leagueChipContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  favoritesBar: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginTop: 12,
  },
  favoritesBarContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  teamsList: {
    padding: 12,
    paddingBottom: 100,
  },
  teamsRow: {
    justifyContent: 'space-between',
    gap: 12,
  },
  teamCard: {
    flex: 1,
    maxWidth: '48%',
    minWidth: 150,
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
    marginBottom: 12,
    alignItems: 'center',
  },
  teamLogo: {
    width: 64,
    height: 64,
    borderRadius: 32,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  teamLogoImage: {
    width: 48,
    height: 48,
  },
  teamInfo: {
    alignItems: 'center',
    marginBottom: 12,
    width: '100%',
  },
  teamName: {
    textAlign: 'center',
  },
  favoriteIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 60,
  },
  emptyText: {
    marginTop: 16,
    textAlign: 'center',
  },
  doneButtonContainer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: 16,
    paddingBottom: 32,
  },
  // New styles for API search
  searchingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8,
    marginBottom: 8,
  },
  apiBadge: {
    position: 'absolute',
    top: 6,
    right: 6,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
    zIndex: 1,
  },
  apiBadgeContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContent: {
    width: '100%',
    maxWidth: 400,
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
  },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  modalTeamPreview: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 12,
    width: '100%',
  },
  modalButtons: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 24,
    width: '100%',
  },
  modalButton: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalButtonContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
});

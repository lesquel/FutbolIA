/**
 * TeamSelector - Dropdown/Modal for selecting teams
 * Now with button-based search to reduce server load!
 */
import { useState, useEffect, useCallback, useRef, memo, useMemo } from "react";
import {
  View,
  Modal,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  Pressable,
  ActivityIndicator,
  Alert,
  Image,
  useWindowDimensions,
  Platform,
  SafeAreaView,
} from "react-native";
import { Search, X, Check, Sparkles, Loader2 } from "lucide-react-native";
import { useTheme } from "@/src/theme";
import { ThemedText, Card, Input, Button, Icon } from "@/src/components/ui";
import { teamsApi, TeamSearchResult } from "@/src/services/api";

// Solo Premier League 2025-2026
const ALLOWED_LEAGUES = ["Premier League"];

// Equipos conocidos de Premier League (para validación cuando no hay liga en la respuesta)
const PREMIER_LEAGUE_TEAMS = [
  "Arsenal",
  "Aston Villa",
  "AFC Bournemouth",
  "Brentford",
  "Brighton",
  "Brighton & Hove Albion",
  "Chelsea",
  "Crystal Palace",
  "Everton",
  "Fulham",
  "Ipswich Town",
  "Leeds United",
  "Leicester City",
  "Liverpool",
  "Manchester City",
  "Manchester United",
  "Newcastle United",
  "Nottingham Forest",
  "Southampton",
  "Sunderland",
  "Tottenham",
  "Tottenham Hotspur",
  "West Ham",
  "West Ham United",
  "Wolverhampton",
  "Wolverhampton Wanderers",
  "Burnley",
  "Luton Town",
  "Sheffield United",
];

// Función para verificar si un nombre de equipo es de Premier League
const isPremierLeagueTeam = (teamName: string): boolean => {
  const normalizedName = teamName
    .toLowerCase()
    .replace(/\s*(fc|afc)\s*$/i, "")
    .trim();
  return PREMIER_LEAGUE_TEAMS.some(
    (known) =>
      normalizedName.includes(known.toLowerCase()) ||
      known.toLowerCase().includes(normalizedName),
  );
};

// Función para filtrar equipos por ligas permitidas
const isTeamInAllowedLeague = (team: TeamSearchResult): boolean => {
  // Si tiene liga y es una de las permitidas, aceptar
  if (team.league && ALLOWED_LEAGUES.includes(team.league)) {
    return true;
  }
  // Si el nombre del equipo es conocido de Premier League, aceptar
  return isPremierLeagueTeam(team.name);
};

// Fallback teams if API is offline or for quick selection (solo Premier League 2025-2026)
// Logos from football-data.org - Usando nombres oficiales con FC
const POPULAR_TEAMS = [
  // Top 6
  {
    name: "Manchester City",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/65.png",
  },
  {
    name: "Liverpool FC",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/64.png",
  },
  {
    name: "Arsenal FC",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/57.png",
  },
  {
    name: "Chelsea FC",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/61.png",
  },
  {
    name: "Tottenham Hotspur FC",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/73.png",
  },
  {
    name: "Manchester United FC",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/66.png",
  },
  // Rest of Premier League
  {
    name: "Newcastle United FC",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/67.png",
  },
  {
    name: "Aston Villa FC",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/58.png",
  },
  {
    name: "Brighton & Hove Albion FC",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/397.png",
  },
  {
    name: "West Ham United FC",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/563.png",
  },
  {
    name: "Crystal Palace FC",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/354.png",
  },
  {
    name: "Brentford FC",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/402.png",
  },
  {
    name: "Fulham FC",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/63.png",
  },
  {
    name: "Wolverhampton Wanderers FC",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/76.png",
  },
  {
    name: "AFC Bournemouth",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/1044.png",
  },
  {
    name: "Nottingham Forest FC",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/351.png",
  },
  {
    name: "Everton FC",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/62.png",
  },
  {
    name: "Leicester City FC",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/338.png",
  },
  {
    name: "Ipswich Town FC",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/349.png",
  },
  {
    name: "Southampton FC",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/340.png",
  },
];

/**
 * Normaliza el nombre del equipo para comparación (elimina FC, AFC, espacios extra)
 */
const normalizeTeamName = (name: string): string => {
  return name
    .toLowerCase()
    .replace(/\s*(fc|afc)\s*$/i, "")
    .replace(/\s+/g, " ")
    .trim();
};

/**
 * Elimina equipos duplicados basándose en el nombre normalizado
 * Prioriza equipos con logo_url y con "FC" en el nombre
 */
const removeDuplicateTeams = (
  teams: TeamSearchResult[],
): TeamSearchResult[] => {
  const seen = new Map<string, TeamSearchResult>();

  for (const team of teams) {
    const normalized = normalizeTeamName(team.name);
    const existing = seen.get(normalized);

    if (!existing) {
      seen.set(normalized, team);
    } else {
      // Priorizar: 1) Con logo, 2) Con "FC" en el nombre, 3) Con has_players
      const shouldReplace =
        (!existing.logo_url && team.logo_url) ||
        (!existing.name.includes("FC") && team.name.includes("FC")) ||
        (!existing.has_players && team.has_players);

      if (shouldReplace) {
        seen.set(normalized, team);
      }
    }
  }

  return Array.from(seen.values());
};

interface TeamSelectorProps {
  label: string;
  selectedTeam: string | null;
  onSelectTeam: (
    team: string,
    teamData?: { logo_url?: string; league?: string },
  ) => void;
  excludeTeam?: string | null; // To prevent selecting the same team twice
  icon?: any; // LucideIcon
}

export const TeamSelector = memo(function TeamSelector({
  label,
  selectedTeam,
  onSelectTeam,
  excludeTeam,
  icon: IconComponent,
}: TeamSelectorProps) {
  const { theme } = useTheme();
  const { width: screenWidth, height: screenHeight } = useWindowDimensions();

  // Responsive breakpoints
  const isTablet = screenWidth >= 768;
  const isDesktop = screenWidth >= 1024;
  const isLargeScreen = isTablet || isDesktop;

  // Calculate responsive modal dimensions
  const modalDimensions = useMemo(() => {
    if (isDesktop) {
      return {
        width: Math.min(600, screenWidth * 0.5),
        maxHeight: screenHeight * 0.8,
        minHeight: 500,
      };
    } else if (isTablet) {
      return {
        width: Math.min(500, screenWidth * 0.65),
        maxHeight: screenHeight * 0.75,
        minHeight: 450,
      };
    }
    return {
      width: "100%" as any,
      maxHeight: "92%" as any,
      minHeight: "65%" as any,
    };
  }, [screenWidth, screenHeight, isTablet, isDesktop]);

  const [modalVisible, setModalVisible] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [teams, setTeams] = useState<TeamSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0); // Para forzar refresco
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Función para recargar equipos desde la API
  const reloadTeams = useCallback(async () => {
    const fallbackTeams = POPULAR_TEAMS.map((t) => ({
      id: t.name.toLowerCase().replaceAll(/\s+/g, "_"),
      name: t.name,
      short_name: t.name.substring(0, 3).toUpperCase(),
      league: t.league,
      logo_url: t.logo_url,
      country: "",
      has_players: true,
      player_count: 11,
    }));

    try {
      // Forzar que no use caché en el backend
      const response = await teamsApi.getTeamsWithPlayers();
      if (
        response.success &&
        response.data?.teams &&
        response.data.teams.length > 0
      ) {
        // Incluir TODOS los equipos (include_all=true equivalente)
        const combinedTeams = [...fallbackTeams, ...response.data.teams];
        setTeams(removeDuplicateTeams(combinedTeams));
        console.log(
          "✅ Teams reloaded:",
          response.data.teams.length,
          "from API",
        );
      } else {
        setTeams(fallbackTeams);
      }
    } catch (error) {
      console.log("Error reloading teams:", error);
      setTeams(fallbackTeams);
    }
  }, []);

  // Initial load of popular teams or teams with players
  useEffect(() => {
    const loadInitialTeams = async () => {
      try {
        // Set fallback teams immediately for instant UI (ya sin duplicados)
        const fallbackTeams = POPULAR_TEAMS.map((t) => ({
          id: t.name.toLowerCase().replaceAll(/\s+/g, "_"),
          name: t.name,
          short_name: t.name.substring(0, 3).toUpperCase(),
          league: t.league,
          logo_url: t.logo_url,
          country: "",
          has_players: true,
          player_count: 11,
        }));
        setTeams(fallbackTeams);

        // Then try to load from API (non-blocking)
        const response = await teamsApi.getTeamsWithPlayers();
        if (
          response.success &&
          response.data?.teams &&
          response.data.teams.length > 0
        ) {
          // Incluir TODOS los equipos, no filtrar por liga
          const combinedTeams = [...fallbackTeams, ...response.data.teams];
          setTeams(removeDuplicateTeams(combinedTeams));
        }
      } catch (error) {
        console.log("Error loading initial teams:", error);
        // Keep fallback teams on error
      }
    };

    loadInitialTeams();
  }, []);

  // Recargar equipos cuando se abre el modal
  useEffect(() => {
    if (modalVisible) {
      console.log("🔄 Modal abierto, recargando equipos...");
      reloadTeams();
    }
  }, [modalVisible, reloadTeams]);

  // Cleanup debounce timer on unmount to prevent memory leaks
  useEffect(() => {
    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
        debounceTimer.current = null;
      }
    };
  }, []);

  // Manual search function (called by button) with debouncing
  const handleSearch = useCallback(async () => {
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    debounceTimer.current = setTimeout(async () => {
      if (!searchQuery.trim()) {
        // Reset to initial teams if search is empty
        setHasSearched(false);
        await reloadTeams();
        return;
      }

      setLoading(true);
      setHasSearched(true);
      try {
        // Search with timeout handling
        const response = (await Promise.race([
          teamsApi.search(searchQuery, true),
          new Promise((_, reject) =>
            setTimeout(() => reject(new Error("Timeout")), 5000),
          ),
        ])) as any;

        if (response.success && response.data?.teams) {
          // Ya NO filtramos por liga - permitir todos los equipos
          setTeams(removeDuplicateTeams(response.data.teams));
        } else {
          // Show error but keep previous results
          Alert.alert(
            "Búsqueda",
            response.error ||
              "No se encontraron equipos. Intenta con otro nombre.",
          );
        }
      } catch (error: any) {
        console.log("Search error:", error);
        Alert.alert(
          "Error de búsqueda",
          error.message === "Timeout"
            ? "La búsqueda está tardando mucho. Intenta con un nombre más específico."
            : "Error al buscar equipos. Verifica tu conexión.",
        );
      } finally {
        setLoading(false);
      }
    }, 500); // 500ms debounce
  }, [searchQuery, reloadTeams]);

  // Reset search when modal closes
  const handleCloseModal = () => {
    setModalVisible(false);
    setSearchQuery("");
    setHasSearched(false);
  };

  const handleSelectTeam = (teamName: string, teamData?: TeamSearchResult) => {
    if (teamName === excludeTeam) return;
    // Pass team data (logo and league) along with the name
    onSelectTeam(teamName, {
      logo_url: teamData?.logo_url,
      league: teamData?.league,
    });
    handleCloseModal();
  };

  const handleAddNewTeam = async () => {
    if (!searchQuery.trim()) return;

    setIsAdding(true);
    try {
      // 1. Add the team
      const addResponse = await teamsApi.addTeam({
        name: searchQuery,
        short_name: searchQuery.substring(0, 3).toUpperCase(),
      });

      if (addResponse.success) {
        // 2. Generate players automatically so GoalMind has data to work with
        const generateResponse = await teamsApi.generatePlayers(
          searchQuery,
          15,
          75,
        );

        // 3. Refrescar caché del backend
        await teamsApi.refreshCache();

        // 4. Refrescar la lista de equipos inmediatamente
        console.log("✅ Equipo agregado, refrescando lista...");
        await reloadTeams();
        setRefreshKey((prev) => prev + 1); // Forzar re-render

        const playersGenerated = generateResponse.success
          ? generateResponse.data?.players_generated || 15
          : 0;

        Alert.alert(
          "✅ Equipo Agregado",
          `${searchQuery} ha sido agregado con ${playersGenerated} jugadores. GoalMind ya conoce a sus jugadores.`,
          [
            {
              text: "¡Genial!",
              onPress: () => {
                // Seleccionar el equipo recién agregado
                handleSelectTeam(searchQuery, {
                  id: `new_${searchQuery.toLowerCase().replace(/\s+/g, "_")}`,
                  name: searchQuery,
                  short_name: searchQuery.substring(0, 3).toUpperCase(),
                  logo_url: "",
                  country: "",
                  league: "",
                  has_players: true,
                  player_count: playersGenerated,
                });
              },
            },
          ],
        );
      } else {
        Alert.alert(
          "Error",
          addResponse.error || "No se pudo agregar el equipo",
        );
      }
    } catch (error) {
      console.error("Error adding team:", error);
      Alert.alert("Error", "Error de conexión al agregar equipo");
    } finally {
      setIsAdding(false);
    }
  };

  // Get team initials for display
  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((w) => w[0])
      .join("")
      .slice(0, 3);
  };

  // Helper to find logo from POPULAR_TEAMS
  const getTeamLogo = (
    teamName: string,
    itemLogo?: string,
  ): string | undefined => {
    if (itemLogo) return itemLogo;
    const popularTeam = POPULAR_TEAMS.find(
      (t) =>
        t.name === teamName ||
        teamName.includes(t.name) ||
        t.name.includes(teamName.replace(" FC", "").replace("FC ", "")),
    );
    return popularTeam?.logo_url;
  };

  const renderTeamItem = ({ item }: { item: TeamSearchResult }) => {
    if (item.name === excludeTeam) return null;

    const logoUrl = getTeamLogo(item.name, item.logo_url);
    // Also pass the logo when selecting the team
    const itemWithLogo = { ...item, logo_url: logoUrl || "" };

    return (
      <TouchableOpacity
        onPress={() => handleSelectTeam(item.name, itemWithLogo)}
        style={[
          styles.teamItem,
          isLargeScreen && styles.teamItemLarge,
          isDesktop && styles.teamItemDesktop,
          {
            backgroundColor:
              selectedTeam === item.name
                ? theme.colors.primary + "20"
                : "transparent",
            borderBottomColor: theme.colors.border,
          },
        ]}
        activeOpacity={0.7}
      >
        <View
          style={[
            styles.teamItemContent,
            isLargeScreen && styles.teamItemContentLarge,
          ]}
        >
          <View
            style={[
              styles.teamItemBadge,
              isLargeScreen && styles.teamItemBadgeLarge,
              { backgroundColor: theme.colors.surfaceSecondary },
            ]}
          >
            {logoUrl ? (
              <Image
                source={{ uri: logoUrl }}
                style={styles.teamLogo}
                resizeMode="contain"
              />
            ) : (
              <ThemedText weight="bold" size={isLargeScreen ? "lg" : "base"}>
                {getInitials(item.name)}
              </ThemedText>
            )}
          </View>
          <View style={{ flex: 1 }}>
            <ThemedText
              weight="semibold"
              size={isLargeScreen ? "lg" : "base"}
              numberOfLines={1}
            >
              {item.name}
            </ThemedText>
            <ThemedText variant="muted" size={isLargeScreen ? "sm" : "xs"}>
              {item.league || item.country || "Liga desconocida"}
            </ThemedText>
          </View>
          {item.has_players && (
            <View
              style={[
                styles.dataBadge,
                isLargeScreen && styles.dataBadgeLarge,
                { backgroundColor: theme.colors.success + "20" },
              ]}
            >
              <Icon
                icon={Check}
                size={isLargeScreen ? 16 : 12}
                variant="success"
              />
              <ThemedText
                size={isLargeScreen ? "sm" : "xs"}
                style={{ color: theme.colors.success, marginLeft: 4 }}
              >
                Datos
              </ThemedText>
            </View>
          )}
        </View>
        {selectedTeam === item.name && (
          <Icon icon={Check} size={isLargeScreen ? 24 : 20} variant="primary" />
        )}
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.labelRow}>
        {IconComponent ? (
          <Icon icon={IconComponent} size={16} variant="secondary" />
        ) : null}
        <ThemedText variant="secondary" size="sm" style={styles.label}>
          {label}
        </ThemedText>
      </View>

      <TouchableOpacity
        onPress={() => setModalVisible(true)}
        activeOpacity={0.7}
        style={[
          styles.selector,
          {
            backgroundColor: theme.colors.surface,
            borderColor: selectedTeam
              ? theme.colors.primary
              : theme.colors.border,
          },
        ]}
      >
        <View style={styles.selectorContent}>
          {selectedTeam ? (
            <View style={styles.selectedTeam}>
              {/* Find team data to show logo and league - prioritize POPULAR_TEAMS for logos */}
              {(() => {
                // First get logo from POPULAR_TEAMS (most reliable)
                const logoUrl = getTeamLogo(selectedTeam, undefined);
                // Then get other team data from teams list
                const teamData = teams.find((t) => t.name === selectedTeam);
                const league =
                  teamData?.league ||
                  POPULAR_TEAMS.find(
                    (t) =>
                      t.name === selectedTeam ||
                      selectedTeam.includes(t.name) ||
                      t.name.includes(
                        selectedTeam.replace(" FC", "").replace("FC ", ""),
                      ),
                  )?.league;
                return (
                  <>
                    <View
                      style={[
                        styles.teamBadge,
                        { backgroundColor: theme.colors.primary + "20" },
                      ]}
                    >
                      {logoUrl ? (
                        <Image
                          source={{ uri: logoUrl }}
                          style={styles.teamLogoSmall}
                          resizeMode="contain"
                        />
                      ) : (
                        <ThemedText variant="primary" weight="bold">
                          {getInitials(selectedTeam)}
                        </ThemedText>
                      )}
                    </View>
                    <View style={{ flex: 1 }}>
                      <ThemedText weight="semibold">{selectedTeam}</ThemedText>
                      {league ? (
                        <ThemedText variant="muted" size="xs">
                          {league}
                        </ThemedText>
                      ) : null}
                    </View>
                  </>
                );
              })()}
            </View>
          ) : (
            <ThemedText variant="muted">Seleccionar equipo...</ThemedText>
          )}
          <ThemedText variant="muted">▼</ThemedText>
        </View>
      </TouchableOpacity>

      {/* Team Selection Modal */}
      <Modal
        visible={modalVisible}
        transparent
        animationType={isLargeScreen ? "fade" : "slide"}
        onRequestClose={() => setModalVisible(false)}
        statusBarTranslucent
      >
        <Pressable
          style={[
            styles.modalOverlay,
            isLargeScreen && styles.modalOverlayCenter,
          ]}
          onPress={() => setModalVisible(false)}
        >
          <Pressable
            style={[
              styles.modalContent,
              { backgroundColor: theme.colors.background },
              isLargeScreen && [
                styles.modalContentCenter,
                {
                  width: modalDimensions.width,
                  maxHeight: modalDimensions.maxHeight,
                  minHeight: modalDimensions.minHeight,
                },
              ],
            ]}
            onPress={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <View
              style={[
                styles.modalHeader,
                isLargeScreen && styles.modalHeaderLarge,
              ]}
            >
              <ThemedText size={isLargeScreen ? "2xl" : "xl"} weight="bold">
                Seleccionar Equipo
              </ThemedText>
              <TouchableOpacity
                onPress={() => setModalVisible(false)}
                style={[
                  styles.closeButton,
                  isLargeScreen && styles.closeButtonLarge,
                ]}
                hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
              >
                <Icon icon={X} size={isLargeScreen ? 28 : 24} variant="muted" />
              </TouchableOpacity>
            </View>

            {/* Search Input with Button */}
            <View
              style={[
                styles.searchContainer,
                isLargeScreen && styles.searchContainerLarge,
              ]}
            >
              <View
                style={[
                  styles.searchInputRow,
                  isLargeScreen && styles.searchInputRowLarge,
                ]}
              >
                <View style={styles.searchInputWrapper}>
                  <Input
                    placeholder="Buscar equipo..."
                    value={searchQuery}
                    onChangeText={setSearchQuery}
                    onSubmitEditing={handleSearch}
                    returnKeyType="search"
                  />
                </View>
                <Button
                  title={isLargeScreen ? "Buscar" : ""}
                  variant="primary"
                  size={isLargeScreen ? "lg" : "md"}
                  onPress={handleSearch}
                  loading={loading}
                  icon={loading ? Loader2 : Search}
                  style={[
                    styles.searchButton,
                    isLargeScreen && styles.searchButtonLarge,
                  ]}
                />
              </View>
              {loading && (
                <ActivityIndicator
                  style={styles.searchLoader}
                  color={theme.colors.primary}
                  size={isLargeScreen ? "large" : "small"}
                />
              )}
            </View>

            {/* Team List */}
            <FlatList
              data={teams}
              keyExtractor={(item, index) => item.id || `team-${index}`}
              renderItem={renderTeamItem}
              style={styles.teamList}
              contentContainerStyle={
                isLargeScreen && styles.teamListContentLarge
              }
              showsVerticalScrollIndicator={true}
              numColumns={isDesktop ? 2 : 1}
              key={isDesktop ? "two-columns" : "one-column"}
              columnWrapperStyle={isDesktop ? styles.columnWrapper : undefined}
              ListHeaderComponent={
                hasSearched && teams.length > 0 ? (
                  <View style={styles.searchResultsHeader}>
                    <Icon icon={Check} size={16} variant="success" />
                    <ThemedText variant="muted" size="sm">
                      {teams.length} equipo(s) encontrado(s)
                    </ThemedText>
                  </View>
                ) : null
              }
              ListEmptyComponent={
                !loading ? (
                  <View style={styles.emptyContainer}>
                    <ThemedText variant="muted" style={styles.emptyText}>
                      {hasSearched && searchQuery.length > 0
                        ? `No se encontró "${searchQuery}" en la base de datos.`
                        : "Escribe el nombre del equipo y presiona buscar."}
                    </ThemedText>
                    {hasSearched && searchQuery.length >= 2 && (
                      <Card variant="outlined" style={styles.addCard}>
                        <ThemedText
                          weight="bold"
                          style={{ marginBottom: 8 }}
                        >{`¿Agregar ${searchQuery} con IA?`}</ThemedText>
                        <ThemedText
                          size="sm"
                          variant="secondary"
                          style={{ marginBottom: 16 }}
                        >
                          GoalMind buscará los jugadores reales de este equipo y
                          los guardará en la base de datos para futuras
                          consultas.
                        </ThemedText>
                        <Button
                          title={
                            isAdding
                              ? "Generando jugadores..."
                              : `Agregar ${searchQuery} con IA`
                          }
                          onPress={handleAddNewTeam}
                          disabled={isAdding}
                          loading={isAdding}
                          icon={isAdding ? Loader2 : Sparkles}
                          size="sm"
                          variant="primary"
                        />
                      </Card>
                    )}
                  </View>
                ) : null
              }
            />
          </Pressable>
        </Pressable>
      </Modal>
    </View>
  );
});

const styles = StyleSheet.create({
  container: {
    marginBottom: 18,
  },
  labelRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 10,
  },
  label: {
    flex: 1,
  },
  selector: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: 18,
    borderRadius: 14,
    borderWidth: 1,
    minHeight: 64,
  },
  selectorContent: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  selectedTeam: {
    flexDirection: "row",
    alignItems: "center",
    gap: 14,
    flex: 1,
  },
  teamBadge: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: "center",
    justifyContent: "center",
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    justifyContent: "flex-end",
  },
  modalContent: {
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    paddingHorizontal: 20,
    paddingTop: 24,
    paddingBottom: 32,
    maxHeight: "92%",
    minHeight: "65%",
  },
  modalHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 22,
  },
  searchContainer: {
    marginBottom: 14,
  },
  searchInputRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  searchInputWrapper: {
    flex: 1,
  },
  searchButton: {
    minWidth: 54,
    paddingHorizontal: 14,
  },
  searchLoader: {
    marginTop: 10,
    alignSelf: "center",
  },
  searchResultsHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    paddingVertical: 10,
    paddingHorizontal: 6,
    borderBottomWidth: 1,
    borderBottomColor: "rgba(0,0,0,0.1)",
    marginBottom: 10,
  },
  dataBadge: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 10,
  },
  teamList: {
    flex: 1,
  },
  teamItem: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 14,
    borderBottomWidth: 1,
  },
  teamItemContent: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    gap: 14,
  },
  teamItemBadge: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden",
  },
  teamLogo: {
    width: "100%",
    height: "100%",
  },
  teamLogoSmall: {
    width: "100%",
    height: "100%",
  },
  emptyContainer: {
    padding: 24,
    alignItems: "center",
  },
  emptyText: {
    textAlign: "center",
    marginBottom: 24,
    lineHeight: 22,
  },
  addCard: {
    width: "100%",
    alignItems: "center",
    padding: 18,
  },
  // ==========================================
  // RESPONSIVE STYLES FOR TABLETS AND DESKTOP
  // ==========================================
  modalOverlayCenter: {
    justifyContent: "center",
    alignItems: "center",
  },
  modalContentCenter: {
    borderRadius: 20,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 10,
  },
  modalHeaderLarge: {
    marginBottom: 28,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: "rgba(0,0,0,0.1)",
  },
  closeButton: {
    padding: 4,
  },
  closeButtonLarge: {
    padding: 8,
    borderRadius: 8,
  },
  searchContainerLarge: {
    marginBottom: 20,
  },
  searchInputRowLarge: {
    gap: 16,
  },
  searchButtonLarge: {
    minWidth: 120,
    paddingHorizontal: 20,
  },
  teamListContentLarge: {
    paddingBottom: 24,
  },
  columnWrapper: {
    gap: 12,
    paddingHorizontal: 4,
  },
  teamItemLarge: {
    paddingVertical: 18,
    paddingHorizontal: 12,
    borderRadius: 12,
    marginVertical: 4,
  },
  teamItemDesktop: {
    flex: 0.5,
    marginHorizontal: 4,
    borderWidth: 1,
    borderColor: "rgba(0,0,0,0.08)",
  },
  teamItemContentLarge: {
    gap: 18,
  },
  teamItemBadgeLarge: {
    width: 56,
    height: 56,
    borderRadius: 28,
  },
  dataBadgeLarge: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 14,
  },
});

/**
 * TeamSelector - Dropdown/Modal for selecting teams
 * Now with button-based search to reduce server load!
 */
import { useState, useEffect, useCallback, useRef, memo } from "react";
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
} from "react-native";
import { Search, X, Check, Sparkles, Loader2 } from "lucide-react-native";
import { useTheme } from "@/src/theme";
import { ThemedText, Card, Input, Button, Icon } from "@/src/components/ui";
import { teamsApi, TeamSearchResult } from "@/src/services/api";

// Fallback teams if API is offline or for quick selection
const POPULAR_TEAMS = [
  {
    name: "Real Madrid",
    league: "La Liga",
    logo_url: "https://crests.football-data.org/86.png",
  },
  {
    name: "Manchester City",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/65.png",
  },
  {
    name: "Barcelona",
    league: "La Liga",
    logo_url: "https://crests.football-data.org/81.png",
  },
  {
    name: "Bayern Munich",
    league: "Bundesliga",
    logo_url: "https://crests.football-data.org/5.png",
  },
  {
    name: "Liverpool",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/64.png",
  },
  {
    name: "Arsenal",
    league: "Premier League",
    logo_url: "https://crests.football-data.org/57.png",
  },
  {
    name: "Paris Saint-Germain",
    league: "Ligue 1",
    logo_url: "https://crests.football-data.org/524.png",
  },
  {
    name: "Inter Milan",
    league: "Serie A",
    logo_url: "https://crests.football-data.org/108.png",
  },
  {
    name: "Juventus",
    league: "Serie A",
    logo_url: "https://crests.football-data.org/109.png",
  },
  {
    name: "Atletico Madrid",
    league: "La Liga",
    logo_url: "https://crests.football-data.org/78.png",
  },
];

interface TeamSelectorProps {
  label: string;
  selectedTeam: string | null;
  onSelectTeam: (team: string) => void;
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
  const [modalVisible, setModalVisible] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [teams, setTeams] = useState<TeamSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);

  // Initial load of popular teams or teams with players
  useEffect(() => {
    const loadInitialTeams = async () => {
      try {
        const response = await teamsApi.getTeamsWithPlayers();
        if (
          response.success &&
          response.data?.teams &&
          response.data.teams.length > 0
        ) {
          setTeams(response.data.teams);
        } else {
          // Fallback to popular teams formatted as TeamSearchResult
          setTeams(
            POPULAR_TEAMS.map((t) => ({
              id: t.name.toLowerCase().replaceAll(/\s+/g, "_"),
              name: t.name,
              league: t.league,
              logo_url: t.logo_url,
              has_players: true,
              player_count: 11,
            }))
          );
        }
      } catch (error) {
        console.log("Error loading initial teams:", error);
      }
    };

    loadInitialTeams();
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
        const response = await teamsApi.getTeamsWithPlayers();
        if (response.success && response.data?.teams) {
          setTeams(response.data.teams);
        }
        return;
      }

      setLoading(true);
      setHasSearched(true);
      try {
        const response = await teamsApi.search(searchQuery, true);
        if (response.success && response.data?.teams) {
          setTeams(response.data.teams);
        }
      } catch (error) {
        console.log("Search error:", error);
      } finally {
        setLoading(false);
      }
    }, 500); // 500ms debounce
  }, [searchQuery]);

  // Reset search when modal closes
  const handleCloseModal = () => {
    setModalVisible(false);
    setSearchQuery("");
    setHasSearched(false);
  };

  const handleSelectTeam = (teamName: string) => {
    onSelectTeam(teamName);
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
        // 2. Generate players automatically so Dixie has data to work with
        await teamsApi.generatePlayers(searchQuery, 15, 75);

        Alert.alert(
          "Equipo Agregado",
          `${searchQuery} ha sido agregado con éxito. Dixie ya conoce a sus jugadores.`,
          [{ text: "¡Genial!", onPress: () => handleSelectTeam(searchQuery) }]
        );
      } else {
        Alert.alert(
          "Error",
          addResponse.error || "No se pudo agregar el equipo"
        );
      }
    } catch (error) {
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

  const renderTeamItem = ({ item }: { item: TeamSearchResult }) => {
    if (item.name === excludeTeam) return null;

    return (
      <TouchableOpacity
        onPress={() => handleSelectTeam(item.name)}
        style={[
          styles.teamItem,
          {
            backgroundColor:
              selectedTeam === item.name
                ? theme.colors.primary + "20"
                : "transparent",
            borderBottomColor: theme.colors.border,
          },
        ]}
      >
        <View style={styles.teamItemContent}>
          <View
            style={[
              styles.teamItemBadge,
              { backgroundColor: theme.colors.surfaceSecondary },
            ]}
          >
            {item.logo_url ? (
              <Image
                source={{ uri: item.logo_url }}
                style={styles.teamLogo}
                resizeMode="contain"
              />
            ) : (
              <ThemedText weight="bold">{getInitials(item.name)}</ThemedText>
            )}
          </View>
          <View style={{ flex: 1 }}>
            <ThemedText weight="semibold" numberOfLines={1}>
              {item.name}
            </ThemedText>
            <ThemedText variant="muted" size="xs">
              {item.league || item.country || "Liga desconocida"}
            </ThemedText>
          </View>
          {item.has_players && (
            <View
              style={[
                styles.dataBadge,
                { backgroundColor: theme.colors.success + "20" },
              ]}
            >
              <Icon icon={Check} size={12} variant="success" />
              <ThemedText size="xs" style={{ color: theme.colors.success, marginLeft: 4 }}>
                Datos
              </ThemedText>
            </View>
          )}
        </View>
        {selectedTeam === item.name && (
          <Icon icon={Check} size={20} variant="primary" />
        )}
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.labelRow}>
        {IconComponent && <Icon icon={IconComponent} size={16} variant="secondary" />}
        <ThemedText variant="secondary" size="sm" style={styles.label}>
          {label}
        </ThemedText>
      </View>

      <TouchableOpacity
        onPress={() => setModalVisible(true)}
        activeOpacity={0.7}
      >
        <View
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
          {selectedTeam ? (
            <View style={styles.selectedTeam}>
              <View
                style={[
                  styles.teamBadge,
                  { backgroundColor: theme.colors.primary + "20" },
                ]}
              >
                <ThemedText variant="primary" weight="bold">
                  {getInitials(selectedTeam)}
                </ThemedText>
              </View>
              <ThemedText weight="semibold">{selectedTeam}</ThemedText>
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
        animationType="slide"
        onRequestClose={() => setModalVisible(false)}
      >
        <Pressable
          style={styles.modalOverlay}
          onPress={() => setModalVisible(false)}
        >
          <Pressable
            style={[
              styles.modalContent,
              { backgroundColor: theme.colors.background },
            ]}
            onPress={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <View style={styles.modalHeader}>
              <ThemedText size="xl" weight="bold">
                Seleccionar Equipo
              </ThemedText>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Icon icon={X} size={24} variant="muted" />
              </TouchableOpacity>
            </View>

            {/* Search Input with Button */}
            <View style={styles.searchContainer}>
              <View style={styles.searchInputRow}>
                <View style={styles.searchInputWrapper}>
                  <Input
                    placeholder="Buscar equipo (ej: Emelec, Boca...)"
                    value={searchQuery}
                    onChangeText={setSearchQuery}
                    onSubmitEditing={handleSearch}
                    returnKeyType="search"
                  />
                </View>
                <Button
                  title=""
                  variant="primary"
                  size="md"
                  onPress={handleSearch}
                  loading={loading}
                  icon={loading ? Loader2 : Search}
                  style={styles.searchButton}
                />
              </View>
              {loading && (
                <ActivityIndicator
                  style={styles.searchLoader}
                  color={theme.colors.primary}
                />
              )}
            </View>

            {/* Team List */}
            <FlatList
              data={teams}
              keyExtractor={(item, index) => item.id || `team-${index}`}
              renderItem={renderTeamItem}
              style={styles.teamList}
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
                        <ThemedText weight="bold" style={{ marginBottom: 8 }}>
                          🤖 ¿Agregar {searchQuery} con IA?
                        </ThemedText>
                    <ThemedText
                      size="sm"
                      variant="secondary"
                      style={{ marginBottom: 16 }}
                    >
                      Dixie buscará los jugadores reales de este equipo y
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
    marginBottom: 16,
  },
  labelRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    marginBottom: 8,
  },
  label: {
    flex: 1,
  },
  selector: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
  },
  selectedTeam: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  teamBadge: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: "center",
    justifyContent: "center",
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    justifyContent: "flex-end",
  },
  modalContent: {
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 20,
    maxHeight: "90%",
    minHeight: "60%",
  },
  modalHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 20,
  },
  searchContainer: {
    marginBottom: 10,
  },
  searchInputRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  searchInputWrapper: {
    flex: 1,
  },
  searchButton: {
    minWidth: 50,
    paddingHorizontal: 12,
  },
  searchLoader: {
    marginTop: 8,
    alignSelf: "center",
  },
  searchResultsHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    paddingVertical: 8,
    paddingHorizontal: 4,
    borderBottomWidth: 1,
    borderBottomColor: "rgba(0,0,0,0.1)",
    marginBottom: 8,
  },
  dataBadge: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
    marginRight: 8,
  },
  teamList: {
    flex: 1,
  },
  teamItem: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 12,
    borderBottomWidth: 1,
  },
  teamItemContent: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  teamItemBadge: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: "center",
    justifyContent: "center",
    overflow: "hidden",
  },
  teamLogo: {
    width: "100%",
    height: "100%",
  },
  dataBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
    marginRight: 8,
  },
  emptyContainer: {
    padding: 20,
    alignItems: "center",
  },
  emptyText: {
    textAlign: "center",
    marginBottom: 20,
  },
  addCard: {
    width: "100%",
    alignItems: "center",
    padding: 16,
  },
});

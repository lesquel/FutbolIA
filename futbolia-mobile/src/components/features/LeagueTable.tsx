/**
 * LeagueTable - Component to display league standings
 * Shows current Premier League 2025-2026 table
 */
import { useState, useEffect, useCallback, useRef } from "react";
import {
  View,
  Modal,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  Pressable,
  ActivityIndicator,
  Image,
  RefreshControl,
  Dimensions,
  ScrollView,
  Animated,
} from "react-native";
import { X, Trophy, TrendingUp, TrendingDown, Minus } from "lucide-react-native";
import { useTheme } from "@/src/theme";
import { ThemedText, Card, Icon } from "@/src/components/ui";
import { leaguesApi, StandingsEntry } from "@/src/services/api";

const { height: SCREEN_HEIGHT } = Dimensions.get("window");

interface LeagueTableProps {
  visible: boolean;
  onClose: () => void;
}

export function LeagueTable({ visible, onClose }: LeagueTableProps) {
  const { theme } = useTheme();
  const [standings, setStandings] = useState<StandingsEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);
  const scrollY = useRef(new Animated.Value(0)).current;
  const [contentHeight, setContentHeight] = useState(0);
  const [scrollViewHeight, setScrollViewHeight] = useState(0);

  const fetchStandings = useCallback(async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    try {
      const response = await leaguesApi.getPremierLeagueStandings();
      // Handle both wrapped (success/data) and direct response formats
      const standings = response.data?.standings || (response as any).standings;
      if (standings && Array.isArray(standings)) {
        setStandings(standings);
      }
    } catch (error) {
      console.error("Error fetching standings:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    if (visible) {
      fetchStandings();
    }
  }, [visible, fetchStandings]);

  const getPositionColor = (position: number) => {
    if (position <= 4) return theme.colors.success; // Champions League
    if (position === 5) return "#f59e0b"; // Europa League
    if (position === 6) return "#8b5cf6"; // Conference League
    if (position >= 18) return theme.colors.error; // Relegation
    return theme.colors.text;
  };

  const getPositionIcon = (position: number) => {
    if (position <= 4) return TrendingUp;
    if (position >= 18) return TrendingDown;
    return Minus;
  };

  const renderHeader = () => (
    <View style={[styles.headerRow, { borderBottomColor: theme.colors.border }]}>
      <ThemedText size="xs" weight="bold" style={styles.posCol}>#</ThemedText>
      <ThemedText size="xs" weight="bold" style={styles.teamCol}>Equipo</ThemedText>
      <ThemedText size="xs" weight="bold" style={styles.statCol}>PJ</ThemedText>
      <ThemedText size="xs" weight="bold" style={styles.statCol}>G</ThemedText>
      <ThemedText size="xs" weight="bold" style={styles.statCol}>E</ThemedText>
      <ThemedText size="xs" weight="bold" style={styles.statCol}>P</ThemedText>
      <ThemedText size="xs" weight="bold" style={styles.statCol}>DG</ThemedText>
      <ThemedText size="xs" weight="bold" style={styles.ptsCol}>Pts</ThemedText>
    </View>
  );

  const renderTeamRow = ({ item, index }: { item: StandingsEntry; index: number }) => {
    const positionColor = getPositionColor(item.position);
    const isChampionsLeague = item.position <= 4;
    const isEuropaLeague = item.position === 5;
    const isConferenceLeague = item.position === 6;
    const isRelegation = item.position >= 18;

    return (
      <View
        style={[
          styles.teamRow,
          {
            backgroundColor: index % 2 === 0 ? theme.colors.surface : theme.colors.background,
            borderLeftColor: positionColor,
            borderLeftWidth: isChampionsLeague || isEuropaLeague || isConferenceLeague || isRelegation ? 3 : 0,
          },
        ]}
      >
        <View style={styles.posCol}>
          <ThemedText
            size="sm"
            weight="bold"
            style={{ color: positionColor }}
          >
            {item.position}
          </ThemedText>
        </View>
        <View style={styles.teamCol}>
          <View style={styles.teamInfo}>
            {item.team.crest ? (
              <Image
                source={{ uri: item.team.crest }}
                style={styles.teamLogo}
                resizeMode="contain"
              />
            ) : (
              <View style={[styles.teamLogoPlaceholder, { backgroundColor: theme.colors.surfaceSecondary }]}>
                <ThemedText size="xs" weight="bold">
                  {item.team.shortName?.charAt(0) || "?"}
                </ThemedText>
              </View>
            )}
            <View style={styles.teamNameContainer}>
              <ThemedText size="sm" weight="semibold" numberOfLines={1}>
                {item.team.shortName || item.team.name}
              </ThemedText>
            </View>
          </View>
        </View>
        <ThemedText size="sm" style={styles.statCol} variant="secondary">{item.playedGames}</ThemedText>
        <ThemedText size="sm" style={styles.statCol} variant="secondary">{item.won}</ThemedText>
        <ThemedText size="sm" style={styles.statCol} variant="secondary">{item.draw}</ThemedText>
        <ThemedText size="sm" style={styles.statCol} variant="secondary">{item.lost}</ThemedText>
        <ThemedText
          size="sm"
          style={[styles.statCol, { color: item.goalDifference > 0 ? theme.colors.success : item.goalDifference < 0 ? theme.colors.error : theme.colors.textSecondary }]}
        >
          {item.goalDifference > 0 ? `+${item.goalDifference}` : item.goalDifference}
        </ThemedText>
        <View style={[styles.ptsCol, styles.ptsContainer]}>
          <ThemedText size="sm" weight="bold" style={{ color: theme.colors.primary }}>
            {item.points}
          </ThemedText>
        </View>
      </View>
    );
  };

  const renderLegend = () => (
    <View style={[styles.legend, { borderTopColor: theme.colors.border }]}>
      <View style={styles.legendItem}>
        <View style={[styles.legendDot, { backgroundColor: theme.colors.success }]} />
        <ThemedText size="xs" variant="muted">Champions League</ThemedText>
      </View>
      <View style={styles.legendItem}>
        <View style={[styles.legendDot, { backgroundColor: "#f59e0b" }]} />
        <ThemedText size="xs" variant="muted">Europa League</ThemedText>
      </View>
      <View style={styles.legendItem}>
        <View style={[styles.legendDot, { backgroundColor: "#8b5cf6" }]} />
        <ThemedText size="xs" variant="muted">Conference</ThemedText>
      </View>
      <View style={styles.legendItem}>
        <View style={[styles.legendDot, { backgroundColor: theme.colors.error }]} />
        <ThemedText size="xs" variant="muted">Descenso</ThemedText>
      </View>
    </View>
  );

  return (
    <Modal
      visible={visible}
      transparent
      animationType="slide"
      onRequestClose={onClose}
    >
      <View style={styles.modalOverlay}>
        <Pressable
          style={styles.modalBackdrop}
          onPress={onClose}
        />
        <View
          style={[styles.modalContent, { backgroundColor: theme.colors.background }]}
        >
          {/* Header */}
          <View style={[styles.modalHeader, { borderBottomColor: theme.colors.border }]}>
            <View style={styles.titleContainer}>
              <Icon icon={Trophy} size={24} variant="primary" />
              <View style={styles.titleText}>
                <ThemedText size="xl" weight="bold">Premier League</ThemedText>
                <ThemedText size="sm" variant="muted">Temporada 2025-2026</ThemedText>
              </View>
            </View>
            <TouchableOpacity onPress={onClose} style={styles.closeButton}>
              <Icon icon={X} size={24} variant="muted" />
            </TouchableOpacity>
          </View>

          {/* Content */}
          {loading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color={theme.colors.primary} />
              <ThemedText variant="muted" style={{ marginTop: 12 }}>
                Cargando tabla de posiciones...
              </ThemedText>
            </View>
          ) : (
            <View style={styles.scrollContainer}>
              <ScrollView
                ref={scrollViewRef}
                style={styles.scrollView}
                contentContainerStyle={styles.scrollContent}
                showsVerticalScrollIndicator={false}
                scrollEnabled={true}
                nestedScrollEnabled={true}
                bounces={true}
                onScroll={Animated.event(
                  [{ nativeEvent: { contentOffset: { y: scrollY } } }],
                  { useNativeDriver: false }
                )}
                onContentSizeChange={(width, height) => setContentHeight(height)}
                onLayout={(event) => setScrollViewHeight(event.nativeEvent.layout.height)}
                scrollEventThrottle={16}
                refreshControl={
                  <RefreshControl
                    refreshing={refreshing}
                    onRefresh={() => fetchStandings(true)}
                    tintColor={theme.colors.primary}
                  />
                }
              >
                {renderHeader()}
                {standings.map((item, index) => renderTeamRow({ item, index }))}
                {renderLegend()}
              </ScrollView>
              
              {/* Custom Scrollbar */}
              {contentHeight > scrollViewHeight && (
                <View style={styles.scrollbarTrack}>
                  <Animated.View
                    style={[
                      styles.scrollbarThumb,
                      {
                        backgroundColor: theme.colors.primary + "80",
                        height: Math.max(
                          (scrollViewHeight / contentHeight) * scrollViewHeight,
                          30
                        ),
                        transform: [
                          {
                            translateY: scrollY.interpolate({
                              inputRange: [0, Math.max(contentHeight - scrollViewHeight, 1)],
                              outputRange: [0, scrollViewHeight - Math.max((scrollViewHeight / contentHeight) * scrollViewHeight, 30)],
                              extrapolate: "clamp",
                            }),
                          },
                        ],
                      },
                    ]}
                  />
                </View>
              )}
            </View>
          )}
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    justifyContent: "flex-end",
  },
  modalBackdrop: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "rgba(0, 0, 0, 0.7)",
  },
  modalContent: {
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    maxHeight: SCREEN_HEIGHT * 0.9,
    minHeight: SCREEN_HEIGHT * 0.7,
    flexDirection: "column",
    overflow: "hidden",
  },
  scrollContainer: {
    flex: 1,
    width: "100%",
    position: "relative",
  },
  scrollView: {
    flex: 1,
    width: "100%",
  },
  scrollContent: {
    paddingBottom: 20,
  },
  scrollbarTrack: {
    position: "absolute",
    right: 2,
    top: 0,
    bottom: 0,
    width: 4,
    backgroundColor: "rgba(0, 0, 0, 0.1)",
    borderRadius: 2,
  },
  scrollbarThumb: {
    width: 4,
    borderRadius: 2,
    position: "absolute",
    right: 0,
  },
  modalHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 20,
    borderBottomWidth: 1,
  },
  titleContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  titleText: {
    gap: 2,
  },
  closeButton: {
    padding: 8,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingVertical: 60,
  },
  listContent: {
    paddingBottom: 20,
  },
  headerRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
  },
  teamRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  posCol: {
    width: 28,
    alignItems: "center",
  },
  teamCol: {
    flex: 1,
    paddingRight: 8,
  },
  teamInfo: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  teamLogo: {
    width: 24,
    height: 24,
  },
  teamLogoPlaceholder: {
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: "center",
    alignItems: "center",
  },
  teamNameContainer: {
    flex: 1,
  },
  statCol: {
    width: 28,
    textAlign: "center",
  },
  ptsCol: {
    width: 36,
    alignItems: "center",
  },
  ptsContainer: {
    borderRadius: 4,
    paddingVertical: 2,
    paddingHorizontal: 4,
  },
  legend: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "center",
    gap: 16,
    paddingVertical: 16,
    paddingHorizontal: 16,
    marginTop: 8,
    borderTopWidth: 1,
  },
  legendItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  legendDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
});


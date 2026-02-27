/**
 * LeagueTable - Component to display league standings
 * Shows current Premier League 2025-2026 table
 */
import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
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
  useWindowDimensions,
  ScrollView,
  Animated,
  Platform,
} from 'react-native';
import { X, Trophy, TrendingUp, TrendingDown, Minus } from 'lucide-react-native';
import { useTheme } from '@/src/theme';
import { ThemedText, Card, Icon } from '@/src/components/ui';
import { leaguesApi, StandingsEntry } from '@/src/services/api';

interface LeagueTableProps {
  visible: boolean;
  onClose: () => void;
}

export function LeagueTable({ visible, onClose }: LeagueTableProps) {
  const { theme } = useTheme();

  // Responsive breakpoints
  const { width: screenWidth, height: screenHeight } = useWindowDimensions();
  const isTablet = screenWidth >= 768;
  const isDesktop = screenWidth >= 1024;
  const isLargeScreen = isTablet || isDesktop;

  // Calculate responsive modal dimensions
  const modalDimensions = useMemo(() => {
    if (isDesktop) {
      return {
        width: Math.min(700, screenWidth * 0.6),
        maxHeight: screenHeight * 0.85,
        minHeight: screenHeight * 0.6,
      };
    } else if (isTablet) {
      return {
        width: Math.min(600, screenWidth * 0.75),
        maxHeight: screenHeight * 0.8,
        minHeight: screenHeight * 0.6,
      };
    }
    return {
      maxHeight: screenHeight * 0.92,
      minHeight: screenHeight * 0.75,
    };
  }, [screenWidth, screenHeight, isTablet, isDesktop]);

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
      console.error('Error fetching standings:', error);
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
    if (position === 5) return '#f59e0b'; // Europa League
    if (position === 6) return '#8b5cf6'; // Conference League
    if (position >= 18) return theme.colors.error; // Relegation
    return theme.colors.text;
  };

  const getPositionIcon = (position: number) => {
    if (position <= 4) return TrendingUp;
    if (position >= 18) return TrendingDown;
    return Minus;
  };

  const renderHeader = () => (
    <View
      style={[
        styles.headerRow,
        isLargeScreen && styles.headerRowLarge,
        { borderBottomColor: theme.colors.border },
      ]}
    >
      <ThemedText
        size={isLargeScreen ? 'sm' : 'xs'}
        weight="bold"
        style={[styles.posCol, isLargeScreen && styles.posColLarge]}
      >
        #
      </ThemedText>
      <ThemedText
        size={isLargeScreen ? 'sm' : 'xs'}
        weight="bold"
        style={[styles.teamCol, isLargeScreen && styles.teamColLarge]}
      >
        Equipo
      </ThemedText>
      <ThemedText
        size={isLargeScreen ? 'sm' : 'xs'}
        weight="bold"
        style={[styles.statCol, isLargeScreen && styles.statColLarge]}
      >
        PJ
      </ThemedText>
      <ThemedText
        size={isLargeScreen ? 'sm' : 'xs'}
        weight="bold"
        style={[styles.statCol, isLargeScreen && styles.statColLarge]}
      >
        G
      </ThemedText>
      <ThemedText
        size={isLargeScreen ? 'sm' : 'xs'}
        weight="bold"
        style={[styles.statCol, isLargeScreen && styles.statColLarge]}
      >
        E
      </ThemedText>
      <ThemedText
        size={isLargeScreen ? 'sm' : 'xs'}
        weight="bold"
        style={[styles.statCol, isLargeScreen && styles.statColLarge]}
      >
        P
      </ThemedText>
      <ThemedText
        size={isLargeScreen ? 'sm' : 'xs'}
        weight="bold"
        style={[styles.statCol, isLargeScreen && styles.statColLarge]}
      >
        DG
      </ThemedText>
      <ThemedText
        size={isLargeScreen ? 'sm' : 'xs'}
        weight="bold"
        style={[styles.ptsCol, isLargeScreen && styles.ptsColLarge]}
      >
        Pts
      </ThemedText>
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
          isLargeScreen && styles.teamRowLarge,
          {
            backgroundColor: index % 2 === 0 ? theme.colors.surface : theme.colors.background,
            borderLeftColor: positionColor,
            borderLeftWidth:
              isChampionsLeague || isEuropaLeague || isConferenceLeague || isRelegation ? 3 : 0,
          },
        ]}
      >
        <View style={[styles.posCol, isLargeScreen && styles.posColLarge]}>
          <ThemedText
            size={isLargeScreen ? 'base' : 'sm'}
            weight="bold"
            style={{ color: positionColor }}
          >
            {item.position}
          </ThemedText>
        </View>
        <View style={[styles.teamCol, isLargeScreen && styles.teamColLarge]}>
          <View style={[styles.teamInfo, isLargeScreen && styles.teamInfoLarge]}>
            {item.team.crest ? (
              <Image
                source={{ uri: item.team.crest }}
                style={[styles.teamLogo, isLargeScreen && styles.teamLogoLarge]}
                resizeMode="contain"
              />
            ) : (
              <View
                style={[
                  styles.teamLogoPlaceholder,
                  isLargeScreen && styles.teamLogoPlaceholderLarge,
                  { backgroundColor: theme.colors.surfaceSecondary },
                ]}
              >
                <ThemedText size={isLargeScreen ? 'sm' : 'xs'} weight="bold">
                  {item.team.shortName?.charAt(0) || '?'}
                </ThemedText>
              </View>
            )}
            <View style={styles.teamNameContainer}>
              <ThemedText size={isLargeScreen ? 'base' : 'sm'} weight="semibold" numberOfLines={1}>
                {item.team.shortName || item.team.name}
              </ThemedText>
            </View>
          </View>
        </View>
        <ThemedText
          size={isLargeScreen ? 'base' : 'sm'}
          style={[styles.statCol, isLargeScreen && styles.statColLarge]}
          variant="secondary"
        >
          {item.playedGames}
        </ThemedText>
        <ThemedText
          size={isLargeScreen ? 'base' : 'sm'}
          style={[styles.statCol, isLargeScreen && styles.statColLarge]}
          variant="secondary"
        >
          {item.won}
        </ThemedText>
        <ThemedText
          size={isLargeScreen ? 'base' : 'sm'}
          style={[styles.statCol, isLargeScreen && styles.statColLarge]}
          variant="secondary"
        >
          {item.draw}
        </ThemedText>
        <ThemedText
          size={isLargeScreen ? 'base' : 'sm'}
          style={[styles.statCol, isLargeScreen && styles.statColLarge]}
          variant="secondary"
        >
          {item.lost}
        </ThemedText>
        <ThemedText
          size={isLargeScreen ? 'base' : 'sm'}
          style={[
            styles.statCol,
            isLargeScreen && styles.statColLarge,
            {
              color:
                item.goalDifference > 0
                  ? theme.colors.success
                  : item.goalDifference < 0
                    ? theme.colors.error
                    : theme.colors.textSecondary,
            },
          ]}
        >
          {item.goalDifference > 0 ? `+${item.goalDifference}` : item.goalDifference}
        </ThemedText>
        <View style={[styles.ptsCol, styles.ptsContainer, isLargeScreen && styles.ptsColLarge]}>
          <ThemedText
            size={isLargeScreen ? 'base' : 'sm'}
            weight="bold"
            style={{ color: theme.colors.primary }}
          >
            {item.points}
          </ThemedText>
        </View>
      </View>
    );
  };

  const renderLegend = () => (
    <View
      style={[
        styles.legend,
        isLargeScreen && styles.legendLarge,
        { borderTopColor: theme.colors.border },
      ]}
    >
      <View style={[styles.legendItem, isLargeScreen && styles.legendItemLarge]}>
        <View
          style={[
            styles.legendDot,
            isLargeScreen && styles.legendDotLarge,
            { backgroundColor: theme.colors.success },
          ]}
        />
        <ThemedText size={isLargeScreen ? 'sm' : 'xs'} variant="muted">
          Champions League
        </ThemedText>
      </View>
      <View style={[styles.legendItem, isLargeScreen && styles.legendItemLarge]}>
        <View
          style={[
            styles.legendDot,
            isLargeScreen && styles.legendDotLarge,
            { backgroundColor: '#f59e0b' },
          ]}
        />
        <ThemedText size={isLargeScreen ? 'sm' : 'xs'} variant="muted">
          Europa League
        </ThemedText>
      </View>
      <View style={[styles.legendItem, isLargeScreen && styles.legendItemLarge]}>
        <View
          style={[
            styles.legendDot,
            isLargeScreen && styles.legendDotLarge,
            { backgroundColor: '#8b5cf6' },
          ]}
        />
        <ThemedText size={isLargeScreen ? 'sm' : 'xs'} variant="muted">
          Conference
        </ThemedText>
      </View>
      <View style={[styles.legendItem, isLargeScreen && styles.legendItemLarge]}>
        <View
          style={[
            styles.legendDot,
            isLargeScreen && styles.legendDotLarge,
            { backgroundColor: theme.colors.error },
          ]}
        />
        <ThemedText size={isLargeScreen ? 'sm' : 'xs'} variant="muted">
          Descenso
        </ThemedText>
      </View>
    </View>
  );

  return (
    <Modal
      visible={visible}
      transparent
      animationType={isLargeScreen ? 'fade' : 'slide'}
      onRequestClose={onClose}
      statusBarTranslucent
    >
      <View style={[styles.modalOverlay, isLargeScreen && styles.modalOverlayCenter]}>
        <Pressable style={styles.modalBackdrop} onPress={onClose} />
        <View
          style={[
            styles.modalContent,
            isLargeScreen && [
              styles.modalContentCenter,
              {
                width: modalDimensions.width,
                maxHeight: modalDimensions.maxHeight,
                minHeight: modalDimensions.minHeight,
              },
              Platform.select({
                web: {
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)',
                },
                default: {
                  shadowColor: '#000',
                  shadowOffset: { width: 0, height: 4 },
                  shadowOpacity: 0.3,
                  shadowRadius: 12,
                  elevation: 10,
                },
              }),
            ],
            { backgroundColor: theme.colors.background },
          ]}
        >
          {/* Header */}
          <View
            style={[
              styles.modalHeader,
              isLargeScreen && styles.modalHeaderLarge,
              { borderBottomColor: theme.colors.border },
            ]}
          >
            <View style={[styles.titleContainer, isLargeScreen && styles.titleContainerLarge]}>
              <Icon icon={Trophy} size={isLargeScreen ? 32 : 24} variant="primary" />
              <View style={styles.titleText}>
                <ThemedText size={isLargeScreen ? '2xl' : 'xl'} weight="bold">
                  Premier League
                </ThemedText>
                <ThemedText size={isLargeScreen ? 'base' : 'sm'} variant="muted">
                  Temporada 2025-2026
                </ThemedText>
              </View>
            </View>
            <TouchableOpacity
              onPress={onClose}
              style={[styles.closeButton, isLargeScreen && styles.closeButtonLarge]}
              hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
            >
              <Icon icon={X} size={isLargeScreen ? 28 : 24} variant="muted" />
            </TouchableOpacity>
          </View>

          {/* Content */}
          {loading ? (
            <View style={[styles.loadingContainer, isLargeScreen && styles.loadingContainerLarge]}>
              <ActivityIndicator size="large" color={theme.colors.primary} />
              <ThemedText
                variant="muted"
                size={isLargeScreen ? 'base' : 'sm'}
                style={{ marginTop: 16 }}
              >
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
                onScroll={Animated.event([{ nativeEvent: { contentOffset: { y: scrollY } } }], {
                  useNativeDriver: false,
                })}
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
                {standings.map((item, index) => (
                  <View key={`team-${item.position}-${item.team.name}`}>
                    {renderTeamRow({ item, index })}
                  </View>
                ))}
                {renderLegend()}
              </ScrollView>

              {/* Custom Scrollbar */}
              {contentHeight > scrollViewHeight && (
                <View style={styles.scrollbarTrack}>
                  <Animated.View
                    style={[
                      styles.scrollbarThumb,
                      {
                        backgroundColor: theme.colors.primary + '80',
                        height: Math.max((scrollViewHeight / contentHeight) * scrollViewHeight, 30),
                        transform: [
                          {
                            translateY: scrollY.interpolate({
                              inputRange: [0, Math.max(contentHeight - scrollViewHeight, 1)],
                              outputRange: [
                                0,
                                scrollViewHeight -
                                  Math.max(
                                    (scrollViewHeight / contentHeight) * scrollViewHeight,
                                    30,
                                  ),
                              ],
                              extrapolate: 'clamp',
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
    justifyContent: 'flex-end',
  },
  modalBackdrop: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
  },
  modalContent: {
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    maxHeight: '92%',
    minHeight: '75%',
    flexDirection: 'column',
    overflow: 'hidden',
  },
  scrollContainer: {
    flex: 1,
    width: '100%',
    position: 'relative',
  },
  scrollView: {
    flex: 1,
    width: '100%',
  },
  scrollContent: {
    paddingBottom: 24,
  },
  scrollbarTrack: {
    position: 'absolute',
    right: 3,
    top: 0,
    bottom: 0,
    width: 5,
    backgroundColor: 'rgba(0, 0, 0, 0.1)',
    borderRadius: 3,
  },
  scrollbarThumb: {
    width: 5,
    borderRadius: 3,
    position: 'absolute',
    right: 0,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 22,
    borderBottomWidth: 1,
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    flex: 1,
  },
  titleText: {
    gap: 4,
    flex: 1,
  },
  closeButton: {
    padding: 10,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 70,
  },
  listContent: {
    paddingBottom: 24,
  },
  headerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
  },
  teamRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  posCol: {
    width: 32,
    alignItems: 'center',
  },
  teamCol: {
    flex: 1,
    paddingRight: 10,
    minWidth: 0,
  },
  teamInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  teamLogo: {
    width: 28,
    height: 28,
  },
  teamLogoPlaceholder: {
    width: 28,
    height: 28,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
  },
  teamNameContainer: {
    flex: 1,
    minWidth: 0,
  },
  statCol: {
    width: 30,
    textAlign: 'center',
  },
  ptsCol: {
    width: 40,
    alignItems: 'center',
  },
  ptsContainer: {
    borderRadius: 6,
    paddingVertical: 3,
    paddingHorizontal: 6,
  },
  legend: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: 14,
    paddingVertical: 18,
    paddingHorizontal: 16,
    marginTop: 10,
    borderTopWidth: 1,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  legendDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  // ==========================================
  // RESPONSIVE STYLES FOR TABLETS AND DESKTOP
  // ==========================================
  modalOverlayCenter: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContentCenter: {
    borderRadius: 20,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  modalHeaderLarge: {
    paddingHorizontal: 28,
    paddingVertical: 28,
  },
  titleContainerLarge: {
    gap: 18,
  },
  closeButtonLarge: {
    padding: 14,
  },
  loadingContainerLarge: {
    paddingVertical: 100,
  },
  headerRowLarge: {
    paddingHorizontal: 24,
    paddingVertical: 18,
  },
  teamRowLarge: {
    paddingHorizontal: 24,
    paddingVertical: 16,
  },
  posColLarge: {
    width: 44,
  },
  teamColLarge: {
    paddingRight: 16,
  },
  teamInfoLarge: {
    gap: 14,
  },
  teamLogoLarge: {
    width: 36,
    height: 36,
  },
  teamLogoPlaceholderLarge: {
    width: 36,
    height: 36,
    borderRadius: 18,
  },
  statColLarge: {
    width: 40,
  },
  ptsColLarge: {
    width: 52,
  },
  legendLarge: {
    gap: 20,
    paddingVertical: 24,
    paddingHorizontal: 24,
    marginTop: 16,
  },
  legendItemLarge: {
    gap: 10,
  },
  legendDotLarge: {
    width: 14,
    height: 14,
    borderRadius: 7,
  },
});

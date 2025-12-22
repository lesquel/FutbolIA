/**
 * FutbolIA - History Screen
 * User's prediction history and statistics
 */
import { useState, useEffect, useCallback } from 'react';
import { 
  ScrollView, 
  View, 
  StyleSheet, 
  RefreshControl,
  FlatList,
} from 'react-native';
import { useFocusEffect } from 'expo-router';
import { useTranslation } from 'react-i18next';

import { useTheme } from '@/src/theme';
import { ThemedView, ThemedText, Card, Button, TeamBadge } from '@/src/components/ui';
import { predictionsApi, Prediction, PredictionStats } from '@/src/services/api';

export default function HistoryScreen() {
  const { theme } = useTheme();
  const { t } = useTranslation();
  
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [stats, setStats] = useState<PredictionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  
  // Reload data when screen comes into focus
  useFocusEffect(
    useCallback(() => {
      loadHistory();
    }, [])
  );
  
  const loadHistory = async () => {
    try {
      const response = await predictionsApi.getHistory(20);
      if (response.success && response.data) {
        setPredictions(response.data.predictions || []);
        setStats(response.data.stats || null);
      }
    } catch (error) {
      console.log('Error loading history:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };
  
  const onRefresh = () => {
    setRefreshing(true);
    loadHistory();
  };
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  };
  
  const renderPredictionItem = ({ item }: { item: Prediction }) => (
    <Card variant="default" padding="md" style={styles.predictionCard}>
      {/* Match Header */}
      <View style={styles.cardHeader}>
        <ThemedText variant="muted" size="xs">
          {item.match?.league || 'Liga'}
        </ThemedText>
        <ThemedText variant="muted" size="xs">
          {formatDate(item.created_at)}
        </ThemedText>
      </View>
      
      {/* Teams */}
      <View style={styles.teamsRow}>
        <View style={styles.teamInfo}>
          <ThemedText weight="semibold" size="sm" numberOfLines={1}>
            {item.match?.home_team?.name || 'Local'}
          </ThemedText>
        </View>
        
        <View style={styles.scoreBox}>
          <ThemedText 
            size="lg" 
            weight="bold"
            style={{ color: theme.colors.primary }}
          >
            {item.result?.predicted_score || '?-?'}
          </ThemedText>
        </View>
        
        <View style={[styles.teamInfo, { alignItems: 'flex-end' }]}>
          <ThemedText weight="semibold" size="sm" numberOfLines={1}>
            {item.match?.away_team?.name || 'Visitante'}
          </ThemedText>
        </View>
      </View>
      
      {/* Prediction Result */}
      <View 
        style={[
          styles.resultBadge,
          { 
            backgroundColor: theme.colors.primary + '15',
            borderColor: theme.colors.primary + '30',
          },
        ]}
      >
        <ThemedText variant="primary" size="sm" weight="semibold">
          🏆 {item.result?.winner || 'Sin resultado'}
        </ThemedText>
        <ThemedText variant="muted" size="xs">
          {item.result?.confidence || 0}% confianza
        </ThemedText>
      </View>
    </Card>
  );
  
  return (
    <ThemedView variant="background" style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={theme.colors.primary}
          />
        }
      >
        {/* Stats Cards */}
        <View style={styles.statsContainer}>
          <Card variant="elevated" padding="md" style={styles.statCard}>
            <ThemedText 
              size="2xl" 
              weight="bold"
              style={{ color: theme.colors.primary }}
            >
              {stats?.total_predictions || 0}
            </ThemedText>
            <ThemedText variant="muted" size="xs">
              {t('history.totalPredictions')}
            </ThemedText>
          </Card>
          
          <Card variant="elevated" padding="md" style={styles.statCard}>
            <ThemedText 
              size="2xl" 
              weight="bold"
              style={{ color: theme.colors.success }}
            >
              {stats?.correct_predictions || 0}
            </ThemedText>
            <ThemedText variant="muted" size="xs">
              {t('history.correctPredictions')}
            </ThemedText>
          </Card>
          
          <Card variant="elevated" padding="md" style={styles.statCard}>
            <ThemedText 
              size="2xl" 
              weight="bold"
              style={{ color: theme.colors.accentGold }}
            >
              {stats?.accuracy || 0}%
            </ThemedText>
            <ThemedText variant="muted" size="xs">
              {t('history.accuracy')}
            </ThemedText>
          </Card>
        </View>
        
        {/* Predictions List */}
        <View style={styles.listHeader}>
          <ThemedText size="lg" weight="semibold">
            📋 {t('history.title')}
          </ThemedText>
        </View>
        
        {predictions.length > 0 ? (
          predictions.map((prediction) => (
            <View key={prediction.id}>
              {renderPredictionItem({ item: prediction })}
            </View>
          ))
        ) : (
          <Card variant="outlined" padding="lg" style={styles.emptyCard}>
            <ThemedText size="3xl" style={styles.emptyIcon}>📊</ThemedText>
            <ThemedText variant="muted" style={styles.emptyText}>
              {t('history.noPredictions')}
            </ThemedText>
            <ThemedText variant="secondary" size="sm">
              {t('history.startPredicting')}
            </ThemedText>
          </Card>
        )}
      </ScrollView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 32,
  },
  statsContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  statCard: {
    flex: 1,
    alignItems: 'center',
  },
  listHeader: {
    marginBottom: 16,
  },
  predictionCard: {
    marginBottom: 12,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  teamsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  teamInfo: {
    flex: 1,
  },
  scoreBox: {
    paddingHorizontal: 16,
    alignItems: 'center',
  },
  resultBadge: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 10,
    borderRadius: 8,
    borderWidth: 1,
  },
  emptyCard: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyIcon: {
    marginBottom: 16,
  },
  emptyText: {
    marginBottom: 8,
  },
});

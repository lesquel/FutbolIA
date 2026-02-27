/**
 * FutbolIA - Profile Screen
 * User profile management with favorite teams
 */
import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Image,
  useWindowDimensions,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';

import { useTheme } from '@/src/theme';
import { useAuth } from '@/src/context';
import { ThemedView, ThemedText, Card, Button, Icon } from '@/src/components/ui';
import { BarChart3, Trophy, Settings } from 'lucide-react-native';

export default function ProfileScreen() {
  const { theme } = useTheme();
  const { t } = useTranslation();
  const { user, isAuthenticated, logout } = useAuth();
  const router = useRouter();
  const { width: screenWidth } = useWindowDimensions();
  const isTablet = screenWidth >= 768;
  const isDesktop = screenWidth >= 1024;
  const isLargeScreen = isTablet || isDesktop;

  const [stats] = useState({
    totalPredictions: 47,
    correctPredictions: 32,
    streak: 5,
    favoriteLeague: 'La Liga',
  });

  const accuracy =
    stats.totalPredictions > 0
      ? Math.round((stats.correctPredictions / stats.totalPredictions) * 100)
      : 0;

  const handleLogout = () => {
    Alert.alert(t('profile.logoutTitle'), t('profile.logoutMessage'), [
      { text: t('common.cancel'), style: 'cancel' },
      {
        text: t('profile.logout'),
        style: 'destructive',
        onPress: () => {
          void logout().then(() => {
            router.replace('/login');
          });
        },
      },
    ]);
  };

  // If not authenticated, show login prompt
  if (!isAuthenticated) {
    return (
      <ThemedView variant="background" style={styles.container}>
        <View style={styles.notAuthContainer}>
          <ThemedText size="3xl" style={styles.notAuthEmoji}>
            👤
          </ThemedText>
          <ThemedText size="xl" weight="semibold" style={styles.notAuthTitle}>
            {t('profile.notLoggedIn')}
          </ThemedText>
          <ThemedText variant="secondary" style={styles.notAuthSubtitle}>
            {t('profile.loginPrompt')}
          </ThemedText>
          <Button
            title={t('auth.login')}
            variant="primary"
            size="lg"
            onPress={() => router.push('/login')}
            style={styles.loginButton}
          />
          <TouchableOpacity onPress={() => router.push('/register')}>
            <ThemedText variant="primary">
              {t('auth.noAccount')} {t('auth.registerNow')}
            </ThemedText>
          </TouchableOpacity>
        </View>
      </ThemedView>
    );
  }

  return (
    <ThemedView variant="background" style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Profile Header */}
        <Card variant="elevated" padding="lg" style={styles.profileCard}>
          <View style={styles.avatarContainer}>
            <View style={[styles.avatar, { backgroundColor: theme.colors.primary }]}>
              <ThemedText size="3xl" weight="bold" style={{ color: '#fff' }}>
                {user?.username?.[0]?.toUpperCase() || 'U'}
              </ThemedText>
            </View>
            <View style={styles.userInfo}>
              <ThemedText size="xl" weight="bold">
                {user?.username || 'Usuario'}
              </ThemedText>
              <ThemedText variant="secondary">{user?.email || 'email@example.com'}</ThemedText>
              <View style={styles.memberBadge}>
                <ThemedText size="xs" style={{ color: theme.colors.primary }}>
                  ⭐ {t('profile.member')}
                </ThemedText>
              </View>
            </View>
          </View>
        </Card>

        {/* Stats Section */}
        <View style={styles.section}>
          <View style={styles.statsTitleRow}>
            <Icon icon={BarChart3} size={18} variant="primary" />
            <ThemedText size="lg" weight="semibold" style={styles.sectionTitle}>
              {t('profile.statistics')}
            </ThemedText>
          </View>

          <View style={styles.statsGrid}>
            <Card variant="outlined" padding="md" style={styles.statCard}>
              <ThemedText size="2xl" weight="bold" style={{ color: theme.colors.primary }}>
                {stats.totalPredictions}
              </ThemedText>
              <ThemedText variant="secondary" size="sm">
                {t('profile.totalPredictions')}
              </ThemedText>
            </Card>

            <Card variant="outlined" padding="md" style={styles.statCard}>
              <ThemedText size="2xl" weight="bold" style={{ color: theme.colors.success }}>
                {accuracy}%
              </ThemedText>
              <ThemedText variant="secondary" size="sm">
                {t('profile.accuracy')}
              </ThemedText>
            </Card>

            <Card variant="outlined" padding="md" style={styles.statCard}>
              <ThemedText size="2xl" weight="bold" style={{ color: theme.colors.warning }}>
                🔥 {stats.streak}
              </ThemedText>
              <ThemedText variant="secondary" size="sm">
                {t('profile.streak')}
              </ThemedText>
            </Card>

            <Card variant="outlined" padding="md" style={styles.statCard}>
              <Icon icon={Trophy} size={32} variant="primary" />
              <ThemedText variant="secondary" size="sm" numberOfLines={1}>
                {stats.favoriteLeague}
              </ThemedText>
            </Card>
          </View>
        </View>

        {/* Account Actions */}
        <View style={styles.section}>
          <View style={styles.statsTitleRow}>
            <Icon icon={Settings} size={18} variant="primary" />
            <ThemedText size="lg" weight="semibold" style={styles.sectionTitle}>
              {t('profile.account')}
            </ThemedText>
          </View>

          <Card variant="default" padding="none">
            <TouchableOpacity
              style={styles.actionRow}
              onPress={() => {
                /* Edit profile */
              }}
            >
              <ThemedText>✏️</ThemedText>
              <ThemedText style={styles.actionText}>{t('profile.editProfile')}</ThemedText>
              <ThemedText variant="muted">→</ThemedText>
            </TouchableOpacity>

            <View style={[styles.divider, { backgroundColor: theme.colors.border }]} />

            <TouchableOpacity style={styles.actionRow} onPress={() => router.push('/settings')}>
              <Icon icon={Settings} size={20} variant="primary" />
              <ThemedText style={styles.actionText}>{t('profile.settings')}</ThemedText>
              <ThemedText variant="muted">→</ThemedText>
            </TouchableOpacity>

            <View style={[styles.divider, { backgroundColor: theme.colors.border }]} />

            <TouchableOpacity style={styles.actionRow} onPress={handleLogout}>
              <ThemedText>🚪</ThemedText>
              <ThemedText style={[styles.actionText, { color: theme.colors.error }]}>
                {t('profile.logout')}
              </ThemedText>
              <ThemedText style={{ color: theme.colors.error }}>→</ThemedText>
            </TouchableOpacity>
          </Card>
        </View>
      </ScrollView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 40,
  },
  notAuthContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 32,
    paddingVertical: 48,
  },
  notAuthEmoji: {
    marginBottom: 20,
  },
  notAuthTitle: {
    marginBottom: 12,
    textAlign: 'center',
  },
  notAuthSubtitle: {
    marginBottom: 28,
    textAlign: 'center',
    lineHeight: 22,
  },
  loginButton: {
    marginBottom: 18,
    minWidth: 220,
  },
  profileCard: {
    marginBottom: 24,
  },
  avatarContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 76,
    height: 76,
    borderRadius: 38,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 18,
  },
  userInfo: {
    flex: 1,
  },
  memberBadge: {
    marginTop: 6,
  },
  section: {
    marginBottom: 28,
  },
  sectionTitle: {
    marginBottom: 14,
    flex: 1,
  },
  statsTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 14,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 14,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 14,
  },
  statCard: {
    flex: 1,
    minWidth: '45%',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 12,
  },
  teamsList: {
    gap: 10,
  },
  teamCard: {
    marginBottom: 0,
  },
  teamRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  teamLogo: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 14,
  },
  teamLogoImage: {
    width: 36,
    height: 36,
  },
  teamInfo: {
    flex: 1,
  },
  removeButton: {
    padding: 10,
  },
  emptyTeams: {
    alignItems: 'center',
    gap: 14,
    paddingVertical: 20,
  },
  emptyText: {
    textAlign: 'center',
    lineHeight: 22,
  },
  actionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 18,
    gap: 14,
  },
  actionText: {
    flex: 1,
  },
  divider: {
    height: 1,
  },
  // ==========================================
  // RESPONSIVE STYLES FOR TABLETS AND DESKTOP
  // ==========================================
});

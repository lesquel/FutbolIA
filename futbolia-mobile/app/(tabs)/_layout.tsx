/**
 * FutbolIA - Tab Navigation Layout
 * Main navigation with Home, Predict, History, and Settings tabs
 */
import React from 'react';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { Link, Tabs } from 'expo-router';
import { Pressable, View } from 'react-native';
import { useTranslation } from 'react-i18next';

import { useTheme } from '@/src/theme';

function TabBarIcon(props: {
  name: React.ComponentProps<typeof FontAwesome>['name'];
  color: string;
}) {
  return <FontAwesome size={24} style={{ marginBottom: -3 }} {...props} />;
}

export default function TabLayout() {
  const { theme, isDark } = useTheme();
  const { t } = useTranslation();

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: theme.colors.tabBarActive,
        tabBarInactiveTintColor: theme.colors.tabBarInactive,
        tabBarStyle: {
          backgroundColor: theme.colors.tabBar,
          borderTopColor: theme.colors.border,
          paddingBottom: 8,
          paddingTop: 8,
          height: 65,
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '600',
        },
        headerStyle: {
          backgroundColor: theme.colors.surface,
        },
        headerTintColor: theme.colors.text,
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      }}>
      
      {/* Home Tab */}
      <Tabs.Screen
        name="index"
        options={{
          title: t('navigation.home'),
          tabBarIcon: ({ color }) => <TabBarIcon name="home" color={color} />,
          headerTitle: 'FutbolIA 🏆',
          headerRight: () => (
            <Link href="/modal" asChild>
              <Pressable>
                {({ pressed }) => (
                  <FontAwesome
                    name="info-circle"
                    size={22}
                    color={theme.colors.text}
                    style={{ marginRight: 15, opacity: pressed ? 0.5 : 1 }}
                  />
                )}
              </Pressable>
            </Link>
          ),
        }}
      />
      
      {/* Predict Tab */}
      <Tabs.Screen
        name="predict"
        options={{
          title: t('navigation.predict'),
          tabBarIcon: ({ color }) => <TabBarIcon name="magic" color={color} />,
          headerTitle: '🔮 Predecir',
        }}
      />
      
      {/* History Tab */}
      <Tabs.Screen
        name="history"
        options={{
          title: t('navigation.history'),
          tabBarIcon: ({ color }) => <TabBarIcon name="history" color={color} />,
          headerTitle: '📊 Historial',
        }}
      />
      
      {/* Settings Tab */}
      <Tabs.Screen
        name="settings"
        options={{
          title: t('navigation.settings'),
          tabBarIcon: ({ color }) => <TabBarIcon name="cog" color={color} />,
          headerTitle: '⚙️ Ajustes',
        }}
      />
      
      {/* Hide the old "two" tab */}
      <Tabs.Screen
        name="two"
        options={{
          href: null, // Hide from tab bar
        }}
      />
    </Tabs>
  );
}

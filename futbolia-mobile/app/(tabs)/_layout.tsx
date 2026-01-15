/**
 * FutbolIA - Tab Navigation Layout
 * Main navigation with Home, Predict, History, and Settings tabs
 */
import React from "react";
import FontAwesome from "@expo/vector-icons/FontAwesome";
import { Link, Tabs } from "expo-router";
import { Pressable, Image, View, Platform, Dimensions } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useTranslation } from "react-i18next";

import { useTheme } from "@/src/theme";
import { ThemedText, Icon } from "@/src/components/ui";
import { Sparkles, BarChart3, Settings, ClipboardList, Database } from "lucide-react-native";

const HomeHeaderTitle = () => {
  const { width } = Dimensions.get("window");
  const isSmallScreen = width < 360;
  
  return (
    <View style={{ flexDirection: "row", alignItems: "center", gap: 8, flex: 1, maxWidth: "85%" }}>
      <Image
        source={require("../../assets/images/logo.png")}
        style={{ width: isSmallScreen ? 24 : 32, height: isSmallScreen ? 24 : 32 }}
        resizeMode="contain"
      />
      <ThemedText 
        size={isSmallScreen ? "lg" : "xl"} 
        weight="bold"
        numberOfLines={1}
        ellipsizeMode="tail"
        style={{ flexShrink: 1 }}
      >
        GoalMind: El Oráculo del Fútbol
      </ThemedText>
    </View>
  );
};

const HomeHeaderRight = () => {
  const { theme } = useTheme();
  return (
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
  );
};

const TabIcon = ({
  name,
  color,
}: {
  name: React.ComponentProps<typeof FontAwesome>["name"];
  color: string;
}) => <TabBarIcon name={name} color={color} />;

function TabBarIcon(
  props: Readonly<{
    name: React.ComponentProps<typeof FontAwesome>["name"];
    color: string;
  }>
) {
  return <FontAwesome size={24} style={{ marginBottom: -3 }} {...props} />;
}

export default function TabLayout() {
  const { theme } = useTheme();
  const { t } = useTranslation();
  const insets = useSafeAreaInsets();

  // Calcular padding más robusto para Android
  // En Android, los botones del sistema suelen tener ~16-24px de altura
  const bottomPadding = Platform.OS === "android" 
    ? Math.max(insets.bottom || 0, 24) // Mínimo 24px en Android para botones del sistema
    : Math.max(insets.bottom || 0, 8);

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: theme.colors.tabBarActive,
        tabBarInactiveTintColor: theme.colors.tabBarInactive,
        tabBarStyle: {
          backgroundColor: theme.colors.tabBar,
          borderTopColor: theme.colors.border,
          paddingBottom: bottomPadding,
          paddingTop: 8,
          height: 65 + bottomPadding,
          ...(Platform.OS === "android" && {
            elevation: 8, // Sombra en Android
            marginBottom: 0,
          }),
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: "600",
        },
        headerStyle: {
          backgroundColor: theme.colors.surface,
          // Note: paddingTop is not supported in headerStyle, using SafeAreaProvider instead
        },
        headerTintColor: theme.colors.text,
        headerTitleStyle: {
          fontWeight: "bold",
        },
      }}
    >
      {/* Home Tab */}
      <Tabs.Screen
        name="index"
        options={{
          title: t("navigation.home"),
          tabBarIcon: ({ color }) => <TabIcon name="home" color={color} />,
          headerTitle: () => <HomeHeaderTitle />,
          headerRight: () => <HomeHeaderRight />,
        }}
      />

      {/* Predict Tab */}
      <Tabs.Screen
        name="predict"
        options={{
          title: t("navigation.predict"),
          tabBarIcon: ({ color }) => <TabIcon name="magic" color={color} />,
          headerTitle: () => (
            <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
              <Icon icon={Sparkles} size={20} variant="primary" />
              <ThemedText size="lg" weight="bold">Predecir</ThemedText>
            </View>
          ),
        }}
      />

      {/* History Tab */}
      <Tabs.Screen
        name="history"
        options={{
          title: t("navigation.history"),
          tabBarIcon: ({ color }) => <TabIcon name="history" color={color} />,
          headerTitle: () => (
            <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
              <Icon icon={ClipboardList} size={20} variant="primary" />
              <ThemedText size="lg" weight="bold">Historial</ThemedText>
            </View>
          ),
        }}
      />

      {/* Clustering Tab */}
      <Tabs.Screen
        name="clustering"
        options={{
          title: "Clustering",
          tabBarIcon: ({ color }) => <TabIcon name="bar-chart" color={color} />,
          headerTitle: () => (
            <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
              <Icon icon={Database} size={20} variant="primary" />
              <ThemedText size="lg" weight="bold">Minería de Datos</ThemedText>
            </View>
          ),
        }}
      />

      {/* Settings Tab */}
      <Tabs.Screen
        name="settings"
        options={{
          title: t("navigation.settings"),
          tabBarIcon: ({ color }) => <TabIcon name="cog" color={color} />,
          headerTitle: () => (
            <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
              <Icon icon={Settings} size={20} variant="primary" />
              <ThemedText size="lg" weight="bold">Ajustes</ThemedText>
            </View>
          ),
        }}
      />
    </Tabs>
  );
}

/**
 * GoalMindChat - The AI assistant chat component
 */
import { useState, useRef, useEffect, memo } from "react";
import {
  View,
  ScrollView,
  StyleSheet,
  Animated,
  ActivityIndicator,
  Image,
  useWindowDimensions,
} from "react-native";
import { Sparkles, Trophy } from "lucide-react-native";
import { useTheme } from "@/src/theme";
import { useTranslation } from "@/src/i18n/i18n";
import { ThemedText, Card, Icon } from "@/src/components/ui";

interface GoalMindChatProps {
  message?: string;
  isLoading?: boolean;
  showGreeting?: boolean;
  compact?: boolean; // Modo compacto para pantallas pequeñas
}

export const GoalMindChat = memo(function GoalMindChat({
  message,
  isLoading = false,
  showGreeting = true,
  compact = false,
}: GoalMindChatProps) {
  const { theme, isDark } = useTheme();
  const { t } = useTranslation();

  // Responsive breakpoints
  const { width: screenWidth } = useWindowDimensions();
  const isTablet = screenWidth >= 768;
  const isDesktop = screenWidth >= 1024;
  const isLargeScreen = isTablet || isDesktop;

  // Typing animation
  const [displayedText, setDisplayedText] = useState("");
  const fadeAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Fade in animation
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 500,
      useNativeDriver: false, // false for web compatibility
    }).start();
  }, []);

  // Typing effect for messages
  useEffect(() => {
    if (message && !isLoading) {
      setDisplayedText("");
      let index = 0;
      const interval = setInterval(() => {
        if (index < message.length) {
          setDisplayedText(message.slice(0, index + 1));
          index++;
        } else {
          clearInterval(interval);
        }
      }, 20); // Speed of typing

      return () => clearInterval(interval);
    }
  }, [message, isLoading]);

  const greeting = t("dixie.greeting");

  // Modo compacto: una sola línea horizontal
  if (compact) {
    return (
      <Animated.View style={[styles.compactContainer, { opacity: fadeAnim }]}>
        <View
          style={[
            styles.compactCard,
            isLargeScreen && styles.compactCardLarge,
            {
              backgroundColor: theme.colors.surface,
              borderColor: theme.colors.border,
            },
          ]}
        >
          <Image
            source={require("../../../assets/images/GoalMind.png")}
            style={[
              styles.compactAvatar,
              isLargeScreen && styles.compactAvatarLarge,
              { borderColor: theme.colors.primary },
            ]}
          />
          <View style={styles.compactInfo}>
            <ThemedText weight="semibold" size={isLargeScreen ? "base" : "sm"}>
              GoalMind
            </ThemedText>
            <ThemedText
              variant="muted"
              size={isLargeScreen ? "sm" : "xs"}
              numberOfLines={1}
            >
              {isLoading ? t("dixie.analyzing") : message || greeting}
            </ThemedText>
          </View>
          <View
            style={[
              styles.compactOnline,
              isLargeScreen && styles.compactOnlineLarge,
              { backgroundColor: theme.colors.success },
            ]}
          />
        </View>
      </Animated.View>
    );
  }

  return (
    <Animated.View
      style={[
        styles.container,
        isLargeScreen && styles.containerLarge,
        { opacity: fadeAnim },
      ]}
    >
      <Card variant="outlined" padding="md">
        {/* GoalMind Avatar */}
        <View style={[styles.header, isLargeScreen && styles.headerLarge]}>
          <Image
            source={require("../../../assets/images/GoalMind.png")}
            style={[
              styles.avatar,
              isLargeScreen && styles.avatarLarge,
              {
                backgroundColor: isDark
                  ? theme.colors.primary + "20"
                  : theme.colors.primaryLight + "30",
                borderColor: theme.colors.primary,
              },
            ]}
          />

          <View style={styles.headerInfo}>
            <ThemedText
              weight="bold"
              size={isLargeScreen ? "xl" : "lg"}
              numberOfLines={1}
            >
              GoalMind
            </ThemedText>
            <ThemedText
              variant="primary"
              size={isLargeScreen ? "sm" : "xs"}
              numberOfLines={1}
            >
              Analista Deportivo IA
            </ThemedText>
          </View>

          {/* Online indicator */}
          <View style={styles.onlineIndicator}>
            <View
              style={[
                styles.onlineDot,
                isLargeScreen && styles.onlineDotLarge,
                { backgroundColor: theme.colors.success },
              ]}
            />
            <ThemedText variant="muted" size={isLargeScreen ? "sm" : "xs"}>
              Online
            </ThemedText>
          </View>
        </View>

        {/* Chat Bubble */}
        <View
          style={[
            styles.chatBubble,
            isLargeScreen && styles.chatBubbleLarge,
            {
              backgroundColor: isDark
                ? theme.colors.surfaceSecondary
                : theme.colors.surfaceSecondary,
            },
          ]}
        >
          {isLoading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator
                color={theme.colors.primary}
                size={isLargeScreen ? "large" : "small"}
              />
              <ThemedText
                variant="muted"
                size={isLargeScreen ? "base" : "sm"}
                style={styles.loadingText}
              >
                {t("dixie.analyzing")}
              </ThemedText>
            </View>
          ) : (
            <View style={styles.chatContent}>
              {showGreeting && !message && (
                <View style={styles.greetingIcon}>
                  <Icon
                    icon={Trophy}
                    size={isLargeScreen ? 20 : 16}
                    variant="primary"
                  />
                </View>
              )}
              <ThemedText
                variant="secondary"
                size={isLargeScreen ? "base" : "sm"}
                style={[styles.chatText, isLargeScreen && styles.chatTextLarge]}
                numberOfLines={undefined}
              >
                {message
                  ? displayedText
                  : showGreeting
                    ? greeting
                    : t("dixie.ready")}
                {message && displayedText.length < message.length && (
                  <ThemedText variant="primary">▋</ThemedText>
                )}
              </ThemedText>
            </View>
          )}
        </View>
      </Card>
    </Animated.View>
  );
});

const styles = StyleSheet.create({
  container: {
    marginBottom: 6,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    borderWidth: 2,
    alignItems: "center",
    justifyContent: "center",
  },
  headerInfo: {
    flex: 1,
    marginLeft: 12,
  },
  onlineIndicator: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
  },
  onlineDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  chatBubble: {
    borderRadius: 12,
    borderTopLeftRadius: 4,
    padding: 12,
    minHeight: 48,
  },
  chatContent: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 8,
  },
  greetingIcon: {
    marginTop: 3,
  },
  chatText: {
    lineHeight: 20,
    flex: 1,
  },
  loadingContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  loadingText: {
    fontStyle: "italic",
  },
  // Estilos compactos
  compactContainer: {
    marginBottom: 6,
  },
  compactCard: {
    flexDirection: "row",
    alignItems: "center",
    borderRadius: 10,
    borderWidth: 1,
    padding: 8,
    gap: 8,
  },
  compactAvatar: {
    width: 36,
    height: 36,
    borderRadius: 18,
    borderWidth: 1.5,
  },
  compactInfo: {
    flex: 1,
  },
  compactOnline: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  // ==========================================
  // RESPONSIVE STYLES FOR TABLETS AND DESKTOP
  // ==========================================
  containerLarge: {
    marginBottom: 24,
  },
  headerLarge: {
    marginBottom: 18,
  },
  avatarLarge: {
    width: 64,
    height: 64,
    borderRadius: 32,
    borderWidth: 3,
  },
  onlineDotLarge: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  chatBubbleLarge: {
    borderRadius: 22,
    borderTopLeftRadius: 8,
    padding: 24,
    minHeight: 80,
  },
  chatTextLarge: {
    lineHeight: 28,
  },
  compactCardLarge: {
    borderRadius: 16,
    padding: 16,
    gap: 14,
  },
  compactAvatarLarge: {
    width: 48,
    height: 48,
    borderRadius: 24,
    borderWidth: 2,
  },
  compactOnlineLarge: {
    width: 14,
    height: 14,
    borderRadius: 7,
  },
});

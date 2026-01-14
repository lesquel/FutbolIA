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
} from "react-native";
import { Sparkles, Trophy } from "lucide-react-native";
import { useTheme } from "@/src/theme";
import { useTranslation } from "@/src/i18n/i18n";
import { ThemedText, Card, Icon } from "@/src/components/ui";

interface GoalMindChatProps {
  message?: string;
  isLoading?: boolean;
  showGreeting?: boolean;
}

export const GoalMindChat = memo(function GoalMindChat({
  message,
  isLoading = false,
  showGreeting = true,
}: GoalMindChatProps) {
  const { theme, isDark } = useTheme();
  const { t } = useTranslation();

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

  return (
    <Animated.View style={[styles.container, { opacity: fadeAnim }]}>
      <Card variant="outlined" padding="md">
        {/* GoalMind Avatar */}
        <View style={styles.header}>
          <Image
            source={require("@/assets/images/GoalMind.png")}
            style={[
              styles.avatar,
              {
                backgroundColor: isDark
                  ? theme.colors.primary + "20"
                  : theme.colors.primaryLight + "30",
                borderColor: theme.colors.primary,
              },
            ]}
          />

          <View style={styles.headerInfo}>
            <ThemedText weight="bold" size="lg">
              GoalMind
            </ThemedText>
            <ThemedText variant="primary" size="xs">
              Analista Deportivo IA
            </ThemedText>
          </View>

          {/* Online indicator */}
          <View style={styles.onlineIndicator}>
            <View
              style={[
                styles.onlineDot,
                { backgroundColor: theme.colors.success },
              ]}
            />
            <ThemedText variant="muted" size="xs">
              Online
            </ThemedText>
          </View>
        </View>

        {/* Chat Bubble */}
        <View
          style={[
            styles.chatBubble,
            {
              backgroundColor: isDark
                ? theme.colors.surfaceSecondary
                : theme.colors.surfaceSecondary,
            },
          ]}
        >
          {isLoading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator color={theme.colors.primary} size="small" />
              <ThemedText variant="muted" size="sm" style={styles.loadingText}>
                {t("dixie.analyzing")}
              </ThemedText>
            </View>
          ) : (
            <View style={styles.chatContent}>
              {showGreeting && !message && (
                <View style={styles.greetingIcon}>
                  <Icon icon={Trophy} size={16} variant="primary" />
                </View>
              )}
              <ThemedText variant="secondary" size="sm" style={styles.chatText}>
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
    marginBottom: 16,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 12,
  },
  avatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
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
    borderRadius: 16,
    borderTopLeftRadius: 4,
    padding: 16,
    minHeight: 60,
  },
  chatContent: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 8,
  },
  greetingIcon: {
    marginTop: 2,
  },
  chatText: {
    lineHeight: 22,
    flex: 1,
  },
  loadingContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  loadingText: {
    fontStyle: "italic",
  },
});

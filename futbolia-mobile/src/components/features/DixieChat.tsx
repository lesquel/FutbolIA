/**
 * DixieChat - The AI assistant chat component
 */
import { useState, useRef, useEffect } from 'react';
import { 
  View, 
  ScrollView, 
  StyleSheet, 
  Animated,
  ActivityIndicator,
} from 'react-native';
import { useTheme } from '@/src/theme';
import { useTranslation } from '@/src/i18n/i18n';
import { ThemedText, Card } from '@/src/components/ui';

interface DixieChatProps {
  message?: string;
  isLoading?: boolean;
  showGreeting?: boolean;
}

export function DixieChat({ 
  message, 
  isLoading = false,
  showGreeting = true,
}: DixieChatProps) {
  const { theme, isDark } = useTheme();
  const { t } = useTranslation();
  
  // Typing animation
  const [displayedText, setDisplayedText] = useState('');
  const fadeAnim = useRef(new Animated.Value(0)).current;
  
  useEffect(() => {
    // Fade in animation
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 500,
      useNativeDriver: true,
    }).start();
  }, []);
  
  // Typing effect for messages
  useEffect(() => {
    if (message && !isLoading) {
      setDisplayedText('');
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
  
  const greeting = t('dixie.greeting');
  
  return (
    <Animated.View style={[styles.container, { opacity: fadeAnim }]}>
      <Card variant="outlined" padding="md">
        {/* Dixie Avatar */}
        <View style={styles.header}>
          <View 
            style={[
              styles.avatar,
              { 
                backgroundColor: isDark 
                  ? theme.colors.primary + '20'
                  : theme.colors.primaryLight + '30',
                borderColor: theme.colors.primary,
              },
            ]}
          >
            <ThemedText size="2xl">🔮</ThemedText>
          </View>
          
          <View style={styles.headerInfo}>
            <ThemedText weight="bold" size="lg">Dixie</ThemedText>
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
            <ThemedText variant="muted" size="xs">Online</ThemedText>
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
                {t('dixie.analyzing')}
              </ThemedText>
            </View>
          ) : (
            <ThemedText 
              variant="secondary" 
              size="sm"
              style={styles.chatText}
            >
              {message ? displayedText : (showGreeting ? greeting : t('dixie.ready'))}
              {message && displayedText.length < message.length && (
                <ThemedText variant="primary">▋</ThemedText>
              )}
            </ThemedText>
          )}
        </View>
      </Card>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  avatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    borderWidth: 2,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerInfo: {
    flex: 1,
    marginLeft: 12,
  },
  onlineIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
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
  chatText: {
    lineHeight: 22,
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  loadingText: {
    fontStyle: 'italic',
  },
});

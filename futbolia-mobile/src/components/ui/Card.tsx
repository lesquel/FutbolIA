/**
 * Card - Themed card component for content containers
 */
import {
  View,
  ViewProps,
  StyleSheet,
  Platform,
  useWindowDimensions,
} from "react-native";
import { useTheme } from "@/src/theme";

interface CardProps extends ViewProps {
  variant?: "default" | "elevated" | "outlined";
  padding?: "none" | "sm" | "md" | "lg";
}

export function Card({
  variant = "default",
  padding = "md",
  style,
  children,
  ...props
}: CardProps) {
  const { theme, isDark } = useTheme();
  const { width: screenWidth } = useWindowDimensions();
  const isLargeScreen = screenWidth >= 768;

  const getPadding = () => {
    // Responsive padding - smaller on mobile
    switch (padding) {
      case "none":
        return 0;
      case "sm":
        return isLargeScreen ? 12 : 8;
      case "md":
        return isLargeScreen ? 16 : 12;
      case "lg":
        return isLargeScreen ? 24 : 14;
    }
  };

  const getVariantStyles = () => {
    switch (variant) {
      case "elevated":
        // Use boxShadow for web, shadow* props for native
        const shadowStyle = Platform.select({
          web: {
            boxShadow: isDark
              ? "0 4px 12px rgba(0, 0, 0, 0.3)"
              : "0 4px 12px rgba(0, 0, 0, 0.1)",
          },
          default: {
            shadowColor: "#000",
            shadowOffset: { width: 0, height: 4 },
            shadowOpacity: isDark ? 0.3 : 0.1,
            shadowRadius: 12,
            elevation: 8,
          },
        });
        return shadowStyle || {};
      case "outlined":
        return {
          borderWidth: 1,
          borderColor: theme.colors.border,
        };
      default:
        return {
          borderWidth: 1,
          borderColor: theme.colors.borderLight,
        };
    }
  };

  return (
    <View
      style={[
        {
          backgroundColor: theme.colors.card,
          borderRadius: isLargeScreen ? 16 : 12,
          padding: getPadding(),
          ...getVariantStyles(),
        },
        style,
      ]}
      {...props}
    >
      {children}
    </View>
  );
}

/**
 * Card - Themed card component for content containers
 */
import { View, ViewProps, StyleSheet, Platform } from "react-native";
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

  const getPadding = () => {
    switch (padding) {
      case "none":
        return 0;
      case "sm":
        return 12;
      case "md":
        return 16;
      case "lg":
        return 24;
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
          borderRadius: 16,
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

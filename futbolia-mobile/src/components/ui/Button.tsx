/**
 * Button - Themed button component with variants
 */
import {
  TouchableOpacity,
  TouchableOpacityProps,
  ActivityIndicator,
  View,
} from "react-native";
import { useTheme } from "@/src/theme";
import { ThemedText } from "./ThemedText";

interface ButtonProps extends TouchableOpacityProps {
  title: string;
  variant?: "primary" | "secondary" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: "left" | "right";
  fullWidth?: boolean;
}

export function Button({
  title,
  variant = "primary",
  size = "md",
  loading = false,
  icon,
  iconPosition = "left",
  fullWidth = false,
  disabled,
  style,
  ...props
}: ButtonProps) {
  const { theme, isDark } = useTheme();

  const getBackgroundColor = () => {
    if (disabled) return theme.colors.textMuted;
    switch (variant) {
      case "primary":
        return theme.colors.primary;
      case "secondary":
        return theme.colors.secondary;
      case "outline":
      case "ghost":
        return "transparent";
      default:
        return theme.colors.primary;
    }
  };

  const getTextColor = () => {
    if (disabled) return "#fff";
    switch (variant) {
      case "primary":
        return isDark ? "#000" : "#fff";
      case "secondary":
        return "#fff";
      case "outline":
        return theme.colors.primary;
      case "ghost":
        return theme.colors.text;
      default:
        return "#fff";
    }
  };

  const getPadding = () => {
    switch (size) {
      case "sm":
        return { paddingVertical: 8, paddingHorizontal: 16 };
      case "md":
        return { paddingVertical: 12, paddingHorizontal: 24 };
      case "lg":
        return { paddingVertical: 16, paddingHorizontal: 32 };
    }
  };

  const getFontSize = () => {
    switch (size) {
      case "sm":
        return 14;
      case "md":
        return 16;
      case "lg":
        return 18;
    }
  };

  const borderStyle =
    variant === "outline"
      ? {
          borderWidth: 2,
          borderColor: theme.colors.primary,
        }
      : {};

  return (
    <TouchableOpacity
      disabled={disabled || loading}
      style={[
        {
          backgroundColor: getBackgroundColor(),
          borderRadius: 12,
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "center",
          gap: 8,
          width: fullWidth ? "100%" : undefined,
          opacity: disabled ? 0.6 : 1,
          ...getPadding(),
          ...borderStyle,
        },
        style,
      ]}
      {...props}
    >
      {loading ? (
        <ActivityIndicator color={getTextColor()} size="small" />
      ) : (
        <>
          {icon && iconPosition === "left" && icon}
          <ThemedText
            style={{
              color: getTextColor(),
              fontSize: getFontSize(),
              fontWeight: "600",
            }}
          >
            {title}
          </ThemedText>
          {icon && iconPosition === "right" && icon}
        </>
      )}
    </TouchableOpacity>
  );
}

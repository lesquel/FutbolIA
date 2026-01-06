/**
 * Icon Component - Wrapper for lucide-react-native icons
 * Provides consistent icon usage throughout the app
 */
import { LucideIcon } from "lucide-react-native";
import { useTheme } from "@/src/theme";

interface IconProps {
  icon: LucideIcon;
  size?: number;
  color?: string;
  variant?: "primary" | "secondary" | "muted" | "error" | "success" | "warning";
}

export function Icon({ icon: IconComponent, size = 24, color, variant }: IconProps) {
  const { theme } = useTheme();
  
  let iconColor = color;
  if (!iconColor && variant) {
    switch (variant) {
      case "primary":
        iconColor = theme.colors.primary;
        break;
      case "secondary":
        iconColor = theme.colors.textSecondary;
        break;
      case "muted":
        iconColor = theme.colors.textMuted;
        break;
      case "error":
        iconColor = theme.colors.error;
        break;
      case "success":
        iconColor = theme.colors.success;
        break;
      case "warning":
        iconColor = theme.colors.warning;
        break;
      default:
        iconColor = theme.colors.text;
    }
  }
  
  if (!iconColor) {
    iconColor = theme.colors.text;
  }
  
  return <IconComponent size={size} color={iconColor} />;
}


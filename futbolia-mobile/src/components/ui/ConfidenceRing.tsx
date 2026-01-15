/**
 * ConfidenceRing - Circular progress indicator for prediction confidence
 */
import { View, StyleSheet } from "react-native";
import Svg, { Circle, G } from "react-native-svg";
import { useTheme } from "@/src/theme";
import { ThemedText } from "./ThemedText";

interface ConfidenceRingProps {
  percentage: number;
  size?: number;
  strokeWidth?: number;
  label?: string;
}

export function ConfidenceRing({
  percentage,
  size = 120,
  strokeWidth = 10,
  label,
}: ConfidenceRingProps) {
  const { theme, isDark } = useTheme();

  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  // Color based on confidence level
  const getColor = () => {
    if (percentage >= 70) return theme.colors.success;
    if (percentage >= 50) return theme.colors.warning;
    return theme.colors.error;
  };

  return (
    <View style={styles.container}>
      <Svg width={size} height={size}>
        <G 
          rotation="-90" 
          origin={`${size / 2},${size / 2}`}
        >
          {/* Background circle */}
          <Circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={theme.colors.border}
            strokeWidth={strokeWidth}
            fill="none"
          />
          {/* Progress circle */}
          <Circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={getColor()}
            strokeWidth={strokeWidth}
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
          />
        </G>
      </Svg>

      {/* Center content */}
      <View style={[styles.center, { width: size, height: size }]}>
        <ThemedText size="2xl" weight="bold" style={{ color: getColor() }}>
          {percentage}%
        </ThemedText>
        {label && (
          <ThemedText variant="muted" size="xs">
            {label}
          </ThemedText>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: "relative",
    alignItems: "center",
    justifyContent: "center",
  },
  center: {
    position: "absolute",
    alignItems: "center",
    justifyContent: "center",
  },
});

/**
 * TeamBadge - Display team information with logo/icon
 * Fixed: Removed text nodes from View components (React Native Web compatibility)
 */
import React from "react";
import { View, Image, StyleSheet } from "react-native";
import { useTheme } from "@/src/theme";
import { ThemedText } from "./ThemedText";

interface TeamBadgeProps {
  name: string;
  logoUrl?: string;
  form?: string;
  size?: "sm" | "md" | "lg";
  showForm?: boolean;
}

export function TeamBadge({
  name,
  logoUrl,
  form,
  size = "md",
  showForm = false,
}: TeamBadgeProps) {
  const { theme } = useTheme();

  const getSizes = () => {
    switch (size) {
      case "sm":
        return { logo: 40, font: "sm" as const };
      case "md":
        return { logo: 60, font: "base" as const };
      case "lg":
        return { logo: 80, font: "lg" as const };
    }
  };

  const sizes = getSizes();

  // Get initials if no logo - ensure it's always a valid string
  const getInitials = (): string => {
    if (!name || typeof name !== "string") return "?";
    return name
      .split(" ")
      .filter(Boolean)
      .map((w) => w[0]?.toUpperCase() || "")
      .join("")
      .slice(0, 3) || "?";
  };

  // Form indicator colors
  const getFormColor = (result: string) => {
    switch (result) {
      case "W":
        return theme.colors.success;
      case "D":
        return theme.colors.warning;
      case "L":
        return theme.colors.error;
      default:
        return theme.colors.textMuted;
    }
  };

  // Parse form string safely
  const formResults = form ? form.split("").filter((r) => r.trim()) : [];

  return (
    <View style={styles.container}>
      <View
        style={[
          styles.logoContainer,
          {
            width: sizes.logo,
            height: sizes.logo,
            backgroundColor: theme.colors.surfaceSecondary,
            borderColor: theme.colors.border,
          },
        ]}
      >
        {logoUrl ? (
          <Image
            source={{ uri: logoUrl }}
            style={{ width: sizes.logo - 10, height: sizes.logo - 10 }}
            resizeMode="contain"
          />
        ) : (
          <ThemedText weight="bold" style={{ fontSize: sizes.logo / 3 }}>
            {getInitials()}
          </ThemedText>
        )}
      </View>
      <ThemedText
        size={sizes.font}
        weight="semibold"
        style={styles.name}
        numberOfLines={2}
      >
        {name || "Unknown Team"}
      </ThemedText>
      {showForm && formResults.length > 0 && (
        <View style={styles.formContainer}>
          {formResults.map((result, index) => (
            <View
              key={index}
              style={[
                styles.formDot,
                { backgroundColor: getFormColor(result) },
              ]}
            />
          ))}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
  },
  logoContainer: {
    borderRadius: 50,
    borderWidth: 2,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 8,
  },
  name: {
    textAlign: "center",
    maxWidth: 100,
  },
  formContainer: {
    flexDirection: "row",
    gap: 4,
    marginTop: 8,
  },
  formDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
});

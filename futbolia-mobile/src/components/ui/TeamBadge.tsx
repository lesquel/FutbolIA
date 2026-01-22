/**
 * TeamBadge - Display team information with logo/icon
 * Fixed: Added proper image loading states and error handling
 */
import React, { useState, useCallback, memo } from "react";
import { View, Image, StyleSheet, ActivityIndicator } from "react-native";
import { useTheme } from "@/src/theme";
import { ThemedText } from "./ThemedText";

interface TeamBadgeProps {
  name: string;
  logoUrl?: string;
  form?: string;
  size?: "sm" | "md" | "lg" | "xl";
  showForm?: boolean;
}

export const TeamBadge = memo(function TeamBadge({
  name,
  logoUrl,
  form,
  size = "md",
  showForm = false,
}: TeamBadgeProps) {
  const { theme } = useTheme();
  const [imageLoading, setImageLoading] = useState(true);
  const [imageError, setImageError] = useState(false);

  const getSizes = () => {
    switch (size) {
      case "sm":
        return { logo: 36, font: "xs" as const, maxWidth: 80 };
      case "md":
        return { logo: 50, font: "sm" as const, maxWidth: 100 };
      case "lg":
        return { logo: 70, font: "base" as const, maxWidth: 120 };
      case "xl":
        return { logo: 100, font: "xl" as const, maxWidth: 160 };
    }
  };

  const sizes = getSizes();

  // Get initials if no logo - ensure it's always a valid string
  const getInitials = useCallback((): string => {
    if (!name || typeof name !== "string") return "?";
    return (
      name
        .split(" ")
        .filter(Boolean)
        .map((w) => w[0]?.toUpperCase() || "")
        .join("")
        .slice(0, 3) || "?"
    );
  }, [name]);

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

  // Validate logo URL
  const hasValidLogo = logoUrl && logoUrl.startsWith("http") && !imageError;

  const handleImageLoad = useCallback(() => {
    setImageLoading(false);
    setImageError(false);
  }, []);

  const handleImageError = useCallback(() => {
    setImageLoading(false);
    setImageError(true);
  }, []);

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
        {hasValidLogo ? (
          <>
            {imageLoading && (
              <ActivityIndicator
                size="small"
                color={theme.colors.primary}
                style={StyleSheet.absoluteFill}
              />
            )}
            <Image
              source={{ uri: logoUrl, cache: "force-cache" }}
              style={[
                { width: sizes.logo - 10, height: sizes.logo - 10 },
                imageLoading && { opacity: 0 },
              ]}
              resizeMode="contain"
              onLoad={handleImageLoad}
              onError={handleImageError}
            />
          </>
        ) : (
          <ThemedText weight="bold" style={{ fontSize: sizes.logo / 3 }}>
            {getInitials()}
          </ThemedText>
        )}
      </View>
      <ThemedText
        size={sizes.font}
        weight="semibold"
        style={[styles.name, { maxWidth: sizes.maxWidth }]}
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
});

const styles = StyleSheet.create({
  container: {
    alignItems: "center",
    paddingHorizontal: 4,
  },
  logoContainer: {
    borderRadius: 50,
    borderWidth: 2,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 10,
  },
  name: {
    textAlign: "center",
    lineHeight: 18,
  },
  formContainer: {
    flexDirection: "row",
    gap: 5,
    marginTop: 10,
  },
  formDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
});

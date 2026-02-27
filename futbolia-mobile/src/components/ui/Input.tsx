/**
 * Input - Themed text input component
 */
import { TextInput, TextInputProps, View, StyleSheet } from "react-native";
import { useTheme } from "@/src/theme";
import { ThemedText } from "./ThemedText";
import { useState } from "react";

interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
  iconPosition?: "left" | "right";
}

export function Input({
  label,
  error,
  icon,
  iconPosition = "left",
  style,
  ...props
}: InputProps) {
  const { theme, isDark } = useTheme();
  const [isFocused, setIsFocused] = useState(false);

  const borderColor = error
    ? theme.colors.error
    : isFocused
      ? theme.colors.primary
      : theme.colors.border;

  return (
    <View style={styles.container}>
      {label && (
        <ThemedText variant="secondary" size="sm" style={styles.label}>
          {label}
        </ThemedText>
      )}

      <View
        style={[
          styles.inputContainer,
          {
            backgroundColor: theme.colors.surface,
            borderColor,
            borderWidth: isFocused ? 2 : 1,
          },
        ]}
      >
        {icon && iconPosition === "left" && (
          <View style={styles.icon}>{icon}</View>
        )}

        <TextInput
          style={[
            styles.input,
            {
              color: theme.colors.text,
              flex: 1,
            },
            style,
          ]}
          placeholderTextColor={theme.colors.textMuted}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          {...props}
        />

        {icon && iconPosition === "right" && (
          <View style={styles.icon}>{icon}</View>
        )}
      </View>

      {error && (
        <ThemedText variant="error" size="sm" style={styles.error}>
          {error}
        </ThemedText>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginBottom: 18,
  },
  label: {
    marginBottom: 10,
  },
  inputContainer: {
    flexDirection: "row",
    alignItems: "center",
    borderRadius: 14,
    paddingHorizontal: 18,
    minHeight: 54,
  },
  input: {
    paddingVertical: 16,
    fontSize: 16,
  },
  icon: {
    marginRight: 14,
  },
  error: {
    marginTop: 6,
  },
});

/**
 * ThemedText - A Text component that responds to theme changes
 */
import { Text, TextProps, StyleSheet } from 'react-native';
import { useTheme } from '@/src/theme';

interface ThemedTextProps extends TextProps {
  variant?: 'default' | 'secondary' | 'muted' | 'primary' | 'error';
  size?: 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl' | '3xl';
  weight?: 'normal' | 'medium' | 'semibold' | 'bold';
}

export function ThemedText({ 
  variant = 'default', 
  size = 'base',
  weight = 'normal',
  style, 
  ...props 
}: ThemedTextProps) {
  const { theme } = useTheme();
  
  const colors = {
    default: theme.colors.text,
    secondary: theme.colors.textSecondary,
    muted: theme.colors.textMuted,
    primary: theme.colors.primary,
    error: theme.colors.error,
  };
  
  const sizes = {
    xs: 12,
    sm: 14,
    base: 16,
    lg: 18,
    xl: 20,
    '2xl': 24,
    '3xl': 30,
  };
  
  const weights = {
    normal: '400' as const,
    medium: '500' as const,
    semibold: '600' as const,
    bold: '700' as const,
  };
  
  return (
    <Text
      style={[
        { 
          color: colors[variant],
          fontSize: sizes[size],
          fontWeight: weights[weight],
        },
        style,
      ]}
      {...props}
    />
  );
}

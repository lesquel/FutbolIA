/**
 * ThemedView - A View component that responds to theme changes
 */
import { View, ViewProps } from 'react-native';
import { useTheme } from '@/src/theme';

interface ThemedViewProps extends ViewProps {
  variant?: 'background' | 'surface' | 'card';
}

export function ThemedView({ variant = 'background', style, className, ...props }: ThemedViewProps) {
  const { theme } = useTheme();
  
  const backgroundColors = {
    background: theme.colors.background,
    surface: theme.colors.surface,
    card: theme.colors.card,
  };
  
  return (
    <View
      style={[{ backgroundColor: backgroundColors[variant] }, style]}
      className={className}
      {...props}
    />
  );
}

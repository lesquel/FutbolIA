/**
 * Button - Themed button component with variants
 */
import React from 'react';
import { TouchableOpacity, TouchableOpacityProps, ActivityIndicator, View } from 'react-native';
import { useTheme } from '@/src/theme';
import { ThemedText } from './ThemedText';

import { LucideIcon } from 'lucide-react-native';
import { Icon } from './Icon';

interface ButtonProps extends TouchableOpacityProps {
  title: string;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: LucideIcon | React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
}

// Helper to check if it's a Lucide icon component
// Lucide icons are function components, so if it's a function, treat it as Lucide icon
const isLucideIcon = (icon: any): icon is LucideIcon => {
  return icon && typeof icon === 'function';
};

export function Button({
  title,
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  iconPosition = 'left',
  fullWidth = false,
  disabled,
  style,
  ...props
}: ButtonProps) {
  const { theme, isDark } = useTheme();

  const getBackgroundColor = () => {
    if (disabled) return theme.colors.textMuted;
    switch (variant) {
      case 'primary':
        return theme.colors.primary;
      case 'secondary':
        return theme.colors.secondary;
      case 'outline':
      case 'ghost':
        return 'transparent';
      default:
        return theme.colors.primary;
    }
  };

  const getTextColor = () => {
    if (disabled) return '#fff';
    switch (variant) {
      case 'primary':
        return isDark ? '#000' : '#fff';
      case 'secondary':
        return '#fff';
      case 'outline':
        return theme.colors.primary;
      case 'ghost':
        return theme.colors.text;
      default:
        return '#fff';
    }
  };

  const getPadding = () => {
    switch (size) {
      case 'sm':
        return { paddingVertical: 10, paddingHorizontal: 18 };
      case 'md':
        return { paddingVertical: 14, paddingHorizontal: 26 };
      case 'lg':
        return { paddingVertical: 18, paddingHorizontal: 34 };
    }
  };

  const getFontSize = () => {
    switch (size) {
      case 'sm':
        return 14;
      case 'md':
        return 16;
      case 'lg':
        return 18;
    }
  };

  const borderStyle =
    variant === 'outline'
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
          borderRadius: 14,
          flexDirection: 'row',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 10,
          width: fullWidth ? '100%' : undefined,
          opacity: disabled ? 0.6 : 1,
          minHeight: size === 'sm' ? 42 : size === 'md' ? 50 : 58,
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
          {icon &&
            iconPosition === 'left' &&
            (isLucideIcon(icon) ? (
              <Icon icon={icon} size={getFontSize()} color={getTextColor()} />
            ) : React.isValidElement(icon) ? (
              icon
            ) : null)}
          <ThemedText
            style={{
              color: getTextColor(),
              fontSize: getFontSize(),
              fontWeight: '600',
            }}
          >
            {title}
          </ThemedText>
          {icon &&
            iconPosition === 'right' &&
            (isLucideIcon(icon) ? (
              <Icon icon={icon} size={getFontSize()} color={getTextColor()} />
            ) : React.isValidElement(icon) ? (
              icon
            ) : null)}
        </>
      )}
    </TouchableOpacity>
  );
}

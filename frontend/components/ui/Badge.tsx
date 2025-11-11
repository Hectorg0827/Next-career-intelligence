/**
 * NEXT Career Intelligence - Badge Component
 * Super-Premium Design System
 *
 * Flexible badge component for status indicators, labels, counts, and premium features.
 * Supports multiple variants, sizes, and styles.
 */

'use client';

import React from 'react';
import { Crown, Sparkles, Check, AlertCircle, Info, X } from 'lucide-react';

export interface BadgeProps {
  /** Badge content */
  children: React.ReactNode;
  /** Visual variant */
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'error' | 'info' | 'premium' | 'gold';
  /** Badge size */
  size?: 'xs' | 'sm' | 'md' | 'lg';
  /** Badge style */
  style?: 'solid' | 'outline' | 'soft' | 'gradient';
  /** Show icon */
  icon?: React.ReactNode | 'check' | 'crown' | 'sparkles' | 'alert' | 'info';
  /** Make badge rounded/pill-shaped */
  rounded?: boolean;
  /** Show close/remove button */
  onRemove?: () => void;
  /** Custom className */
  className?: string;
  /** Make badge clickable */
  onClick?: () => void;
  /** Dot indicator (for status badges) */
  dot?: boolean;
  /** Pulse animation (for live status) */
  pulse?: boolean;
}

/**
 * Premium Badge Component
 *
 * @example
 * ```tsx
 * <Badge variant="success" icon="check">Active</Badge>
 * <Badge variant="premium" style="gradient" icon="crown">Pro</Badge>
 * <Badge variant="error" dot pulse>Live</Badge>
 * <Badge onRemove={() => handleRemove()}>JavaScript</Badge>
 * ```
 */
export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'md',
  style = 'solid',
  icon,
  rounded = true,
  onRemove,
  className = '',
  onClick,
  dot = false,
  pulse = false,
}) => {
  // Size classes
  const sizeClasses = {
    xs: 'px-2 py-0.5 text-xs',
    sm: 'px-2.5 py-1 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-1.5 text-base',
  };

  const iconSizes = {
    xs: 'w-3 h-3',
    sm: 'w-3.5 h-3.5',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  };

  // Variant + Style combinations
  const variantStyles = {
    solid: {
      default: 'bg-gray-600 text-white',
      primary: 'bg-primary-600 text-white',
      success: 'bg-green-600 text-white',
      warning: 'bg-amber-600 text-white',
      error: 'bg-red-600 text-white',
      info: 'bg-blue-600 text-white',
      premium: 'bg-gradient-to-r from-primary-600 to-primary-500 text-white shadow-lg shadow-primary-500/30',
      gold: 'bg-gradient-to-r from-amber-500 to-yellow-500 text-white shadow-lg shadow-amber-500/30',
    },
    outline: {
      default: 'border-2 border-gray-600 text-gray-700 dark:text-gray-300',
      primary: 'border-2 border-primary-600 text-primary-700 dark:text-primary-400',
      success: 'border-2 border-green-600 text-green-700 dark:text-green-400',
      warning: 'border-2 border-amber-600 text-amber-700 dark:text-amber-400',
      error: 'border-2 border-red-600 text-red-700 dark:text-red-400',
      info: 'border-2 border-blue-600 text-blue-700 dark:text-blue-400',
      premium: 'border-2 border-primary-600 text-primary-700 dark:text-primary-400',
      gold: 'border-2 border-amber-500 text-amber-700 dark:text-amber-400',
    },
    soft: {
      default: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
      primary: 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300',
      success: 'bg-green-50 text-green-700 dark:bg-green-900/30 dark:text-green-300',
      warning: 'bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
      error: 'bg-red-50 text-red-700 dark:bg-red-900/30 dark:text-red-300',
      info: 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
      premium: 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300',
      gold: 'bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
    },
    gradient: {
      default: 'bg-gradient-to-r from-gray-600 to-gray-500 text-white',
      primary: 'bg-gradient-to-r from-primary-600 to-primary-500 text-white shadow-lg shadow-primary-500/30',
      success: 'bg-gradient-to-r from-green-600 to-emerald-500 text-white shadow-lg shadow-green-500/30',
      warning: 'bg-gradient-to-r from-amber-600 to-yellow-500 text-white shadow-lg shadow-amber-500/30',
      error: 'bg-gradient-to-r from-red-600 to-rose-500 text-white shadow-lg shadow-red-500/30',
      info: 'bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-lg shadow-blue-500/30',
      premium: 'bg-gradient-to-r from-purple-600 via-primary-600 to-pink-600 text-white shadow-lg shadow-primary-500/40',
      gold: 'bg-gradient-to-r from-yellow-500 via-amber-500 to-orange-500 text-white shadow-lg shadow-amber-500/40',
    },
  };

  // Icon mapping
  const iconMap = {
    check: <Check className={iconSizes[size]} />,
    crown: <Crown className={iconSizes[size]} />,
    sparkles: <Sparkles className={iconSizes[size]} />,
    alert: <AlertCircle className={iconSizes[size]} />,
    info: <Info className={iconSizes[size]} />,
  };

  const renderIcon = () => {
    if (!icon) return null;
    if (typeof icon === 'string' && icon in iconMap) {
      return iconMap[icon as keyof typeof iconMap];
    }
    return icon;
  };

  const baseClasses = `
    inline-flex items-center justify-center gap-1.5
    font-medium
    ${rounded ? 'rounded-full' : 'rounded-md'}
    ${sizeClasses[size]}
    ${variantStyles[style][variant]}
    ${onClick ? 'cursor-pointer hover:opacity-90 transition-opacity duration-200' : ''}
    ${pulse ? 'animate-pulse' : ''}
    ${className}
  `;

  return (
    <span
      className={baseClasses}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      {/* Dot indicator */}
      {dot && (
        <span
          className={`
            w-2 h-2 rounded-full
            ${pulse ? 'animate-pulse' : ''}
            ${variant === 'success' ? 'bg-green-400' : ''}
            ${variant === 'error' ? 'bg-red-400' : ''}
            ${variant === 'warning' ? 'bg-amber-400' : ''}
            ${variant === 'default' ? 'bg-gray-400' : ''}
          `}
        />
      )}

      {/* Icon */}
      {renderIcon()}

      {/* Content */}
      <span>{children}</span>

      {/* Remove button */}
      {onRemove && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className="
            ml-1 -mr-1
            hover:bg-white/20 rounded-full
            transition-colors duration-200
            focus:outline-none focus:ring-2 focus:ring-white/50
          "
          aria-label="Remove"
        >
          <X className={iconSizes[size]} />
        </button>
      )}
    </span>
  );
};

/**
 * Badge Group - Display multiple badges with consistent spacing
 */
export const BadgeGroup: React.FC<{
  children: React.ReactNode;
  className?: string;
  wrap?: boolean;
}> = ({ children, className = '', wrap = true }) => {
  return (
    <div
      className={`
        flex items-center gap-2
        ${wrap ? 'flex-wrap' : ''}
        ${className}
      `}
    >
      {children}
    </div>
  );
};

/**
 * Status Badge - Pre-configured for common statuses
 */
export const StatusBadge: React.FC<{
  status: 'active' | 'inactive' | 'pending' | 'archived' | 'draft';
  size?: BadgeProps['size'];
}> = ({ status, size = 'md' }) => {
  const statusConfig = {
    active: { variant: 'success' as const, icon: 'check' as const, label: 'Active', dot: true },
    inactive: { variant: 'default' as const, label: 'Inactive', dot: true },
    pending: { variant: 'warning' as const, label: 'Pending', dot: true, pulse: true },
    archived: { variant: 'default' as const, label: 'Archived' },
    draft: { variant: 'info' as const, label: 'Draft' },
  };

  const config = statusConfig[status];

  return (
    <Badge
      variant={config.variant}
      size={size}
      icon={config.icon}
      dot={config.dot}
      pulse={config.pulse}
    >
      {config.label}
    </Badge>
  );
};

/**
 * Premium Badge - Pre-configured for premium features
 */
export const PremiumBadge: React.FC<{
  tier?: 'pro' | 'premium' | 'enterprise';
  size?: BadgeProps['size'];
  style?: BadgeProps['style'];
}> = ({ tier = 'premium', size = 'sm', style = 'gradient' }) => {
  const tierConfig = {
    pro: { label: 'Pro', variant: 'primary' as const, icon: 'sparkles' as const },
    premium: { label: 'Premium', variant: 'premium' as const, icon: 'crown' as const },
    enterprise: { label: 'Enterprise', variant: 'gold' as const, icon: 'crown' as const },
  };

  const config = tierConfig[tier];

  return (
    <Badge
      variant={config.variant}
      size={size}
      style={style}
      icon={config.icon}
    >
      {config.label}
    </Badge>
  );
};

export default Badge;

/**
 * NEXT Career Intelligence - Progress Bar Component
 * Super-Premium Design System
 *
 * Elegant progress bar component for loading states, skill levels, and progress tracking.
 * Supports multiple variants, animations, and labels.
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Check, Crown, Sparkles } from 'lucide-react';

export interface ProgressBarProps {
  /** Current progress value (0-100) */
  value: number;
  /** Maximum value (default 100) */
  max?: number;
  /** Size variant */
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  /** Visual variant */
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'error' | 'gradient' | 'premium';
  /** Show percentage label */
  showLabel?: boolean;
  /** Custom label */
  label?: string;
  /** Label position */
  labelPosition?: 'top' | 'bottom' | 'inside' | 'right';
  /** Show icon when complete */
  showCompleteIcon?: boolean;
  /** Animate progress changes */
  animate?: boolean;
  /** Indeterminate loading state */
  indeterminate?: boolean;
  /** Custom className */
  className?: string;
  /** Striped pattern */
  striped?: boolean;
  /** Animated stripes */
  stripedAnimated?: boolean;
}

/**
 * Premium Progress Bar Component
 *
 * @example
 * ```tsx
 * <ProgressBar value={75} variant="primary" showLabel />
 * <ProgressBar value={100} variant="success" showCompleteIcon />
 * <ProgressBar indeterminate variant="gradient" />
 * ```
 */
export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  size = 'md',
  variant = 'primary',
  showLabel = false,
  label,
  labelPosition = 'right',
  showCompleteIcon = false,
  animate = true,
  indeterminate = false,
  className = '',
  striped = false,
  stripedAnimated = false,
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  const isComplete = percentage >= 100;

  // Size classes
  const sizeClasses = {
    xs: 'h-1',
    sm: 'h-2',
    md: 'h-3',
    lg: 'h-4',
    xl: 'h-6',
  };

  const labelSizes = {
    xs: 'text-xs',
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
    xl: 'text-lg',
  };

  // Variant colors
  const variantClasses = {
    default: 'bg-gray-600',
    primary: 'bg-primary-600',
    success: 'bg-green-600',
    warning: 'bg-amber-600',
    error: 'bg-red-600',
    gradient: 'bg-gradient-to-r from-primary-600 to-primary-500',
    premium: 'bg-gradient-to-r from-purple-600 via-primary-600 to-pink-600',
  };

  const backgroundClasses = {
    default: 'bg-gray-200 dark:bg-gray-700',
    primary: 'bg-primary-100 dark:bg-primary-900/30',
    success: 'bg-green-100 dark:bg-green-900/30',
    warning: 'bg-amber-100 dark:bg-amber-900/30',
    error: 'bg-red-100 dark:bg-red-900/30',
    gradient: 'bg-gray-200 dark:bg-gray-700',
    premium: 'bg-gray-200 dark:bg-gray-700',
  };

  const renderLabel = () => {
    const labelText = label || `${Math.round(percentage)}%`;
    const labelClass = `${labelSizes[size]} font-medium text-gray-700 dark:text-gray-300`;

    if (isComplete && showCompleteIcon) {
      return (
        <span className={`${labelClass} flex items-center gap-1.5`}>
          <Check className="w-4 h-4 text-green-600" />
          Complete
        </span>
      );
    }

    return <span className={labelClass}>{labelText}</span>;
  };

  const progressBar = (
    <div
      className={`
        relative w-full rounded-full overflow-hidden
        ${sizeClasses[size]}
        ${backgroundClasses[variant]}
        ${className}
      `}
      role="progressbar"
      aria-valuenow={indeterminate ? undefined : percentage}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={label || 'Progress'}
    >
      {/* Indeterminate animation */}
      {indeterminate ? (
        <motion.div
          className={`
            absolute inset-y-0 w-1/3
            ${variantClasses[variant]}
            rounded-full
          `}
          animate={{
            x: ['-100%', '400%'],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ) : (
        <>
          {/* Progress fill */}
          <motion.div
            className={`
              h-full rounded-full
              ${variantClasses[variant]}
              ${striped ? 'bg-stripes' : ''}
              ${stripedAnimated ? 'animate-stripes' : ''}
            `}
            initial={animate ? { width: 0 } : undefined}
            animate={{ width: `${percentage}%` }}
            transition={
              animate
                ? { duration: 0.8, ease: [0.16, 1, 0.3, 1] }
                : { duration: 0 }
            }
          />

          {/* Striped pattern */}
          {striped && (
            <div
              className={`
                absolute inset-0 rounded-full
                ${stripedAnimated ? 'animate-stripes-move' : ''}
              `}
              style={{
                backgroundImage:
                  'linear-gradient(45deg, rgba(255,255,255,.15) 25%, transparent 25%, transparent 50%, rgba(255,255,255,.15) 50%, rgba(255,255,255,.15) 75%, transparent 75%, transparent)',
                backgroundSize: '1rem 1rem',
                width: `${percentage}%`,
              }}
            />
          )}
        </>
      )}
    </div>
  );

  if (!showLabel && labelPosition === 'inside') {
    return (
      <div className="relative">
        {progressBar}
        <div
          className={`
            absolute inset-0 flex items-center justify-center
            ${labelSizes[size]} font-medium text-white
          `}
        >
          {renderLabel()}
        </div>
      </div>
    );
  }

  if (!showLabel) {
    return progressBar;
  }

  if (labelPosition === 'top') {
    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          {renderLabel()}
        </div>
        {progressBar}
      </div>
    );
  }

  if (labelPosition === 'bottom') {
    return (
      <div className="space-y-2">
        {progressBar}
        <div className="flex items-center justify-between">
          {renderLabel()}
        </div>
      </div>
    );
  }

  // Default: right position
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1">{progressBar}</div>
      {renderLabel()}
    </div>
  );
};

/**
 * Skill Progress Bar - Pre-configured for skill levels
 */
export const SkillProgress: React.FC<{
  skill: string;
  level: number; // 0-100
  showLevel?: boolean;
  size?: ProgressBarProps['size'];
}> = ({ skill, level, showLevel = true, size = 'md' }) => {
  const getLevelLabel = (value: number) => {
    if (value >= 90) return 'Expert';
    if (value >= 70) return 'Advanced';
    if (value >= 50) return 'Intermediate';
    if (value >= 30) return 'Beginner';
    return 'Novice';
  };

  const getVariant = (value: number): ProgressBarProps['variant'] => {
    if (value >= 90) return 'premium';
    if (value >= 70) return 'success';
    if (value >= 50) return 'primary';
    if (value >= 30) return 'warning';
    return 'default';
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-900 dark:text-white">
          {skill}
        </span>
        {showLevel && (
          <span className="text-sm text-gray-500 dark:text-gray-400">
            {getLevelLabel(level)}
          </span>
        )}
      </div>
      <ProgressBar value={level} variant={getVariant(level)} size={size} />
    </div>
  );
};

/**
 * Profile Completion Progress
 */
export const ProfileCompletion: React.FC<{
  completedSteps: number;
  totalSteps: number;
  steps?: Array<{ label: string; completed: boolean }>;
}> = ({ completedSteps, totalSteps, steps }) => {
  const percentage = (completedSteps / totalSteps) * 100;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Profile Completion
        </h3>
        <span className="text-sm font-medium text-primary-600">
          {completedSteps} of {totalSteps} completed
        </span>
      </div>

      <ProgressBar
        value={percentage}
        variant={percentage === 100 ? 'success' : 'primary'}
        size="lg"
        showCompleteIcon
        showLabel
        labelPosition="inside"
      />

      {steps && (
        <div className="space-y-2 mt-4">
          {steps.map((step, index) => (
            <div key={index} className="flex items-center gap-3">
              <div
                className={`
                  w-5 h-5 rounded-full flex items-center justify-center
                  ${
                    step.completed
                      ? 'bg-green-600 text-white'
                      : 'border-2 border-gray-300 dark:border-gray-600'
                  }
                `}
              >
                {step.completed && <Check className="w-3 h-3" />}
              </div>
              <span
                className={`text-sm ${
                  step.completed
                    ? 'text-gray-900 dark:text-white'
                    : 'text-gray-500 dark:text-gray-400'
                }`}
              >
                {step.label}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

/**
 * Loading Progress Bar - Indeterminate
 */
export const LoadingProgress: React.FC<{
  message?: string;
  variant?: ProgressBarProps['variant'];
}> = ({ message, variant = 'primary' }) => {
  return (
    <div className="space-y-3">
      <ProgressBar indeterminate variant={variant} size="sm" />
      {message && (
        <p className="text-center text-sm text-gray-500 dark:text-gray-400">
          {message}
        </p>
      )}
    </div>
  );
};

export default ProgressBar;

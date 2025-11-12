/**
 * Premium Skeleton Loading Component
 * Beautiful, animated skeleton screens for all loading states
 */

'use client';

import React from 'react';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular' | 'rounded';
  width?: string | number;
  height?: string | number;
  animation?: 'pulse' | 'wave' | 'none';
  glass?: boolean;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className = '',
  variant = 'text',
  width,
  height,
  animation = 'pulse',
  glass = false,
}) => {
  const variantClasses = {
    text: 'rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-none',
    rounded: 'rounded-xl',
  };

  const animationClasses = glass
    ? {
        pulse: 'skeleton-glass',
        wave: 'skeleton-glass',
        none: '',
      }
    : {
        pulse: 'animate-pulse',
        wave: 'animate-shimmer bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 bg-[length:200%_100%]',
        none: '',
      };

  const bgClass = glass ? '' : 'bg-gray-200 dark:bg-gray-700';

  const style: React.CSSProperties = {
    width: width ? (typeof width === 'number' ? `${width}px` : width) : undefined,
    height: height ? (typeof height === 'number' ? `${height}px` : height) : undefined,
  };

  return (
    <div
      className={`
        ${bgClass}
        ${variantClasses[variant]}
        ${animationClasses[animation]}
        ${className}
      `}
      style={style}
      aria-label="Loading..."
      role="status"
    />
  );
};

// Pre-built skeleton components for common patterns

export const SkeletonText: React.FC<{ lines?: number; className?: string }> = ({
  lines = 3,
  className = '',
}) => (
  <div className={`space-y-2 ${className}`}>
    {Array.from({ length: lines }).map((_, i) => (
      <Skeleton
        key={i}
        variant="text"
        height={16}
        width={i === lines - 1 ? '80%' : '100%'}
      />
    ))}
  </div>
);

export const SkeletonCard: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg ${className}`}>
    <div className="flex items-start gap-4">
      {/* Avatar */}
      <Skeleton variant="circular" width={64} height={64} />

      {/* Content */}
      <div className="flex-1 space-y-3">
        {/* Title */}
        <Skeleton variant="text" height={20} width="60%" />

        {/* Subtitle */}
        <Skeleton variant="text" height={16} width="40%" />

        {/* Description */}
        <SkeletonText lines={2} />

        {/* Tags */}
        <div className="flex gap-2 mt-4">
          <Skeleton variant="rounded" width={80} height={28} />
          <Skeleton variant="rounded" width={100} height={28} />
          <Skeleton variant="rounded" width={90} height={28} />
        </div>
      </div>
    </div>
  </div>
);

export const SkeletonJobCard: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`p-6 bg-white dark:bg-gray-800 rounded-xl shadow-md border border-gray-200 dark:border-gray-700 ${className}`}>
    <div className="flex items-start gap-4">
      {/* Company logo */}
      <Skeleton variant="rounded" width={56} height={56} />

      {/* Content */}
      <div className="flex-1 space-y-3">
        {/* Job title */}
        <Skeleton variant="text" height={20} width="70%" />

        {/* Company */}
        <Skeleton variant="text" height={16} width="40%" />

        {/* Meta info */}
        <div className="flex gap-4 mt-2">
          <Skeleton variant="text" height={14} width={80} />
          <Skeleton variant="text" height={14} width={100} />
          <Skeleton variant="text" height={14} width={90} />
        </div>

        {/* Skills */}
        <div className="flex flex-wrap gap-2 mt-3">
          {[60, 80, 70, 90].map((width, i) => (
            <Skeleton key={i} variant="rounded" width={width} height={24} />
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="space-y-2">
        <Skeleton variant="rounded" width={40} height={40} />
        <Skeleton variant="rounded" width={40} height={40} />
      </div>
    </div>
  </div>
);

export const SkeletonDashboard: React.FC = () => (
  <div className="space-y-6">
    {/* Header */}
    <div className="flex items-center justify-between">
      <div className="space-y-2">
        <Skeleton variant="text" height={32} width={300} />
        <Skeleton variant="text" height={16} width={200} />
      </div>
      <Skeleton variant="rounded" width={120} height={40} />
    </div>

    {/* Stats Grid */}
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {[1, 2, 3].map((i) => (
        <div key={i} className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
          <Skeleton variant="text" height={16} width="40%" className="mb-4" />
          <Skeleton variant="text" height={36} width="60%" />
        </div>
      ))}
    </div>

    {/* Chart */}
    <div className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
      <Skeleton variant="text" height={24} width={200} className="mb-6" />
      <Skeleton variant="rectangular" height={300} />
    </div>

    {/* Table */}
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <Skeleton variant="text" height={24} width={150} />
      </div>
      <div className="divide-y divide-gray-200 dark:divide-gray-700">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="p-4 flex items-center gap-4">
            <Skeleton variant="circular" width={40} height={40} />
            <div className="flex-1 space-y-2">
              <Skeleton variant="text" height={16} width="60%" />
              <Skeleton variant="text" height={14} width="40%" />
            </div>
            <Skeleton variant="rounded" width={80} height={32} />
          </div>
        ))}
      </div>
    </div>
  </div>
);

export const SkeletonProfile: React.FC = () => (
  <div className="space-y-6">
    {/* Header */}
    <div className="flex items-start gap-6 p-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
      <Skeleton variant="circular" width={128} height={128} />
      <div className="flex-1 space-y-4">
        <Skeleton variant="text" height={32} width="40%" />
        <Skeleton variant="text" height={20} width="30%" />
        <SkeletonText lines={2} />
        <div className="flex gap-3 mt-4">
          <Skeleton variant="rounded" width={120} height={40} />
          <Skeleton variant="rounded" width={120} height={40} />
        </div>
      </div>
    </div>

    {/* Sections */}
    {[1, 2, 3].map((i) => (
      <div key={i} className="p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg space-y-4">
        <Skeleton variant="text" height={24} width="25%" />
        <SkeletonText lines={4} />
      </div>
    ))}
  </div>
);

/**
 * Usage Examples:
 *
 * // Single skeleton
 * <Skeleton width={200} height={20} />
 *
 * // Text skeleton
 * <SkeletonText lines={3} />
 *
 * // Card skeleton
 * <SkeletonCard />
 *
 * // Job listing skeleton
 * <div className="space-y-4">
 *   {[1, 2, 3].map(i => (
 *     <SkeletonJobCard key={i} />
 *   ))}
 * </div>
 *
 * // Dashboard loading
 * {isLoading ? <SkeletonDashboard /> : <Dashboard data={data} />}
 *
 * // Profile loading
 * {isLoading ? <SkeletonProfile /> : <Profile user={user} />}
 */

// Add shimmer animation to tailwind.config.js:
/*
module.exports = {
  theme: {
    extend: {
      keyframes: {
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      animation: {
        shimmer: 'shimmer 2s ease-in-out infinite',
      },
    },
  },
};
*/

/**
 * NEXT Career Intelligence - Empty State Component
 * Super-Premium Design System
 *
 * Elegant empty state component for no data scenarios.
 * Supports multiple variants, custom illustrations, and call-to-action buttons.
 */

'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  Search,
  Briefcase,
  FileText,
  Users,
  TrendingUp,
  BookOpen,
  Bell,
  Star,
  Target,
  Package,
  Inbox,
  Filter,
  AlertCircle,
  LucideIcon,
} from 'lucide-react';

export interface EmptyStateProps {
  /** Title text */
  title: string;
  /** Description text */
  description?: string;
  /** Icon to display */
  icon?: React.ReactNode | EmptyStateIcon;
  /** Icon size */
  iconSize?: 'sm' | 'md' | 'lg' | 'xl';
  /** Primary action button */
  action?: {
    label: string;
    onClick: () => void;
    icon?: React.ReactNode;
  };
  /** Secondary action button */
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
  /** Custom illustration/image */
  illustration?: React.ReactNode;
  /** Custom className */
  className?: string;
  /** Show animation */
  animate?: boolean;
  /** Compact layout */
  compact?: boolean;
}

export type EmptyStateIcon =
  | 'search'
  | 'jobs'
  | 'resume'
  | 'users'
  | 'analytics'
  | 'learning'
  | 'notifications'
  | 'bookmarks'
  | 'goals'
  | 'packages'
  | 'inbox'
  | 'filter'
  | 'error';

/**
 * Premium Empty State Component
 *
 * @example
 * ```tsx
 * <EmptyState
 *   icon="jobs"
 *   title="No jobs found"
 *   description="Try adjusting your search filters or check back later."
 *   action={{
 *     label: "Clear filters",
 *     onClick: () => clearFilters()
 *   }}
 * />
 * ```
 */
export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon = 'inbox',
  iconSize = 'lg',
  action,
  secondaryAction,
  illustration,
  className = '',
  animate = true,
  compact = false,
}) => {
  // Icon size classes
  const iconSizes = {
    sm: 'w-12 h-12',
    md: 'w-16 h-16',
    lg: 'w-24 h-24',
    xl: 'w-32 h-32',
  };

  // Icon mapping
  const iconMap: Record<EmptyStateIcon, LucideIcon> = {
    search: Search,
    jobs: Briefcase,
    resume: FileText,
    users: Users,
    analytics: TrendingUp,
    learning: BookOpen,
    notifications: Bell,
    bookmarks: Star,
    goals: Target,
    packages: Package,
    inbox: Inbox,
    filter: Filter,
    error: AlertCircle,
  };

  const renderIcon = () => {
    if (illustration) return illustration;

    let IconComponent: React.ReactNode;

    if (typeof icon === 'string' && icon in iconMap) {
      const Icon = iconMap[icon];
      IconComponent = <Icon className="w-full h-full" strokeWidth={1.5} />;
    } else {
      IconComponent = icon;
    }

    return (
      <motion.div
        initial={animate ? { scale: 0.8, opacity: 0 } : undefined}
        animate={animate ? { scale: 1, opacity: 1 } : undefined}
        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
        className={`
          ${iconSizes[iconSize]}
          mx-auto
          text-gray-300 dark:text-gray-600
          ${animate ? 'animate-float' : ''}
        `}
      >
        {IconComponent}
      </motion.div>
    );
  };

  const contentVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { delay: 0.2, duration: 0.5 },
    },
  };

  return (
    <motion.div
      initial={animate ? 'hidden' : undefined}
      animate={animate ? 'visible' : undefined}
      variants={contentVariants}
      className={`
        flex flex-col items-center justify-center
        text-center
        ${compact ? 'py-8 px-4' : 'py-16 px-6'}
        ${className}
      `}
    >
      {/* Icon/Illustration */}
      <div className={compact ? 'mb-4' : 'mb-6'}>
        {renderIcon()}
      </div>

      {/* Title */}
      <h3
        className={`
          font-semibold text-gray-900 dark:text-white
          ${compact ? 'text-lg' : 'text-2xl'}
        `}
      >
        {title}
      </h3>

      {/* Description */}
      {description && (
        <p
          className={`
            text-gray-500 dark:text-gray-400
            max-w-md
            ${compact ? 'mt-2 text-sm' : 'mt-3 text-base'}
          `}
        >
          {description}
        </p>
      )}

      {/* Actions */}
      {(action || secondaryAction) && (
        <div className={`flex items-center gap-3 ${compact ? 'mt-4' : 'mt-6'}`}>
          {action && (
            <button
              onClick={action.onClick}
              className="
                inline-flex items-center gap-2
                px-5 py-2.5
                bg-gradient-to-r from-primary-600 to-primary-500
                text-white font-medium
                rounded-lg
                hover:from-primary-700 hover:to-primary-600
                transition-all duration-200
                shadow-lg shadow-primary-500/30
                focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
              "
            >
              {action.icon}
              {action.label}
            </button>
          )}

          {secondaryAction && (
            <button
              onClick={secondaryAction.onClick}
              className="
                px-5 py-2.5
                text-gray-700 dark:text-gray-300
                border border-gray-300 dark:border-gray-600
                rounded-lg
                hover:bg-gray-50 dark:hover:bg-gray-800
                transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
              "
            >
              {secondaryAction.label}
            </button>
          )}
        </div>
      )}
    </motion.div>
  );
};

/**
 * No Results Empty State - For search/filter scenarios
 */
export const NoResultsState: React.FC<{
  searchTerm?: string;
  onClearFilters?: () => void;
  onResetSearch?: () => void;
}> = ({ searchTerm, onClearFilters, onResetSearch }) => {
  return (
    <EmptyState
      icon="search"
      title={searchTerm ? `No results for "${searchTerm}"` : 'No results found'}
      description="Try adjusting your search or filters to find what you're looking for."
      action={
        onClearFilters
          ? {
              label: 'Clear all filters',
              onClick: onClearFilters,
              icon: <Filter className="w-4 h-4" />,
            }
          : undefined
      }
      secondaryAction={
        onResetSearch
          ? {
              label: 'Reset search',
              onClick: onResetSearch,
            }
          : undefined
      }
    />
  );
};

/**
 * No Jobs Empty State
 */
export const NoJobsState: React.FC<{
  onBrowseJobs?: () => void;
  onSetAlerts?: () => void;
}> = ({ onBrowseJobs, onSetAlerts }) => {
  return (
    <EmptyState
      icon="jobs"
      title="No jobs yet"
      description="We haven't found any matching jobs. Try browsing available positions or set up job alerts."
      action={
        onBrowseJobs
          ? {
              label: 'Browse jobs',
              onClick: onBrowseJobs,
              icon: <Briefcase className="w-4 h-4" />,
            }
          : undefined
      }
      secondaryAction={
        onSetAlerts
          ? {
              label: 'Set up alerts',
              onClick: onSetAlerts,
            }
          : undefined
      }
    />
  );
};

/**
 * No Bookmarks Empty State
 */
export const NoBookmarksState: React.FC<{
  onBrowseJobs?: () => void;
}> = ({ onBrowseJobs }) => {
  return (
    <EmptyState
      icon="bookmarks"
      title="No saved jobs"
      description="Start bookmarking jobs you're interested in to review them later."
      action={
        onBrowseJobs
          ? {
              label: 'Browse jobs',
              onClick: onBrowseJobs,
              icon: <Search className="w-4 h-4" />,
            }
          : undefined
      }
    />
  );
};

/**
 * No Notifications Empty State
 */
export const NoNotificationsState: React.FC = () => {
  return (
    <EmptyState
      icon="notifications"
      title="You're all caught up!"
      description="No new notifications at the moment."
      compact
    />
  );
};

/**
 * Error Empty State
 */
export const ErrorState: React.FC<{
  title?: string;
  description?: string;
  onRetry?: () => void;
  onGoHome?: () => void;
}> = ({
  title = 'Something went wrong',
  description = "We're having trouble loading this content. Please try again.",
  onRetry,
  onGoHome,
}) => {
  return (
    <EmptyState
      icon="error"
      title={title}
      description={description}
      action={
        onRetry
          ? {
              label: 'Try again',
              onClick: onRetry,
            }
          : undefined
      }
      secondaryAction={
        onGoHome
          ? {
              label: 'Go to home',
              onClick: onGoHome,
            }
          : undefined
      }
    />
  );
};

/**
 * Coming Soon Empty State
 */
export const ComingSoonState: React.FC<{
  title?: string;
  description?: string;
  onNotifyMe?: () => void;
}> = ({
  title = 'Coming soon',
  description = 'This feature is under development. Stay tuned!',
  onNotifyMe,
}) => {
  return (
    <EmptyState
      icon="packages"
      title={title}
      description={description}
      action={
        onNotifyMe
          ? {
              label: 'Notify me',
              onClick: onNotifyMe,
              icon: <Bell className="w-4 h-4" />,
            }
          : undefined
      }
    />
  );
};

export default EmptyState;

'use client';

import { motion } from 'framer-motion';
import { ExclamationTriangleIcon, BriefcaseIcon } from '@heroicons/react/24/outline';

interface PriorityActionCardProps {
  type: 'warning' | 'opportunity';
  title: string;
  description: string;
  onAction?: () => void;
  onDismiss?: () => void;
}

export default function PriorityActionCard({
  type,
  title,
  description,
  onAction,
  onDismiss,
}: PriorityActionCardProps) {
  const config = {
    warning: {
      icon: ExclamationTriangleIcon,
      color: 'text-warning-500',
      bg: 'bg-warning-500/10',
      badge: 'High Priority',
      badgeBg: 'bg-warning-100 dark:bg-warning-900/30',
      badgeText: 'text-warning-700 dark:text-warning-300',
    },
    opportunity: {
      icon: BriefcaseIcon,
      color: 'text-primary-500',
      bg: 'bg-primary-500/10',
      badge: 'New',
      badgeBg: 'bg-primary-100 dark:bg-primary-900/30',
      badgeText: 'text-primary-700 dark:text-primary-300',
    },
  };

  const style = config[type] || config.opportunity;
  const Icon = style.icon;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4 }}
      className="glass-card hover-reflect rounded-2xl p-6"
    >
      <div className="flex items-start space-x-4">
        <div className={`w-12 h-12 rounded-full ${style.bg} flex items-center justify-center flex-shrink-0`}>
          <Icon className={`w-6 h-6 ${style.color}`} />
        </div>

        <div className="flex-1">
          {type === 'warning' && (
            <span
              className={`inline-block px-2 py-1 text-xs font-medium ${style.badgeText} ${style.badgeBg} rounded-full mb-2`}
            >
              {style.badge}
            </span>
          )}

          <h3 className="text-lg font-semibold text-white">
            {title}
          </h3>

          <p className="mt-2 text-sm text-ink-300">
            {description}
          </p>
        </div>
      </div>

      <div className="mt-6 flex space-x-3">
        {onAction && (
          <button
            onClick={onAction}
            className="flex-1 py-2.5 px-4 bg-primary-500 hover:bg-primary-600 text-white font-medium rounded-xl transition-colors"
          >
            Take Action
          </button>
        )}

        {onDismiss && (
          <button
            onClick={onDismiss}
            className="px-4 py-2.5 text-ink-400 hover:text-white transition-colors"
          >
            Dismiss
          </button>
        )}
      </div>
    </motion.div>
  );
}

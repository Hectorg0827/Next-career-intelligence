'use client';

import { motion } from 'framer-motion';
import { BriefcaseIcon, ExclamationTriangleIcon, ChartBarIcon } from '@heroicons/react/24/outline';

interface EmptyStateProps {
  type: 'jobs' | 'actions' | 'health';
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

const iconConfig = {
  jobs: { icon: BriefcaseIcon, color: 'text-primary-500', bg: 'bg-primary-500/10' },
  actions: { icon: ExclamationTriangleIcon, color: 'text-warning-500', bg: 'bg-warning-500/10' },
  health: { icon: ChartBarIcon, color: 'text-success-500', bg: 'bg-success-500/10' },
};

export default function EmptyState({ type, title, description, actionLabel, onAction }: EmptyStateProps) {
  const config = iconConfig[type];
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="glass-card rounded-2xl p-12 text-center"
    >
      <div className={`w-16 h-16 ${config.bg} rounded-full flex items-center justify-center mx-auto mb-4`}>
        <Icon className={`w-8 h-8 ${config.color}`} />
      </div>

      <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
      <p className="text-ink-300 max-w-md mx-auto mb-6">{description}</p>

      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white font-semibold rounded-xl transition-colors"
        >
          {actionLabel}
        </button>
      )}
    </motion.div>
  );
}

export function NoJobsEmptyState({ onBrowseJobs }: { onBrowseJobs?: () => void }) {
  return (
    <EmptyState
      type="jobs"
      title="No Job Matches Yet"
      description="Complete your profile and set your career goals to get personalized job recommendations."
      actionLabel="Browse All Jobs"
      onAction={onBrowseJobs}
    />
  );
}

export function NoActionsEmptyState() {
  return (
    <EmptyState
      type="actions"
      title="All Clear!"
      description="You have no priority actions at the moment. Keep up the great work on your career development."
    />
  );
}

export function NoHealthDataEmptyState({ onCompleteProfile }: { onCompleteProfile?: () => void }) {
  return (
    <EmptyState
      type="health"
      title="Complete Your Profile"
      description="We need more information to calculate your Career Health Score. Complete your profile to get started."
      actionLabel="Complete Profile"
      onAction={onCompleteProfile}
    />
  );
}

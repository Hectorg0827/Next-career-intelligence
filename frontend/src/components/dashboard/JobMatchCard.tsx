'use client';

import { motion } from 'framer-motion';
import { MapPinIcon, CurrencyDollarIcon } from '@heroicons/react/24/outline';

interface JobMatchCardProps {
  job: {
    id: string;
    title: string;
    company: string;
    location: string;
    isRemote?: boolean;
    salaryMin?: number;
    salaryMax?: number;
    gaps?: string[];
  };
  matchScore: number;
  onApply?: () => void;
}

export default function JobMatchCard({ job, matchScore, onApply }: JobMatchCardProps) {
  const getMatchColor = (score: number) => {
    if (score >= 90) return 'text-success-500 bg-success-500/10';
    if (score >= 75) return 'text-primary-500 bg-primary-500/10';
    return 'text-warning-500 bg-warning-500/10';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="glass-card hover-reflect rounded-2xl p-6"
    >
      <div className={`inline-flex px-3 py-1.5 rounded-full text-sm font-semibold mb-4 ${getMatchColor(matchScore)}`}>
        {matchScore}% Match
      </div>

      <h3 className="text-xl font-bold text-white mb-2">
        {job.title}
      </h3>

      <p className="text-base text-ink-200 font-medium mb-4">
        {job.company}
      </p>

      <div className="space-y-2 mb-4">
        <div className="flex items-center text-sm text-ink-300">
          <MapPinIcon className="w-4 h-4 mr-2" />
          {job.location} {job.isRemote && '• Remote'}
        </div>

        {job.salaryMin && job.salaryMax && (
          <div className="flex items-center text-sm text-ink-300">
            <CurrencyDollarIcon className="w-4 h-4 mr-2" />
            ${job.salaryMin?.toLocaleString()} - ${job.salaryMax?.toLocaleString()}
          </div>
        )}
      </div>

      <div className="mb-4 space-y-1.5">
        <div className="flex items-start text-sm">
          <span className="text-success-500 mr-2">✓</span>
          <span className="text-ink-200">
            10/12 required skills
          </span>
        </div>
        <div className="flex items-start text-sm">
          <span className="text-success-500 mr-2">✓</span>
          <span className="text-ink-200">
            Aligns with your career goals
          </span>
        </div>
        {job.gaps && job.gaps.length > 0 && (
          <div className="flex items-start text-sm">
            <span className="text-warning-500 mr-2">⚠</span>
            <span className="text-ink-200">
              Missing: {job.gaps.join(', ')}
            </span>
          </div>
        )}
      </div>

      {onApply && (
        <button
          onClick={onApply}
          className="w-full py-3 bg-primary-500 hover:bg-primary-600 text-white font-semibold rounded-xl transition-colors"
        >
          Quick Apply
        </button>
      )}
    </motion.div>
  );
}

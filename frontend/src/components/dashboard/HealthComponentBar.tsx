'use client';

import { motion } from 'framer-motion';

interface HealthComponentBarProps {
  name: string;
  score: number;
  description: string;
  onClick?: () => void;
}

export default function HealthComponentBar({ name, score, description, onClick }: HealthComponentBarProps) {
  const getColor = (s: number) => {
    if (s >= 80) return 'bg-success-500';
    if (s >= 60) return 'bg-primary-500';
    return 'bg-warning-500';
  };

  return (
    <motion.div
      whileHover={{ scale: 1.01 }}
      onClick={onClick}
      className={`glass-card hover-reflect rounded-xl p-5 ${onClick ? 'cursor-pointer' : ''}`}
    >
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-base font-semibold text-white">
          {name}
        </h4>
        <div className="flex items-center space-x-2">
          <span className="text-2xl font-bold text-white">{score}</span>
          <span className="text-sm text-ink-500">/100</span>
        </div>
      </div>

      <div className="w-full h-2 bg-gray-700/30 rounded-full mb-3 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className={`h-full ${getColor(score)}`}
        />
      </div>

      <p className="text-sm text-ink-300">{description}</p>
    </motion.div>
  );
}

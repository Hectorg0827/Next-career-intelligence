'use client';

import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import { motion } from 'framer-motion';
import 'react-circular-progressbar/dist/styles.css';

interface CareerHealthGaugeProps {
  score: number;
  trend?: number;
  onViewReport?: () => void;
}

export default function CareerHealthGauge({ score, trend, onViewReport }: CareerHealthGaugeProps) {
  const getColor = (s: number) => {
    if (s >= 80) return '#34C759'; // success-500
    if (s >= 60) return '#FF9500'; // warning-500
    return '#FF3B30'; // danger-500
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="glass-card hover-reflect rounded-3xl p-8"
    >
      <h2 className="text-2xl font-semibold text-white mb-6">Career Health Score</h2>

      <div className="w-48 h-48 mx-auto">
        <CircularProgressbar
          value={score}
          text={`${score}`}
          strokeWidth={8}
          styles={buildStyles({
            textSize: '32px',
            textColor: getColor(score),
            pathColor: getColor(score),
            trailColor: 'rgba(255, 255, 255, 0.1)',
            pathTransitionDuration: 1.5,
          })}
        />
      </div>

      {trend !== undefined && (
        <div className="mt-6 text-center">
          <span className={`text-2xl ${trend > 0 ? 'text-success-500' : 'text-danger-500'}`}>
            {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}
          </span>
          <span className="ml-2 text-ink-300">
            points this week
          </span>
        </div>
      )}

      {onViewReport && (
        <button
          onClick={onViewReport}
          className="w-full mt-6 py-3 text-primary-500 font-medium hover:bg-white/5 rounded-xl transition-colors"
        >
          View Full Report →
        </button>
      )}
    </motion.div>
  );
}

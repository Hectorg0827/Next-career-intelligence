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
      className="glass-card-enhanced hover-reflect card-padding-lg"
    >
      <h2 className="heading-sm text-primary-white mb-8 text-center">Career Health Score</h2>

      <div className="w-52 h-52 mx-auto">
        <CircularProgressbar
          value={score}
          text={`${score}`}
          strokeWidth={6}
          styles={buildStyles({
            textSize: '28px',
            textColor: getColor(score),
            pathColor: getColor(score),
            trailColor: 'rgba(255, 255, 255, 0.08)',
            pathTransitionDuration: 1.5,
          })}
        />
      </div>

      {trend !== undefined && (
        <div className="mt-8 text-center">
          <span className={`text-3xl font-bold ${trend > 0 ? 'text-ios-green' : 'text-ios-red'}`}>
            {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}
          </span>
          <span className="ml-3 body-md text-secondary-white">
            points this week
          </span>
        </div>
      )}

      {onViewReport && (
        <button
          onClick={onViewReport}
          className="w-full mt-8 py-3.5 btn-secondary hover:bg-white/15"
        >
          <span className="text-primary-white">View Full Report →</span>
        </button>
      )}
    </motion.div>
  );
}

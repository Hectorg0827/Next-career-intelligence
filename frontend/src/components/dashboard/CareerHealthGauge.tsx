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
      className="bg-white rounded-lg border border-slate-200 shadow-sm hover:shadow-md transition-all duration-200 p-8"
    >
      <h2 className="text-xl font-semibold text-slate-800 mb-8 text-center">Career Health Score</h2>

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
          <span className={`text-3xl font-bold ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}
          </span>
          <span className="ml-3 text-base text-slate-600">
            points this week
          </span>
        </div>
      )}

      {onViewReport && (
        <button
          onClick={onViewReport}
          className="w-full mt-8 py-3.5 text-blue-600 hover:text-blue-700 font-medium"
        >
          <span className="text-blue-600">View Full Report →</span>
        </button>
      )}
    </motion.div>
  );
}

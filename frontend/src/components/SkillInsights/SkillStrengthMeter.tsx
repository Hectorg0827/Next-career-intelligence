'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface SkillStrength {
  overall_score: number;
  category_scores: Record<string, number>;
  total_skills: number;
  skill_diversity: number;
  interpretation: string;
}

interface SkillStrengthMeterProps {
  skillStrength: SkillStrength;
}

const SkillStrengthMeter: React.FC<SkillStrengthMeterProps> = ({ skillStrength }) => {
  const score = Math.round(skillStrength.overall_score);
  const radius = 100;
  const strokeWidth = 12;
  const normalizedRadius = radius - strokeWidth / 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  // Color based on score
  const getScoreColor = (score: number) => {
    if (score >= 80) return { gradient: 'from-green-400 to-emerald-600', text: 'text-green-600', stroke: '#10b981' };
    if (score >= 60) return { gradient: 'from-blue-400 to-blue-600', text: 'text-blue-600', stroke: '#3b82f6' };
    if (score >= 40) return { gradient: 'from-yellow-400 to-orange-500', text: 'text-orange-600', stroke: '#f59e0b' };
    return { gradient: 'from-red-400 to-red-600', text: 'text-red-600', stroke: '#ef4444' };
  };

  const colors = getScoreColor(score);

  // Category icons
  const categoryIcons: Record<string, string> = {
    'Technical Skills': '💻',
    'Business Skills': '📊',
    'Soft Skills': '🤝',
    'Domain Expertise': '🎯'
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-xl p-8 border border-gray-200 dark:border-gray-700">
      <div className="flex flex-col lg:flex-row items-center gap-8">
        {/* Left: Circular meter */}
        <div className="relative flex-shrink-0">
          <svg
            height={radius * 2}
            width={radius * 2}
            className="transform -rotate-90"
          >
            {/* Background circle */}
            <circle
              stroke="#e5e7eb"
              fill="transparent"
              strokeWidth={strokeWidth}
              r={normalizedRadius}
              cx={radius}
              cy={radius}
            />
            
            {/* Progress circle with animation */}
            <motion.circle
              stroke={colors.stroke}
              fill="transparent"
              strokeWidth={strokeWidth}
              strokeDasharray={`${circumference} ${circumference}`}
              strokeDashoffset={circumference}
              r={normalizedRadius}
              cx={radius}
              cy={radius}
              strokeLinecap="round"
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset }}
              transition={{
                duration: 1.5,
                ease: "easeInOut",
                delay: 0.5
              }}
            />
          </svg>

          {/* Center text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <motion.div
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 1, type: 'spring', stiffness: 200 }}
              className={`text-5xl font-bold ${colors.text}`}
            >
              {score}
            </motion.div>
            <div className="text-sm text-gray-500 dark:text-gray-400 font-medium mt-1">
              Skill Score
            </div>
          </div>
        </div>

        {/* Right: Details */}
        <div className="flex-1 space-y-6 w-full">
          <div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Your Skill Strength
            </h3>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              {skillStrength.interpretation}
            </p>
          </div>

          {/* Stats grid */}
          <div className="grid grid-cols-2 gap-4">
            <motion.div 
              className="p-4 rounded-xl bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/30 border border-blue-200 dark:border-blue-700"
              whileHover={{ scale: 1.05 }}
              transition={{ type: 'spring', stiffness: 300 }}
            >
              <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                {skillStrength.total_skills}
              </div>
              <div className="text-sm text-gray-700 dark:text-gray-300 font-medium mt-1">
                Total Skills
              </div>
            </motion.div>

            <motion.div 
              className="p-4 rounded-xl bg-gradient-to-br from-silver-soft to-silver-light dark:from-royal-navy/30 dark:to-purple-800/30 border border-silver-soft dark:border-gold-accent"
              whileHover={{ scale: 1.05 }}
              transition={{ type: 'spring', stiffness: 300 }}
            >
              <div className="text-3xl font-bold text-gold-primary dark:text-gold-hover">
                {Math.round(skillStrength.skill_diversity * 100)}%
              </div>
              <div className="text-sm text-gray-700 dark:text-gray-300 font-medium mt-1">
                Diversity
              </div>
            </motion.div>
          </div>

          {/* Category breakdown */}
          <div className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide">
              Category Breakdown
            </h4>
            {Object.entries(skillStrength.category_scores).map(([category, categoryScore]) => (
              <div key={category} className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium text-gray-700 dark:text-gray-300">
                    {categoryIcons[category] || '📌'} {category}
                  </span>
                  <span className="text-gray-600 dark:text-gray-400 font-semibold">
                    {Math.round(categoryScore)}/100
                  </span>
                </div>
                <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <motion.div
                    className={`h-full bg-gradient-to-r ${colors.gradient}`}
                    initial={{ width: 0 }}
                    animate={{ width: `${categoryScore}%` }}
                    transition={{ duration: 1, delay: 0.8, ease: 'easeOut' }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SkillStrengthMeter;

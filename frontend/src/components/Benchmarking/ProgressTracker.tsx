'use client';

import React from 'react';
import { motion } from 'framer-motion';

/**
 * FEATURE 6: Benchmarking Dashboard - Skill Demand Tracker
 * 
 * Shows demand scores for user's skills and identifies gaps
 */

interface Skill {
  skill: string;
  demand_score: number;
  growth_rate: string;
}

interface SkillGap {
  skill: string;
  importance: 'high' | 'medium' | 'low';
  demand_score: number;
}

interface ProgressTrackerProps {
  overallScore: number;
  topSkills: Skill[];
  skillGaps: SkillGap[];
}

export default function ProgressTracker({
  overallScore,
  topSkills,
  skillGaps
}: ProgressTrackerProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreGradient = (score: number) => {
    if (score >= 80) return 'from-green-500 to-emerald-600';
    if (score >= 60) return 'from-blue-500 to-royal-blue';
    if (score >= 40) return 'from-yellow-500 to-orange-600';
    return 'from-red-500 to-gold-accent';
  };

  const getImportanceColor = (importance: string) => {
    if (importance === 'high') return 'bg-red-100 text-red-700 border-red-300';
    if (importance === 'medium') return 'bg-yellow-100 text-yellow-700 border-yellow-300';
    return 'bg-gray-100 text-gray-700 border-gray-300';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="bg-gradient-to-br from-white to-silver-soft rounded-2xl border-2 border-silver-soft p-6 shadow-lg"
    >
      {/* Header with overall score */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-900">
            📈 Skill Demand Analysis
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Market demand for your skillset
          </p>
        </div>
        
        {/* Overall score circle */}
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: 'spring', delay: 0.3 }}
          className="relative w-20 h-20"
        >
          <svg className="w-20 h-20 transform -rotate-90">
            <circle
              cx="40"
              cy="40"
              r="32"
              stroke="#E5E7EB"
              strokeWidth="6"
              fill="none"
            />
            <motion.circle
              cx="40"
              cy="40"
              r="32"
              stroke="url(#scoreGradient)"
              strokeWidth="6"
              fill="none"
              strokeLinecap="round"
              initial={{ strokeDasharray: '0 999' }}
              animate={{ strokeDasharray: `${overallScore * 2} 999` }}
              transition={{ duration: 1.5, delay: 0.5 }}
            />
            <defs>
              <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#8B5CF6" />
                <stop offset="100%" stopColor="#EC4899" />
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={`text-xl font-bold ${getScoreColor(overallScore)}`}>
              {overallScore}
            </span>
          </div>
        </motion.div>
      </div>

      {/* Top skills */}
      <div className="mb-6">
        <h4 className="text-sm font-bold text-gray-800 mb-3 flex items-center gap-2">
          <span>⭐</span>
          Your Strongest Skills
        </h4>
        <div className="space-y-3">
          {topSkills.map((skill, index) => (
            <motion.div
              key={skill.skill}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 + index * 0.1 }}
              className="bg-white rounded-lg p-3 border border-gray-200 hover:border-purple-300 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-gray-900 text-sm">
                  {skill.skill}
                </span>
                <div className="flex items-center gap-2">
                  <span className={`text-xs font-bold ${getScoreColor(skill.demand_score)}`}>
                    {skill.demand_score}/100
                  </span>
                  <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full font-medium">
                    {skill.growth_rate}
                  </span>
                </div>
              </div>
              
              {/* Progress bar */}
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${skill.demand_score}%` }}
                  transition={{ duration: 1, delay: 0.5 + index * 0.1 }}
                  className={`h-full bg-gradient-to-r ${getScoreGradient(skill.demand_score)}`}
                />
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Skill gaps */}
      <div>
        <h4 className="text-sm font-bold text-gray-800 mb-3 flex items-center gap-2">
          <span>🎯</span>
          High-Value Skills to Learn
        </h4>
        <div className="space-y-2">
          {skillGaps.map((gap, index) => (
            <motion.div
              key={gap.skill}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.7 + index * 0.1 }}
              className={`flex items-center justify-between p-3 rounded-lg border ${getImportanceColor(gap.importance)}`}
            >
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold">{gap.skill}</span>
                <span className="text-xs px-2 py-0.5 bg-white rounded-full border border-current">
                  {gap.importance}
                </span>
              </div>
              <span className="text-xs font-bold">
                Demand: {gap.demand_score}/100
              </span>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Call to action */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="mt-6 bg-gradient-to-r from-silver-light to-pink-100 border border-purple-300 rounded-xl p-4"
      >
        <p className="text-sm text-royal-navy">
          <strong>💡 Action Item:</strong> Focus on the high-importance gaps first. 
          These skills are in demand and will significantly boost your market value!
        </p>
      </motion.div>
    </motion.div>
  );
}

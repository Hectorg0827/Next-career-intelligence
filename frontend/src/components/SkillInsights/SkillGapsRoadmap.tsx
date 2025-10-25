'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';

interface SkillGap {
  skill: string;
  priority: string;
  learn_difficulty: string;
  market_demand: string;
  estimated_learning_time: string;
  confidence_score: number;
  why_important: string;
}

interface SkillGapsRoadmapProps {
  skillGaps: SkillGap[];
}

const SkillGapsRoadmap: React.FC<SkillGapsRoadmapProps> = ({ skillGaps }) => {
  const [selectedGap, setSelectedGap] = useState<SkillGap | null>(null);
  const [filterPriority, setFilterPriority] = useState<string>('all');

  // Priority colors
  const priorityConfig: Record<string, { bg: string; border: string; text: string; icon: string }> = {
    Critical: {
      bg: 'bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/30 dark:to-red-800/30',
      border: 'border-red-300 dark:border-red-600',
      text: 'text-red-700 dark:text-red-300',
      icon: '🚨'
    },
    High: {
      bg: 'bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/30 dark:to-orange-800/30',
      border: 'border-orange-300 dark:border-orange-600',
      text: 'text-orange-700 dark:text-orange-300',
      icon: '⚡'
    },
    Medium: {
      bg: 'bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/30',
      border: 'border-blue-300 dark:border-blue-600',
      text: 'text-blue-700 dark:text-blue-300',
      icon: '📈'
    }
  };

  const getDifficultyBadge = (difficulty: string) => {
    const config: Record<string, { bg: string; text: string }> = {
      Beginner: { bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-700 dark:text-green-300' },
      Intermediate: { bg: 'bg-yellow-100 dark:bg-yellow-900/30', text: 'text-yellow-700 dark:text-yellow-300' },
      Advanced: { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-700 dark:text-red-300' }
    };
    return config[difficulty] || config.Beginner;
  };

  const filteredGaps = filterPriority === 'all' 
    ? skillGaps 
    : skillGaps.filter(gap => gap.priority === filterPriority);

  // Group by priority
  const critical = skillGaps.filter(g => g.priority === 'Critical');
  const high = skillGaps.filter(g => g.priority === 'High');
  const medium = skillGaps.filter(g => g.priority === 'Medium');

  return (
    <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-xl p-6 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
            <span className="mr-2">🗺️</span>
            Your Learning Roadmap
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Prioritized skill gaps based on market demand and your profile
          </p>
        </div>
      </div>

      {/* Stats summary */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="p-4 rounded-xl bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/30 dark:to-red-800/30 border border-red-200 dark:border-red-700 cursor-pointer"
          onClick={() => setFilterPriority(filterPriority === 'Critical' ? 'all' : 'Critical')}
        >
          <div className="text-sm font-medium text-red-700 dark:text-red-300 mb-1">Critical</div>
          <div className="text-2xl font-bold text-red-600 dark:text-red-400">{critical.length}</div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.05 }}
          className="p-4 rounded-xl bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/30 dark:to-orange-800/30 border border-orange-200 dark:border-orange-700 cursor-pointer"
          onClick={() => setFilterPriority(filterPriority === 'High' ? 'all' : 'High')}
        >
          <div className="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">High</div>
          <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">{high.length}</div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.05 }}
          className="p-4 rounded-xl bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/30 border border-blue-200 dark:border-blue-700 cursor-pointer"
          onClick={() => setFilterPriority(filterPriority === 'Medium' ? 'all' : 'Medium')}
        >
          <div className="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Medium</div>
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{medium.length}</div>
        </motion.div>
      </div>

      {filterPriority !== 'all' && (
        <button
          onClick={() => setFilterPriority('all')}
          className="mb-4 text-sm text-blue-600 dark:text-blue-400 hover:underline"
        >
          ← Show all priorities
        </button>
      )}

      {/* Roadmap timeline */}
      <div className="space-y-4">
        {filteredGaps.map((gap, index) => {
          const config = priorityConfig[gap.priority] || priorityConfig.Medium;
          const difficultyColors = getDifficultyBadge(gap.learn_difficulty);
          const isSelected = selectedGap?.skill === gap.skill;

          return (
            <motion.div
              key={gap.skill}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="relative"
            >
              {/* Timeline connector */}
              {index < filteredGaps.length - 1 && (
                <div className="absolute left-6 top-16 w-0.5 h-full bg-gradient-to-b from-gray-300 to-transparent dark:from-gray-600" />
              )}

              <button
                onClick={() => setSelectedGap(isSelected ? null : gap)}
                className={`w-full text-left p-5 rounded-xl border-2 transition-all hover:shadow-lg ${
                  isSelected 
                    ? `${config.border} ${config.bg}` 
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
              >
                <div className="flex items-start space-x-4">
                  {/* Priority icon */}
                  <motion.div
                    className={`flex-shrink-0 w-12 h-12 rounded-full ${config.bg} border-2 ${config.border} flex items-center justify-center text-2xl`}
                    whileHover={{ scale: 1.2, rotate: 360 }}
                    transition={{ type: 'spring', stiffness: 300 }}
                  >
                    {config.icon}
                  </motion.div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="text-lg font-bold text-gray-900 dark:text-white">
                        {gap.skill}
                      </h4>
                      <svg
                        className={`w-5 h-5 transition-transform ${isSelected ? 'rotate-180' : ''} text-gray-400 flex-shrink-0 ml-2`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 9l-7 7-7-7"
                        />
                      </svg>
                    </div>

                    <div className="flex flex-wrap gap-2 mb-2">
                      <span className={`px-2 py-1 rounded-lg text-xs font-semibold ${config.text} ${config.bg} border ${config.border}`}>
                        {gap.priority} Priority
                      </span>
                      <span className={`px-2 py-1 rounded-lg text-xs font-semibold ${difficultyColors.text} ${difficultyColors.bg}`}>
                        {gap.learn_difficulty}
                      </span>
                      <span className="px-2 py-1 rounded-lg text-xs font-semibold text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700">
                        ⏱️ {gap.estimated_learning_time}
                      </span>
                      <span className="px-2 py-1 rounded-lg text-xs font-semibold text-gold-accent dark:text-purple-300 bg-silver-light dark:bg-royal-navy/30">
                        📊 {gap.market_demand} Demand
                      </span>
                    </div>

                    {!isSelected && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                        {gap.why_important}
                      </p>
                    )}
                  </div>
                </div>

                {/* Expanded content */}
                {isSelected && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600 space-y-3"
                  >
                    <div>
                      <h5 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                        🎯 Why This Matters
                      </h5>
                      <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                        {gap.why_important}
                      </p>
                    </div>

                    <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50">
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Recommendation Confidence
                      </span>
                      <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
                        {Math.round(gap.confidence_score * 100)}%
                      </span>
                    </div>
                  </motion.div>
                )}
              </button>
            </motion.div>
          );
        })}
      </div>

      {/* Action CTA */}
      <div className="mt-6 p-5 rounded-xl bg-gradient-to-r from-green-50 via-blue-50 to-silver-soft dark:from-green-900/20 dark:via-blue-900/20 dark:to-royal-navy/20 border-2 border-green-300 dark:border-green-700">
        <div className="flex items-start space-x-4">
          <span className="text-3xl flex-shrink-0">🎓</span>
          <div className="flex-1">
            <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-2">
              Ready to Level Up?
            </h4>
            <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed mb-3">
              We recommend starting with <span className="font-bold text-red-600 dark:text-red-400">Critical</span> priority 
              skills. These will have the biggest impact on your career opportunities. Check out personalized 
              training recommendations below!
            </p>
            <button className="px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-gold-primary text-white font-semibold hover:shadow-lg transition-all hover:scale-105">
              View Training Courses →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SkillGapsRoadmap;

'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface SkillCluster {
  category: string;
  skills: string[];
  color: string;
}

interface SkillClustersCardProps {
  skillClusters: SkillCluster[];
}

const SkillClustersCard: React.FC<SkillClustersCardProps> = ({ skillClusters }) => {
  const [expandedCluster, setExpandedCluster] = useState<string | null>(null);

  // Color mapping for categories
  const colorClasses: Record<string, { bg: string; border: string; text: string; badge: string }> = {
    'Technical Skills': {
      bg: 'bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/30',
      border: 'border-blue-300 dark:border-blue-600',
      text: 'text-blue-700 dark:text-blue-300',
      badge: 'bg-blue-500 text-white'
    },
    'Business Skills': {
      bg: 'bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/30 dark:to-green-800/30',
      border: 'border-green-300 dark:border-green-600',
      text: 'text-green-700 dark:text-green-300',
      badge: 'bg-green-500 text-white'
    },
    'Soft Skills': {
      bg: 'bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/30 dark:to-purple-800/30',
      border: 'border-purple-300 dark:border-purple-600',
      text: 'text-purple-700 dark:text-purple-300',
      badge: 'bg-purple-500 text-white'
    },
    'Domain Expertise': {
      bg: 'bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/30 dark:to-orange-800/30',
      border: 'border-orange-300 dark:border-orange-600',
      text: 'text-orange-700 dark:text-orange-300',
      badge: 'bg-orange-500 text-white'
    }
  };

  const getColors = (category: string) => {
    return colorClasses[category] || colorClasses['Technical Skills'];
  };

  const toggleCluster = (category: string) => {
    setExpandedCluster(expandedCluster === category ? null : category);
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-xl p-6 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
          <span className="mr-2">🎯</span>
          Your Skill Clusters
        </h3>
        <div className="text-sm text-gray-500 dark:text-gray-400 font-medium">
          {skillClusters.length} Categories
        </div>
      </div>

      <div className="space-y-4">
        {skillClusters.map((cluster, index) => {
          const colors = getColors(cluster.category);
          const isExpanded = expandedCluster === cluster.category;

          return (
            <motion.div
              key={cluster.category}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`rounded-xl border-2 ${colors.border} ${colors.bg} overflow-hidden`}
            >
              <button
                onClick={() => toggleCluster(cluster.category)}
                className="w-full p-4 flex items-center justify-between hover:opacity-80 transition-opacity"
              >
                <div className="flex items-center space-x-3">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${colors.badge}`}>
                    {cluster.skills.length}
                  </span>
                  <span className={`text-lg font-semibold ${colors.text}`}>
                    {cluster.category}
                  </span>
                </div>
                
                <motion.svg
                  className={`w-6 h-6 ${colors.text}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  animate={{ rotate: isExpanded ? 180 : 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 9l-7 7-7-7"
                  />
                </motion.svg>
              </button>

              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3, ease: 'easeInOut' }}
                    className="overflow-hidden"
                  >
                    <div className="px-4 pb-4 pt-2">
                      <div className="flex flex-wrap gap-2">
                        {cluster.skills.map((skill, skillIndex) => (
                          <motion.span
                            key={skill}
                            initial={{ scale: 0, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            transition={{ 
                              delay: skillIndex * 0.05,
                              type: 'spring',
                              stiffness: 200
                            }}
                            className={`px-3 py-1.5 rounded-lg ${colors.text} bg-white dark:bg-gray-800 border ${colors.border} text-sm font-medium shadow-sm hover:shadow-md transition-shadow cursor-default`}
                          >
                            {skill}
                          </motion.span>
                        ))}
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </div>

      <div className="mt-6 p-4 rounded-xl bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600">
        <div className="flex items-start space-x-3">
          <svg 
            className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
            />
          </svg>
          <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
            <span className="font-semibold">Pro Tip:</span> Click each category to see your organized skills. 
            These clusters help you understand your skill distribution and identify areas of strength.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SkillClustersCard;

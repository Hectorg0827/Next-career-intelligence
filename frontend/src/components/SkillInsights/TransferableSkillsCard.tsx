'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';

interface AdjacentSkill {
  skill: string;
  confidence: number;
  reasoning: string;
  source_skills: string[];
}

interface TransferableSkillsCardProps {
  transferableSkills: AdjacentSkill[];
}

const TransferableSkillsCard: React.FC<TransferableSkillsCardProps> = ({ 
  transferableSkills 
}) => {
  const [selectedSkill, setSelectedSkill] = useState<AdjacentSkill | null>(null);

  // Show top 5 skills by default
  const topSkills = transferableSkills.slice(0, 5);

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return { bg: 'bg-green-500', text: 'text-green-600', border: 'border-green-300' };
    if (confidence >= 0.6) return { bg: 'bg-blue-500', text: 'text-blue-600', border: 'border-blue-300' };
    if (confidence >= 0.4) return { bg: 'bg-yellow-500', text: 'text-yellow-600', border: 'border-yellow-300' };
    return { bg: 'bg-gray-500', text: 'text-gray-600', border: 'border-gray-300' };
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-xl p-6 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
          <span className="mr-2">🚀</span>
          Transferable Skills
        </h3>
        <div className="text-sm text-gray-500 dark:text-gray-400 font-medium">
          Top {topSkills.length} Matches
        </div>
      </div>

      <p className="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
        Based on your current skills, these adjacent skills are within reach. Click to see why!
      </p>

      <div className="space-y-4">
        {topSkills.map((skill, index) => {
          const colors = getConfidenceColor(skill.confidence);
          const isSelected = selectedSkill?.skill === skill.skill;

          return (
            <motion.div
              key={skill.skill}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="group"
            >
              <button
                onClick={() => setSelectedSkill(isSelected ? null : skill)}
                className={`w-full text-left p-4 rounded-xl border-2 transition-all hover:shadow-lg ${
                  isSelected 
                    ? `${colors.border} bg-gradient-to-r from-blue-50 to-silver-soft dark:from-blue-900/20 dark:to-royal-navy/20` 
                    : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-lg font-semibold text-gray-900 dark:text-white">
                    {skill.skill}
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className={`text-sm font-bold ${colors.text}`}>
                      {Math.round(skill.confidence * 100)}%
                    </span>
                    <svg
                      className={`w-5 h-5 transition-transform ${isSelected ? 'rotate-180' : ''} text-gray-400`}
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
                </div>

                {/* Confidence bar */}
                <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <motion.div
                    className={`h-full ${colors.bg}`}
                    initial={{ width: 0 }}
                    animate={{ width: `${skill.confidence * 100}%` }}
                    transition={{ duration: 0.8, delay: index * 0.1 + 0.3 }}
                  />
                </div>

                {/* Expanded details */}
                {isSelected && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                    className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-600 space-y-3"
                  >
                    <div>
                      <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                        💡 Why This Skill?
                      </h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                        {skill.reasoning}
                      </p>
                    </div>

                    {skill.source_skills.length > 0 && (
                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                          🔗 Built From Your Skills:
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {skill.source_skills.map((sourceSkill) => (
                            <span
                              key={sourceSkill}
                              className="px-2 py-1 text-xs font-medium rounded-lg bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-700"
                            >
                              {sourceSkill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}
              </button>
            </motion.div>
          );
        })}
      </div>

      {transferableSkills.length > 5 && (
        <div className="mt-4 text-center">
          <button className="text-sm text-blue-600 dark:text-blue-400 font-medium hover:underline">
            View all {transferableSkills.length} transferable skills →
          </button>
        </div>
      )}

      <div className="mt-6 p-4 rounded-xl bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-700">
        <div className="flex items-start space-x-3">
          <span className="text-2xl">✨</span>
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
              Quick Win Strategy
            </h4>
            <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
              Focus on skills with 80%+ confidence first—these are your &quot;low-hanging fruit.&quot; 
              You already have the foundation to master them quickly!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TransferableSkillsCard;

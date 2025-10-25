'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface HiddenSkillsBadgeProps {
  hiddenSkills: string[];
}

const HiddenSkillsBadge: React.FC<HiddenSkillsBadgeProps> = ({ hiddenSkills }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!hiddenSkills || hiddenSkills.length === 0) {
    return null;
  }

  return (
    <div className="bg-gradient-to-br from-silver-soft via-silver-soft to-orange-50 dark:from-royal-navy/20 dark:via-pink-900/20 dark:to-orange-900/20 rounded-3xl shadow-xl p-6 border-2 border-silver-soft dark:border-gold-accent">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-3xl">💎</span>
            <h3 className="text-2xl font-bold bg-gradient-to-r from-gold-primary via-gold-accent to-orange-600 bg-clip-text text-transparent">
              Hidden Skills Revealed
            </h3>
          </div>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
            Our AI detected <span className="font-bold text-gold-primary dark:text-gold-hover">{hiddenSkills.length} implicit skills</span> from your experience that you might not have listed!
          </p>
        </div>
      </div>

      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full mb-4 p-4 rounded-xl bg-white dark:bg-gray-800 border-2 border-purple-300 dark:border-gold-primary hover:shadow-lg transition-all group"
      >
        <div className="flex items-center justify-between">
          <span className="text-lg font-semibold text-gray-900 dark:text-white group-hover:text-gold-primary dark:group-hover:text-gold-hover transition-colors">
            {isExpanded ? 'Hide' : 'Reveal'} Your Hidden Skills
          </span>
          <motion.div
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.3 }}
          >
            <svg 
              className="w-6 h-6 text-gold-primary dark:text-gold-hover" 
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
          </motion.div>
        </div>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="space-y-3">
              {hiddenSkills.map((skill, index) => (
                <motion.div
                  key={skill}
                  initial={{ opacity: 0, x: -20, scale: 0.8 }}
                  animate={{ opacity: 1, x: 0, scale: 1 }}
                  transition={{ 
                    delay: index * 0.1,
                    type: 'spring',
                    stiffness: 200
                  }}
                  className="group"
                >
                  <div className="p-4 rounded-xl bg-white dark:bg-gray-800 border-2 border-silver-soft dark:border-gold-accent hover:border-gold-hover dark:hover:border-royal-blue hover:shadow-md transition-all cursor-default">
                    <div className="flex items-center space-x-3">
                      <motion.span
                        className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-royal-blue to-gold-accent flex items-center justify-center text-white font-bold text-sm"
                        whileHover={{ scale: 1.2, rotate: 360 }}
                        transition={{ type: 'spring', stiffness: 300 }}
                      >
                        {index + 1}
                      </motion.span>
                      <span className="text-base font-medium text-gray-900 dark:text-white group-hover:text-gold-primary dark:group-hover:text-gold-hover transition-colors">
                        {skill}
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            <div className="mt-6 p-4 rounded-xl bg-gradient-to-r from-silver-light to-pink-100 dark:from-royal-navy/30 dark:to-pink-900/30 border border-silver-soft dark:border-gold-accent">
              <div className="flex items-start space-x-3">
                <svg 
                  className="w-5 h-5 text-gold-primary dark:text-gold-hover flex-shrink-0 mt-0.5" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" 
                  />
                </svg>
                <div>
                  <h4 className="font-semibold text-royal-navy dark:text-silver-soft mb-1">
                    Update Your Resume
                  </h4>
                  <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                    These skills are valuable assets you already possess. Add them to your resume 
                    and LinkedIn profile to increase your visibility to recruiters!
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {!isExpanded && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex justify-center"
        >
          <motion.div
            animate={{ 
              y: [0, -10, 0],
            }}
            transition={{ 
              duration: 2,
              repeat: Infinity,
              ease: 'easeInOut'
            }}
            className="text-4xl"
          >
            ✨
          </motion.div>
        </motion.div>
      )}
    </div>
  );
};

export default HiddenSkillsBadge;

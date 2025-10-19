'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface RiskMitigation {
  automation_threats: string[];
  protective_skills: string[];
  pivot_options: string[];
  why_these_skills: string;
}

interface RiskMitigationCardProps {
  mitigation: RiskMitigation;
}

const RiskMitigationCard: React.FC<RiskMitigationCardProps> = ({ mitigation }) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-xl p-6 border border-gray-200 dark:border-gray-700 h-full">
      <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2 flex items-center">
        <span className="mr-2">🛡️</span>
        Risk Mitigation Strategy
      </h3>
      <p className="text-gray-600 dark:text-gray-400 text-sm mb-6">
        Stay ahead of automation with these protective measures
      </p>

      <div className="space-y-4">
        {/* Automation Threats */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-xl">⚠️</span>
            <h4 className="font-bold text-gray-900 dark:text-white">Automation Threats</h4>
          </div>
          <div className="space-y-2">
            {mitigation.automation_threats.map((threat, index) => (
              <div
                key={index}
                className="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 text-sm text-red-800 dark:text-red-200"
              >
                {threat}
              </div>
            ))}
          </div>
        </motion.div>

        {/* Protective Skills */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-xl">🎯</span>
            <h4 className="font-bold text-gray-900 dark:text-white">Protective Skills</h4>
          </div>
          <div className="flex flex-wrap gap-2">
            {mitigation.protective_skills.map((skill, index) => (
              <motion.span
                key={skill}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.3 + index * 0.05 }}
                className="px-3 py-1.5 rounded-lg bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-sm font-medium border border-green-200 dark:border-green-700"
              >
                {skill}
              </motion.span>
            ))}
          </div>
        </motion.div>

        {/* Pivot Options */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-xl">🔀</span>
            <h4 className="font-bold text-gray-900 dark:text-white">Pivot Options</h4>
          </div>
          <div className="space-y-2">
            {mitigation.pivot_options.map((option, index) => (
              <div
                key={index}
                className="p-3 rounded-lg bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-700 text-sm text-purple-800 dark:text-purple-200 flex items-start space-x-2"
              >
                <span className="text-purple-600 dark:text-purple-400 mt-0.5">→</span>
                <span>{option}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Why These Skills */}
        <div className="p-4 rounded-xl bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border border-blue-200 dark:border-blue-700">
          <div className="flex items-start space-x-3">
            <svg className="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <div>
              <h4 className="font-bold text-blue-900 dark:text-blue-100 mb-1">Why Focus on These?</h4>
              <p className="text-sm text-blue-800 dark:text-blue-200 leading-relaxed">
                {mitigation.why_these_skills}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskMitigationCard;

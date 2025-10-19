'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface ImmediateSteps {
  month_1_3: string[];
  month_4_6: string[];
  month_7_12: string[];
  why_start_here: string;
}

interface ImmediateStepsCardProps {
  steps: ImmediateSteps;
}

const ImmediateStepsCard: React.FC<ImmediateStepsCardProps> = ({ steps }) => {
  const phases = [
    { key: 'month_1_3', label: 'Months 1-3', icon: '🏃', color: 'from-green-500 to-emerald-600', actions: steps.month_1_3 },
    { key: 'month_4_6', label: 'Months 4-6', icon: '🚴', color: 'from-blue-500 to-cyan-600', actions: steps.month_4_6 },
    { key: 'month_7_12', label: 'Months 7-12', icon: '🚀', color: 'from-purple-500 to-pink-600', actions: steps.month_7_12 }
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-xl p-6 border border-gray-200 dark:border-gray-700 h-full">
      <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2 flex items-center">
        <span className="mr-2">⏱️</span>
        Your First Year Action Plan
      </h3>
      <p className="text-gray-600 dark:text-gray-400 text-sm mb-6">
        Start building your future today with these concrete steps
      </p>

      <div className="space-y-4 mb-6">
        {phases.map((phase, phaseIndex) => (
          <motion.div
            key={phase.key}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: phaseIndex * 0.1 }}
            className="relative"
          >
            <div className={`p-4 rounded-xl bg-gradient-to-r ${phase.color} text-white`}>
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-2xl">{phase.icon}</span>
                <span className="font-bold text-lg">{phase.label}</span>
              </div>
            </div>
            <div className="mt-2 space-y-2">
              {phase.actions.map((action, actionIndex) => (
                <motion.div
                  key={actionIndex}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: phaseIndex * 0.1 + actionIndex * 0.05 + 0.2 }}
                  className="flex items-start space-x-2 p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50"
                >
                  <svg className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm text-gray-700 dark:text-gray-300">{action}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        ))}
      </div>

      <div className="p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700">
        <div className="flex items-start space-x-3">
          <svg className="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h4 className="font-bold text-blue-900 dark:text-blue-100 mb-1">Why Start Here?</h4>
            <p className="text-sm text-blue-800 dark:text-blue-200 leading-relaxed">
              {steps.why_start_here}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImmediateStepsCard;

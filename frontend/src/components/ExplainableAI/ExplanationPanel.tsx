'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ExplanationPanelProps {
  title?: string;
  explanation: string;
  variant?: 'inline' | 'button' | 'accordion';
  icon?: string;
  size?: 'sm' | 'md' | 'lg';
}

/**
 * FEATURE 3: Explainable AI Component
 * 
 * Reusable component that adds "Why?" explanations to any recommendation.
 * Use this component anywhere you want to provide AI reasoning transparency.
 * 
 * Usage:
 * <ExplanationPanel 
 *   explanation="This skill is recommended because..."
 *   variant="button"
 * />
 */
const ExplanationPanel: React.FC<ExplanationPanelProps> = ({ 
  title = "Why this recommendation?",
  explanation,
  variant = 'button',
  icon = '💡',
  size = 'md'
}) => {
  const [isExpanded, setIsExpanded] = useState(variant === 'inline');

  const sizeClasses = {
    sm: 'text-xs p-2',
    md: 'text-sm p-3',
    lg: 'text-base p-4'
  };

  const buttonSizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base'
  };

  // Inline variant - always visible, no toggle
  if (variant === 'inline') {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`rounded-xl bg-gradient-to-r from-blue-50 to-silver-soft dark:from-blue-900/20 dark:to-royal-navy/20 border-2 border-blue-200 dark:border-blue-700 ${sizeClasses[size]}`}
      >
        <div className="flex items-start space-x-3">
          <span className="text-2xl flex-shrink-0">{icon}</span>
          <div className="flex-1">
            <h4 className="font-bold text-blue-900 dark:text-blue-100 mb-1">
              {title}
            </h4>
            <p className="text-blue-800 dark:text-blue-200 leading-relaxed">
              {explanation}
            </p>
          </div>
        </div>
      </motion.div>
    );
  }

  // Button variant - compact button that expands
  if (variant === 'button') {
    return (
      <div>
        <motion.button
          onClick={() => setIsExpanded(!isExpanded)}
          className={`rounded-lg font-semibold bg-gradient-to-r from-blue-500 to-gold-primary text-white hover:shadow-lg transition-all flex items-center space-x-2 ${buttonSizeClasses[size]}`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <span>{icon}</span>
          <span>Why?</span>
        </motion.button>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ opacity: 0, height: 0, marginTop: 0 }}
              animate={{ opacity: 1, height: 'auto', marginTop: 12 }}
              exit={{ opacity: 0, height: 0, marginTop: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <div className={`rounded-xl bg-gradient-to-r from-blue-50 to-silver-soft dark:from-blue-900/20 dark:to-royal-navy/20 border-2 border-blue-200 dark:border-blue-700 ${sizeClasses[size]}`}>
                <div className="flex items-start space-x-3">
                  <svg className="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div className="flex-1">
                    <h4 className="font-bold text-blue-900 dark:text-blue-100 mb-1">
                      {title}
                    </h4>
                    <p className="text-blue-800 dark:text-blue-200 leading-relaxed">
                      {explanation}
                    </p>
                  </div>
                  <button
                    onClick={() => setIsExpanded(false)}
                    className="flex-shrink-0 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  }

  // Accordion variant - full-width expandable section
  return (
    <div className="rounded-xl border-2 border-blue-200 dark:border-blue-700 overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 flex items-center justify-between bg-gradient-to-r from-blue-50 to-silver-soft dark:from-blue-900/20 dark:to-royal-navy/20 hover:from-blue-100 hover:to-silver-light dark:hover:from-blue-800/30 dark:hover:to-purple-800/30 transition-colors"
      >
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{icon}</span>
          <span className="font-bold text-blue-900 dark:text-blue-100">{title}</span>
        </div>
        <motion.svg
          className="w-6 h-6 text-blue-600 dark:text-blue-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.3 }}
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </motion.svg>
      </button>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className={`bg-white dark:bg-gray-800 border-t-2 border-blue-200 dark:border-blue-700 ${sizeClasses[size]}`}>
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                {explanation}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ExplanationPanel;

// Helper component for quick "Why?" icons next to text
interface WhyIconProps {
  explanation: string;
  size?: 'sm' | 'md' | 'lg';
}

export const WhyIcon: React.FC<WhyIconProps> = ({ explanation, size = 'sm' }) => {
  const [showTooltip, setShowTooltip] = useState(false);

  const iconSizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  };

  return (
    <div className="relative inline-block">
      <button
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onClick={() => setShowTooltip(!showTooltip)}
        className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 transition-colors"
      >
        <svg className={iconSizes[size]} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </button>

      <AnimatePresence>
        {showTooltip && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-64"
          >
            <div className="bg-gray-900 dark:bg-gray-700 text-white text-xs rounded-lg p-3 shadow-xl">
              <div className="font-semibold mb-1">💡 Why?</div>
              <p className="leading-relaxed">{explanation}</p>
              <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/2 rotate-45 w-2 h-2 bg-gray-900 dark:bg-gray-700" />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

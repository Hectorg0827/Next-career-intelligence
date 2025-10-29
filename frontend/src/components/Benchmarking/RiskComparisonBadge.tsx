'use client';

import React from 'react';
import { motion } from 'framer-motion';

/**
 * FEATURE 6: Benchmarking Dashboard - Risk Comparison
 * 
 * Shows user's automation risk compared to industry average
 */

interface RiskComparisonProps {
  yourScore: number;
  industryAverage: number;
  percentile: number;
  comparisonText: string;
  trend: 'improving' | 'declining' | 'stable';
}

export default function RiskComparisonBadge({
  yourScore,
  industryAverage,
  percentile,
  comparisonText,
  trend
}: RiskComparisonProps) {
  const getTrendIcon = () => {
    if (trend === 'improving') return '📈';
    if (trend === 'declining') return '📉';
    return '➡️';
  };

  const getTrendColor = () => {
    if (trend === 'improving') return 'text-green-600';
    if (trend === 'declining') return 'text-red-600';
    return 'text-gray-600';
  };

  const getScoreColor = (score: number) => {
    if (score < 40) return 'text-green-600';
    if (score < 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getPercentileMessage = () => {
    if (percentile >= 75) return '🎯 Lower risk than most peers!';
    if (percentile >= 50) return '✓ About average risk level';
    if (percentile >= 25) return '⚠️ Higher risk than average';
    return '🚨 Significantly higher risk';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 border-2 border-blue-200 shadow-lg bg-gradient-to-br from-white to-blue-50 rounded-2xl"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-gray-900">
          🎯 Risk Comparison
        </h3>
        <span className={`text-2xl ${getTrendColor()}`}>
          {getTrendIcon()}
        </span>
      </div>

      {/* Main comparison */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        {/* Your score */}
        <div className="text-center">
          <p className="mb-2 text-sm text-gray-600">Your Risk Score</p>
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', delay: 0.2 }}
            className={`text-5xl font-bold ${getScoreColor(yourScore)}`}
          >
            {yourScore}%
          </motion.div>
        </div>

        {/* Industry average */}
        <div className="text-center">
          <p className="mb-2 text-sm text-gray-600">Industry Average</p>
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', delay: 0.3 }}
            className="text-5xl font-bold text-gray-700"
          >
            {industryAverage}%
          </motion.div>
        </div>
      </div>

      {/* Comparison bar */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2 text-xs text-gray-600">
          <span>Lower Risk</span>
          <span>Higher Risk</span>
        </div>
        <div className="relative h-8 overflow-hidden rounded-full bg-gradient-to-r from-green-200 via-yellow-200 to-red-200">
          {/* Industry average marker */}
          <div
            className="absolute top-0 bottom-0 w-1 bg-gray-600 opacity-50"
            style={{ left: `${industryAverage}%` }}
          />
          
          {/* Your score indicator */}
          <motion.div
            initial={{ left: 0 }}
            animate={{ left: `${yourScore}%` }}
            transition={{ duration: 1, ease: 'easeOut' }}
            className="absolute top-0 bottom-0 flex items-center"
            style={{ transform: 'translateX(-50%)' }}
          >
            <div className="w-6 h-6 bg-blue-600 border-4 border-white rounded-full shadow-lg" />
          </motion.div>
        </div>
        <div className="flex items-center justify-center mt-2">
          <span className="text-xs text-gray-500">
            <span className="inline-block w-3 h-3 mr-1 bg-gray-600 opacity-50"></span>
            Industry Average ({industryAverage}%)
          </span>
        </div>
      </div>

      {/* Percentile info */}
      <div className="p-4 mb-4 bg-blue-100 border border-blue-300 rounded-xl">
        <p className="mb-1 text-sm font-semibold text-blue-900">
          {getPercentileMessage()}
        </p>
        <p className="text-xs text-blue-700">
          You&apos;re in the {percentile}th percentile - {comparisonText}
        </p>
      </div>

      {/* Trend explanation */}
      <div className="text-center">
        <p className="text-xs text-gray-600">
          <strong className={getTrendColor()}>Trend:</strong>{' '}
          {trend === 'improving' && 'Your risk is decreasing over time 🎉'}
          {trend === 'declining' && 'Risk increasing - time to adapt ⚡'}
          {trend === 'stable' && 'Risk level holding steady 📊'}
        </p>
      </div>
    </motion.div>
  );
}

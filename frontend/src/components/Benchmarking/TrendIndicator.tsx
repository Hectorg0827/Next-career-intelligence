'use client';

import React from 'react';
import { motion } from 'framer-motion';

/**
 * FEATURE 6: Benchmarking Dashboard - Market Trends
 * 
 * Shows current market trends for the role
 */

interface MarketTrendsProps {
  roleGrowth: string;
  hiringDifficulty: 'high' | 'medium' | 'low';
  remoteAvailability: string;
  topHiringIndustries: string[];
  careerPace: string;
  typicalYearsToNextLevel: number;
  readinessScore: number;
}

export default function TrendIndicator({
  roleGrowth,
  hiringDifficulty,
  remoteAvailability,
  topHiringIndustries,
  careerPace,
  typicalYearsToNextLevel,
  readinessScore
}: MarketTrendsProps) {
  const getDifficultyColor = () => {
    if (hiringDifficulty === 'high') return 'text-green-600 bg-green-100';
    if (hiringDifficulty === 'medium') return 'text-yellow-600 bg-yellow-100';
    return 'text-gray-600 bg-gray-100';
  };

  const getPaceColor = () => {
    if (careerPace.includes('faster')) return 'text-green-600';
    if (careerPace.includes('slower')) return 'text-red-600';
    return 'text-blue-600';
  };

  const getReadinessColor = () => {
    if (readinessScore >= 80) return 'from-green-500 to-emerald-600';
    if (readinessScore >= 60) return 'from-blue-500 to-indigo-600';
    if (readinessScore >= 40) return 'from-yellow-500 to-orange-600';
    return 'from-red-500 to-pink-600';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="bg-gradient-to-br from-white to-indigo-50 rounded-2xl border-2 border-indigo-200 p-6 shadow-lg"
    >
      {/* Header */}
      <h3 className="text-xl font-bold text-gray-900 mb-1 flex items-center gap-2">
        <span>📊</span>
        Market Trends
      </h3>
      <p className="text-sm text-gray-600 mb-6">
        Real-time insights for your role
      </p>

      {/* Key metrics grid */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {/* Role growth */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.4, type: 'spring' }}
          className="bg-white rounded-xl p-4 border border-gray-200"
        >
          <p className="text-xs text-gray-600 mb-2">📈 Role Growth</p>
          <p className="text-2xl font-bold text-green-600">{roleGrowth}</p>
          <p className="text-xs text-gray-500 mt-1">Year-over-year</p>
        </motion.div>

        {/* Hiring difficulty */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.5, type: 'spring' }}
          className="bg-white rounded-xl p-4 border border-gray-200"
        >
          <p className="text-xs text-gray-600 mb-2">🎯 Hiring Demand</p>
          <p className={`text-xl font-bold px-3 py-1 rounded-lg inline-block ${getDifficultyColor()}`}>
            {hiringDifficulty.charAt(0).toUpperCase() + hiringDifficulty.slice(1)}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {hiringDifficulty === 'high' && 'Employers actively seeking!'}
            {hiringDifficulty === 'medium' && 'Competitive market'}
            {hiringDifficulty === 'low' && 'Less demand currently'}
          </p>
        </motion.div>

        {/* Remote availability */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.6, type: 'spring' }}
          className="bg-white rounded-xl p-4 border border-gray-200"
        >
          <p className="text-xs text-gray-600 mb-2">🏠 Remote Jobs</p>
          <p className="text-2xl font-bold text-blue-600">{remoteAvailability}</p>
          <p className="text-xs text-gray-500 mt-1">Available remotely</p>
        </motion.div>

        {/* Career progression */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.7, type: 'spring' }}
          className="bg-white rounded-xl p-4 border border-gray-200"
        >
          <p className="text-xs text-gray-600 mb-2">⏱️ Next Level</p>
          <p className="text-2xl font-bold text-purple-600">{typicalYearsToNextLevel}y</p>
          <p className={`text-xs font-semibold mt-1 ${getPaceColor()}`}>
            Your pace: {careerPace}
          </p>
        </motion.div>
      </div>

      {/* Top hiring industries */}
      <div className="mb-6">
        <h4 className="text-sm font-bold text-gray-800 mb-3">
          🏢 Top Hiring Industries
        </h4>
        <div className="flex flex-wrap gap-2">
          {topHiringIndustries.map((industry, index) => (
            <motion.span
              key={industry}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.8 + index * 0.1 }}
              className="px-3 py-2 bg-gradient-to-r from-indigo-100 to-purple-100 border border-indigo-300 text-indigo-800 text-sm font-medium rounded-lg"
            >
              {industry}
            </motion.span>
          ))}
        </div>
      </div>

      {/* Promotion readiness */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4 border border-purple-200">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-bold text-purple-900">
            🚀 Promotion Readiness
          </h4>
          <span className="text-2xl font-bold text-purple-600">
            {readinessScore}%
          </span>
        </div>
        
        {/* Readiness bar */}
        <div className="h-3 bg-white rounded-full overflow-hidden mb-2">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${readinessScore}%` }}
            transition={{ duration: 1.5, delay: 1 }}
            className={`h-full bg-gradient-to-r ${getReadinessColor()}`}
          />
        </div>
        
        <p className="text-xs text-purple-700">
          {readinessScore >= 80 && '🎉 You\'re ready for the next level!'}
          {readinessScore >= 60 && readinessScore < 80 && '💪 Almost there - keep building skills'}
          {readinessScore >= 40 && readinessScore < 60 && '📚 Focus on closing key gaps'}
          {readinessScore < 40 && '🌱 Early in your journey - steady progress ahead'}
        </p>
      </div>
    </motion.div>
  );
}

'use client';

import React from 'react';
import { motion } from 'framer-motion';

/**
 * FEATURE 6: Benchmarking Dashboard - Salary Benchmark
 * 
 * Visual chart showing where user's salary sits within industry ranges
 */

interface SalaryBenchmarkProps {
  yourEstimatedRange: string;
  industryMedian: string;
  percentile25: string;
  percentile50: string;
  percentile75: string;
  percentile90: string;
  yourPosition: string;
}

export default function BenchmarkChart({
  yourEstimatedRange,
  industryMedian,
  percentile25,
  percentile50,
  percentile75,
  percentile90,
  yourPosition
}: SalaryBenchmarkProps) {
  // Parse salary strings to numbers
  const parseNumber = (str: string) => {
    return parseInt(str.replace(/[$,]/g, ''));
  };

  const p25 = parseNumber(percentile25);
  const p50 = parseNumber(percentile50);
  const p75 = parseNumber(percentile75);
  const p90 = parseNumber(percentile90);
  
  const yourMin = parseNumber(yourEstimatedRange.split('-')[0]);
  const yourMax = parseNumber(yourEstimatedRange.split('-')[1]);
  const yourMid = (yourMin + yourMax) / 2;

  const maxSalary = p90 * 1.1; // Add 10% padding
  const minSalary = p25 * 0.9;

  const getPosition = (value: number) => {
    return ((value - minSalary) / (maxSalary - minSalary)) * 100;
  };

  const getPositionColor = () => {
    if (yourPosition.includes('above')) return 'text-green-600';
    if (yourPosition.includes('below')) return 'text-red-600';
    return 'text-blue-600';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="bg-gradient-to-br from-white to-green-50 rounded-2xl border-2 border-green-200 p-6 shadow-lg"
    >
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-xl font-bold text-gray-900 mb-2">
          💰 Salary Benchmark
        </h3>
        <p className="text-sm text-gray-600">
          See where you stand in the market
        </p>
      </div>

      {/* Main chart */}
      <div className="relative h-64 mb-6">
        {/* Percentile bars */}
        <div className="absolute inset-0 flex items-end justify-around px-4">
          {[
            { label: '25th', value: p25, color: 'bg-gray-300' },
            { label: '50th', value: p50, color: 'bg-blue-400' },
            { label: '75th', value: p75, color: 'bg-green-400' },
            { label: '90th', value: p90, color: 'bg-purple-400' }
          ].map((item, index) => {
            const height = getPosition(item.value);
            return (
              <motion.div
                key={item.label}
                initial={{ height: 0 }}
                animate={{ height: `${height}%` }}
                transition={{ delay: 0.2 + index * 0.1, duration: 0.6 }}
                className="flex flex-col items-center w-16"
              >
                <div className="text-xs font-bold text-gray-700 mb-2">
                  ${(item.value / 1000).toFixed(0)}k
                </div>
                <div className={`w-full ${item.color} rounded-t-lg shadow-md`} />
                <div className="text-xs font-medium text-gray-600 mt-2">
                  {item.label}
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Your position indicator */}
        <motion.div
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.8, type: 'spring' }}
          className="absolute left-4 right-4 flex items-center"
          style={{ bottom: `${getPosition(yourMid)}%` }}
        >
          <div className="flex-1 border-t-4 border-dashed border-red-500" />
          <div className="px-3 py-1 bg-red-500 text-white text-xs font-bold rounded-full shadow-lg whitespace-nowrap">
            You: ${(yourMid / 1000).toFixed(0)}k
          </div>
          <div className="flex-1 border-t-4 border-dashed border-red-500" />
        </motion.div>
      </div>

      {/* Detailed breakdown */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-white rounded-lg p-3 border border-gray-200">
          <p className="text-xs text-gray-600 mb-1">Your Range</p>
          <p className="text-sm font-bold text-gray-900">{yourEstimatedRange}</p>
        </div>
        <div className="bg-white rounded-lg p-3 border border-gray-200">
          <p className="text-xs text-gray-600 mb-1">Industry Median</p>
          <p className="text-sm font-bold text-blue-600">{industryMedian}</p>
        </div>
      </div>

      {/* Position summary */}
      <div className={`rounded-xl p-4 ${
        yourPosition.includes('above') ? 'bg-green-100 border border-green-300' :
        yourPosition.includes('below') ? 'bg-red-100 border border-red-300' :
        'bg-blue-100 border border-blue-300'
      }`}>
        <p className={`text-sm font-bold ${getPositionColor()} mb-1`}>
          📊 Market Position: {yourPosition.charAt(0).toUpperCase() + yourPosition.slice(1)}
        </p>
        <p className="text-xs text-gray-700">
          {yourPosition.includes('above') && 'You\'re earning more than the typical market rate - great job! 🎉'}
          {yourPosition.includes('below') && 'There\'s room to negotiate higher compensation based on market rates 💪'}
          {yourPosition.includes('at') && 'You\'re right at the market median - competitive positioning ✓'}
        </p>
      </div>
    </motion.div>
  );
}

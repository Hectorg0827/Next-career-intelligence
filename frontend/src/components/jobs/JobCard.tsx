'use client';

import React from 'react';
import Link from 'next/link';
import { JobMatch, getAIRiskBadge } from '@/types/jobs';

interface JobCardProps {
  job: JobMatch;
  onApply?: (jobId: string) => void;
  showDetails?: boolean;
}

export default function JobCard({ job, onApply, showDetails = false }: JobCardProps) {
  const riskBadge = getAIRiskBadge(job.ai_displacement_risk);

  // Format salary
  const formatSalary = () => {
    if (!job.salary_min && !job.salary_max) return null;
    const currency = job.salary_currency || 'USD';
    const formatter = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      maximumFractionDigits: 0,
    });

    if (job.salary_min && job.salary_max) {
      return `${formatter.format(job.salary_min)} - ${formatter.format(job.salary_max)}`;
    } else if (job.salary_min) {
      return `From ${formatter.format(job.salary_min)}`;
    } else if (job.salary_max) {
      return `Up to ${formatter.format(job.salary_max)}`;
    }
    return null;
  };

  // AI Risk Badge Colors
  const getRiskColorClasses = () => {
    switch (riskBadge.level) {
      case 'very-low':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'very-high':
        return 'bg-red-100 text-red-800 border-red-200';
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <Link
            href={`/jobs/${job.id}`}
            className="text-xl font-semibold text-gray-900 hover:text-blue-600 transition-colors"
          >
            {job.title}
          </Link>
          <p className="text-gray-600 mt-1">{job.company}</p>
        </div>

        {/* Match Score Badge */}
        <div className="ml-4 flex flex-col items-end gap-2">
          <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold">
            {job.match_score.toFixed(0)}% Match ⭐
          </div>

          {/* AI Displacement Risk Badge */}
          <div className={`px-3 py-1 rounded-full text-xs font-medium border ${getRiskColorClasses()}`}>
            🤖 {riskBadge.percentage.toFixed(0)}% Risk
          </div>
        </div>
      </div>

      {/* Location & Type */}
      <div className="flex flex-wrap gap-3 mb-4 text-sm text-gray-600">
        <div className="flex items-center gap-1">
          <span>📍</span>
          {job.location_type === 'remote' ? (
            <span className="font-medium text-green-600">Remote</span>
          ) : (
            <span>
              {job.location_city}, {job.location_state}
              {job.distance_km !== null && job.distance_km !== undefined && (
                <span className="ml-1 text-gray-500">({job.distance_km.toFixed(1)} km)</span>
              )}
            </span>
          )}
        </div>

        <div className="flex items-center gap-1">
          <span>💼</span>
          <span className="capitalize">{job.location_type}</span>
        </div>

        {formatSalary() && (
          <div className="flex items-center gap-1">
            <span>💰</span>
            <span>{formatSalary()}</span>
          </div>
        )}

        <div className="flex items-center gap-1">
          <span>📊</span>
          <span className="capitalize">{job.seniority}</span>
        </div>
      </div>

      {/* Match Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4 p-3 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="text-xs text-gray-500">Match</div>
          <div className="text-lg font-semibold text-gray-900">{job.match_score.toFixed(0)}%</div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-500">Goals</div>
          <div className="text-lg font-semibold text-purple-600">
            {job.relevant_goals.length > 0 ? `🎯 ${job.relevant_goals.length}` : '—'}
          </div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-500">Distance</div>
          <div className="text-lg font-semibold text-gray-900">
            {job.distance_km !== null && job.distance_km !== undefined
              ? `📍 ${job.distance_km.toFixed(0)} km`
              : job.location_type === 'remote'
              ? 'Remote'
              : '—'}
          </div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-500">AI Risk</div>
          <div className={`text-lg font-semibold ${
            riskBadge.percentage < 30 ? 'text-green-600' :
            riskBadge.percentage < 50 ? 'text-yellow-600' : 'text-orange-600'
          }`}>
            🤖 {riskBadge.percentage.toFixed(0)}%
          </div>
        </div>
      </div>

      {/* Skills Match */}
      {job.match_details.match_highlights.length > 0 && (
        <div className="mb-3">
          <div className="text-sm font-medium text-gray-700 mb-2">✅ Match Highlights:</div>
          <div className="flex flex-wrap gap-2">
            {job.match_details.match_highlights.slice(0, 3).map((highlight, idx) => (
              <span key={idx} className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded border border-green-200">
                {highlight}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Skill Gaps */}
      {job.match_details.skill_gaps.length > 0 && (
        <div className="mb-3">
          <div className="text-sm font-medium text-gray-700 mb-2">⚠️ Skills to Learn:</div>
          <div className="flex flex-wrap gap-2">
            {job.match_details.skill_gaps.slice(0, 3).map((gap, idx) => (
              <span key={idx} className="text-xs bg-orange-50 text-orange-700 px-2 py-1 rounded border border-orange-200">
                {gap}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Goal Relevance */}
      {job.relevant_goals.length > 0 && (
        <div className="mb-4 p-3 bg-purple-50 border border-purple-200 rounded-lg">
          <div className="text-sm font-medium text-purple-900 mb-2">💡 Helps You Achieve:</div>
          {job.relevant_goals.slice(0, 2).map((goalInfo, idx) => (
            <div key={idx} className="text-sm text-purple-800 mb-1">
              🎯 <span className="font-medium">&quot;{goalInfo.goal_title}&quot;</span>
              {goalInfo.overlap_keywords.length > 0 && (
                <span className="text-xs text-purple-600 ml-2">
                  ({goalInfo.overlap_keywords.slice(0, 3).join(', ')})
                </span>
              )}
            </div>
          ))}
          {job.relevant_goals.length > 2 && (
            <div className="text-xs text-purple-600 mt-1">
              +{job.relevant_goals.length - 2} more goals
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <Link
          href={`/jobs/${job.id}`}
          className="flex-1 text-center py-2 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors font-medium"
        >
          View Details
        </Link>
        <button
          onClick={() => onApply?.(job.id)}
          className="flex-1 py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          Apply with Auto-Tailor 🚀
        </button>
      </div>
    </div>
  );
}

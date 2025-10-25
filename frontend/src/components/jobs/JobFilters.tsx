'use client';

import React, { useState } from 'react';
import { JobFilters as JobFiltersType } from '@/types/jobs';

interface JobFiltersProps {
  filters: JobFiltersType;
  onChange: (filters: JobFiltersType) => void;
  userGoals?: Array<{ id: string; title: string }>;
}

export default function JobFilters({ filters, onChange, userGoals = [] }: JobFiltersProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleFilterChange = (key: keyof JobFiltersType, value: any) => {
    onChange({
      ...filters,
      [key]: value,
    });
  };

  const resetFilters = () => {
    onChange({
      minSkillMatch: 30,
      maxDistance: null,
      seniority: [],
      locationType: [],
      minSalary: null,
      maxAIRisk: null,
      industries: [],
      expandSearch: false,
    });
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg">
      {/* Header */}
      <div
        className="p-4 cursor-pointer flex justify-between items-center"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <span className="text-lg font-semibold text-gray-900">🔍 Filter Jobs</span>
          {!isExpanded && (
            <span className="text-sm text-gray-500">
              ({Object.values(filters).filter(v => v !== null && v !== false && (Array.isArray(v) ? v.length > 0 : v !== 30)).length} active)
            </span>
          )}
        </div>
        <button className="text-gray-500 hover:text-gray-700">
          {isExpanded ? '▼' : '▶'}
        </button>
      </div>

      {/* Filters Panel */}
      {isExpanded && (
        <div className="border-t border-gray-200 p-4 space-y-6">
          {/* Skill Match Threshold */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Skill Match Threshold
              <span className="ml-2 text-blue-600 font-semibold">{filters.minSkillMatch}%</span>
            </label>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={filters.minSkillMatch}
              onChange={(e) => handleFilterChange('minSkillMatch', parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0% (All jobs)</span>
              <span>30% (Balanced)</span>
              <span>70% (Qualified)</span>
              <span>100% (Perfect)</span>
            </div>
            <p className="text-xs text-gray-600 mt-2">
              {filters.minSkillMatch < 20 && 'Very loose - shows many jobs including stretches'}
              {filters.minSkillMatch >= 20 && filters.minSkillMatch < 40 && 'Balanced - relevant jobs with some skill gaps'}
              {filters.minSkillMatch >= 40 && filters.minSkillMatch < 70 && 'Strict - highly qualified roles'}
              {filters.minSkillMatch >= 70 && 'Very strict - only near-perfect matches'}
            </p>
          </div>

          {/* Distance Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Distance
            </label>
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  checked={filters.maxDistance === null}
                  onChange={() => handleFilterChange('maxDistance', null)}
                  className="text-blue-600"
                />
                <span className="text-sm">Any distance</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  checked={filters.maxDistance === 25}
                  onChange={() => handleFilterChange('maxDistance', 25)}
                  className="text-blue-600"
                />
                <span className="text-sm">Within 25 km</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  checked={filters.maxDistance === 50}
                  onChange={() => handleFilterChange('maxDistance', 50)}
                  className="text-blue-600"
                />
                <span className="text-sm">Within 50 km</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  checked={filters.maxDistance === 100}
                  onChange={() => handleFilterChange('maxDistance', 100)}
                  className="text-blue-600"
                />
                <span className="text-sm">Within 100 km</span>
              </label>
            </div>
            <p className="text-xs text-gray-600 mt-2">
              💡 Remote jobs are always included
            </p>
          </div>

          {/* Seniority Level */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Seniority Level
            </label>
            <div className="space-y-2">
              {['entry', 'mid', 'senior', 'lead', 'director', 'executive'].map((level) => (
                <label key={level} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={filters.seniority.includes(level)}
                    onChange={(e) => {
                      const newSeniority = e.target.checked
                        ? [...filters.seniority, level]
                        : filters.seniority.filter(s => s !== level);
                      handleFilterChange('seniority', newSeniority);
                    }}
                    className="rounded text-blue-600"
                  />
                  <span className="text-sm capitalize">{level}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Location Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Work Location
            </label>
            <div className="space-y-2">
              {[
                { value: 'remote', label: 'Remote' },
                { value: 'hybrid', label: 'Hybrid' },
                { value: 'onsite', label: 'On-site' },
              ].map((type) => (
                <label key={type.value} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={filters.locationType.includes(type.value as any)}
                    onChange={(e) => {
                      const newTypes = e.target.checked
                        ? [...filters.locationType, type.value as any]
                        : filters.locationType.filter(t => t !== type.value);
                      handleFilterChange('locationType', newTypes);
                    }}
                    className="rounded text-blue-600"
                  />
                  <span className="text-sm">{type.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* AI Displacement Risk */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              AI Displacement Risk
            </label>
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  checked={filters.maxAIRisk === null}
                  onChange={() => handleFilterChange('maxAIRisk', null)}
                  className="text-blue-600"
                />
                <span className="text-sm">All jobs</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  checked={filters.maxAIRisk === 30}
                  onChange={() => handleFilterChange('maxAIRisk', 30)}
                  className="text-blue-600"
                />
                <span className="text-sm">Low risk only (&lt; 30%)</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  checked={filters.maxAIRisk === 50}
                  onChange={() => handleFilterChange('maxAIRisk', 50)}
                  className="text-blue-600"
                />
                <span className="text-sm">Medium risk or lower (&lt; 50%)</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  checked={filters.maxAIRisk === 70}
                  onChange={() => handleFilterChange('maxAIRisk', 70)}
                  className="text-blue-600"
                />
                <span className="text-sm">High risk or lower (&lt; 70%)</span>
              </label>
            </div>
          </div>

          {/* Goals Alignment */}
          {userGoals.length > 0 && (
            <div className="p-3 bg-silver-soft border border-silver-soft rounded-lg">
              <div className="text-sm font-medium text-royal-navy mb-2">
                🎯 Your Active Goals ({userGoals.length})
              </div>
              <div className="space-y-1">
                {userGoals.map((goal) => (
                  <div key={goal.id} className="text-sm text-gold-accent">
                    • {goal.title}
                  </div>
                ))}
              </div>
              <p className="text-xs text-gold-primary mt-2">
                Jobs are automatically scored based on goal alignment
              </p>
            </div>
          )}

          {/* Expand Search Toggle */}
          <div className="border-t border-gray-200 pt-4">
            <label className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-gray-700">🔍 Expand Search</div>
                <div className="text-xs text-gray-500 mt-1">
                  Loosen filters to see more opportunities
                </div>
              </div>
              <input
                type="checkbox"
                checked={filters.expandSearch}
                onChange={(e) => handleFilterChange('expandSearch', e.target.checked)}
                className="h-5 w-5 rounded text-blue-600"
              />
            </label>
            {filters.expandSearch && (
              <div className="mt-2 text-xs text-gray-600 bg-blue-50 border border-blue-200 rounded p-2">
                ✨ Expanded search: Skill threshold -20%, Distance ×2
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <button
              onClick={resetFilters}
              className="flex-1 py-2 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors font-medium"
            >
              Reset All
            </button>
            <button
              onClick={() => setIsExpanded(false)}
              className="flex-1 py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Apply Filters
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

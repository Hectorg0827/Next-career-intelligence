import React from 'react';

interface SearchFilterProps {
  filters: {
    query: string;
    location: string;
    remote_type: string;
    min_salary: string;
    max_salary: string;
    experience_level: string;
    skills: string;
    job_type: string;
    page: number;
    limit: number;
  };
  setFilters: (filters: any) => void;
}

export default function SearchFilter({ filters, setFilters }: SearchFilterProps) {
  const handleReset = () => {
    setFilters({
      query: '',
      location: '',
      remote_type: '',
      min_salary: '',
      max_salary: '',
      experience_level: '',
      skills: '',
      job_type: '',
      page: 1,
      limit: 20
    });
  };

  const handleChange = (field: string, value: string) => {
    setFilters({
      ...filters,
      [field]: value,
      page: 1 // Reset to first page
    });
  };

  return (
    <div className="bg-white rounded-lg p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">Filters</h2>
        {Object.values(filters).some(v => v && v !== '' && v !== 1 && v !== 20) && (
          <button
            onClick={handleReset}
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            Reset
          </button>
        )}
      </div>

      <div className="space-y-4">
        {/* Job Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Job Title
          </label>
          <input
            type="text"
            value={filters.query}
            onChange={(e) => handleChange('query', e.target.value)}
            placeholder="e.g., Python Developer"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Location */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Location
          </label>
          <input
            type="text"
            value={filters.location}
            onChange={(e) => handleChange('location', e.target.value)}
            placeholder="e.g., San Francisco, CA"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Remote Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Remote Type
          </label>
          <select
            value={filters.remote_type}
            onChange={(e) => handleChange('remote_type', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Any</option>
            <option value="remote">Remote</option>
            <option value="hybrid">Hybrid</option>
            <option value="on_site">On-site</option>
          </select>
        </div>

        {/* Job Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Job Type
          </label>
          <select
            value={filters.job_type}
            onChange={(e) => handleChange('job_type', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Any</option>
            <option value="full_time">Full-time</option>
            <option value="part_time">Part-time</option>
            <option value="contract">Contract</option>
            <option value="intern">Internship</option>
          </select>
        </div>

        {/* Experience Level */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Experience Level
          </label>
          <select
            value={filters.experience_level}
            onChange={(e) => handleChange('experience_level', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Any</option>
            <option value="entry">Entry Level</option>
            <option value="mid">Mid Level</option>
            <option value="senior">Senior</option>
            <option value="lead">Lead</option>
          </select>
        </div>

        {/* Salary Range */}
        <div className="pt-2 border-t border-gray-200">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Salary Range
          </label>
          <div className="space-y-2">
            <input
              type="number"
              value={filters.min_salary}
              onChange={(e) => handleChange('min_salary', e.target.value)}
              placeholder="Min salary"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="number"
              value={filters.max_salary}
              onChange={(e) => handleChange('max_salary', e.target.value)}
              placeholder="Max salary"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Skills */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Skills
          </label>
          <input
            type="text"
            value={filters.skills}
            onChange={(e) => handleChange('skills', e.target.value)}
            placeholder="e.g., Python, React, AWS"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p className="text-xs text-gray-500 mt-1">Comma-separated skills</p>
        </div>
      </div>
    </div>
  );
}

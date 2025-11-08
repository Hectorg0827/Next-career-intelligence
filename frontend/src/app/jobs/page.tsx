'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth-context';
import { intelligenceApi } from '@/lib/api';
import { Job, JobSearchQuery } from '@/types/jobs';
import { 
  Briefcase, 
  MapPin, 
  DollarSign, 
  Building2,
  Search,
  Filter,
  Sparkles,
  TrendingUp,
  Heart,
  ExternalLink
} from 'lucide-react';

export default function JobsPage() {
  const { user } = useAuth();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<JobSearchQuery>({
    page: 1,
    page_size: 20
  });

  useEffect(() => {
    loadJobs();
  }, [filters]);

  const loadJobs = async () => {
    try {
      setLoading(true);
      const response = await intelligenceApi.searchJobs(filters);
      setJobs(response.data);
    } catch (error) {
      console.error('Failed to load jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setFilters(prev => ({ ...prev, query: searchQuery, page: 1 }));
  };

  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return 'Competitive';
    if (min && max) return `$${(min/1000).toFixed(0)}k - $${(max/1000).toFixed(0)}k`;
    if (min) return `From $${(min/1000).toFixed(0)}k`;
    return `Up to $${(max!/1000).toFixed(0)}k`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl">
              <Briefcase className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Job Marketplace</h1>
              <p className="text-gray-600">AI-powered job matching with risk analysis</p>
            </div>
          </div>

          {/* Search Bar */}
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Search jobs by title, skills, or company..."
                className="w-full pl-12 pr-4 py-3 border rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              />
            </div>
            <button
              onClick={handleSearch}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:shadow-lg transition-all"
            >
              Search
            </button>
          </div>

          {/* Quick Filters */}
          <div className="mt-4 flex gap-2 flex-wrap">
            <button
              onClick={() => setFilters(prev => ({ ...prev, remote_only: !prev.remote_only }))}
              className={`px-4 py-2 rounded-lg border transition-all ${
                filters.remote_only 
                  ? 'bg-purple-100 border-purple-300 text-purple-700' 
                  : 'bg-white border-gray-300 text-gray-700 hover:border-purple-300'
              }`}
            >
              Remote Only
            </button>
            <button className="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:border-purple-300 transition-all">
              <Filter className="inline h-4 w-4 mr-2" />
              More Filters
            </button>
          </div>
        </div>
      </div>

      {/* Job Results */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="bg-white rounded-xl p-6 border animate-pulse">
                <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-2/3"></div>
              </div>
            ))}
          </div>
        ) : jobs.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center border">
            <Briefcase className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No jobs found</h3>
            <p className="text-gray-600 mb-6">Try adjusting your search or filters</p>
            <button
              onClick={() => {
                setSearchQuery('');
                setFilters({ page: 1, page_size: 20 });
              }}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:shadow-lg transition-all"
            >
              Clear Filters
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {jobs.map((job) => (
              <div
                key={job.id}
                className="bg-white rounded-xl p-6 border hover:shadow-lg transition-all cursor-pointer group"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 group-hover:text-purple-600 transition-colors mb-2">
                      {job.title}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span className="flex items-center gap-1">
                        <Building2 className="h-4 w-4" />
                        {job.company}
                      </span>
                      <span className="flex items-center gap-1">
                        <MapPin className="h-4 w-4" />
                        {job.location || 'Remote'}
                      </span>
                      <span className="flex items-center gap-1">
                        <DollarSign className="h-4 w-4" />
                        {formatSalary(job.salary_min, job.salary_max)}
                      </span>
                    </div>
                  </div>
                  <button className="p-2 hover:bg-purple-50 rounded-lg transition-colors">
                    <Heart className="h-5 w-5 text-gray-400 hover:text-purple-600" />
                  </button>
                </div>

                <p className="text-gray-700 mb-4 line-clamp-2">
                  {job.description}
                </p>

                {/* Skills */}
                {job.required_skills && job.required_skills.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {job.required_skills.slice(0, 6).map((skill, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-purple-50 text-purple-700 rounded-full text-sm font-medium"
                      >
                        {skill}
                      </span>
                    ))}
                    {job.required_skills.length > 6 && (
                      <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm">
                        +{job.required_skills.length - 6} more
                      </span>
                    )}
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-3 pt-4 border-t">
                  <button className="flex-1 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:shadow-lg transition-all font-medium">
                    <Sparkles className="inline h-4 w-4 mr-2" />
                    AI Match Analysis
                  </button>
                  <button className="px-4 py-2 border border-gray-300 rounded-lg hover:border-purple-300 hover:bg-purple-50 transition-all font-medium text-gray-700">
                    View Details
                    <ExternalLink className="inline h-4 w-4 ml-2" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Load More */}
        {!loading && jobs.length > 0 && (
          <div className="mt-8 text-center">
            <button
              onClick={() => setFilters(prev => ({ ...prev, page: (prev.page || 1) + 1 }))}
              className="px-6 py-3 bg-white border border-gray-300 rounded-xl hover:border-purple-300 hover:bg-purple-50 transition-all font-medium text-gray-700"
            >
              Load More Jobs
            </button>
          </div>
        )}
      </div>
    </div>
  );
}


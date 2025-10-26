'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/firebase';
import { jobsApi } from '@/lib/api';
import JobCard from '@/components/jobs/JobCard';
import SearchFilter from '@/components/jobs/SearchFilter';
import { Job, JobMatch } from '@/types/jobs';

interface PaginatedResponse {
  total: number;
  page: number;
  limit: number;
  results: Job[];
}

// Convert Job to JobMatch with default values
const convertToJobMatch = (job: Job): JobMatch => ({
  ...job,
  match_score: 0,
  ai_displacement_risk: 0,
  goal_relevance_score: 0,
  relevant_goals: [],
  match_details: {
    overall_score: 0,
    skill_fit_score: 0,
    trajectory_fit_score: 0,
    value_match_score: 0,
    logistics_fit_score: 0,
    growth_potential_score: 0,
    penalties: 0,
    match_highlights: [],
    skill_gaps: [],
    displacement_risk_improvement: 0,
    why_matched: 'Browse all available jobs'
  }
});

export default function BrowseJobsPage() {
  const { user, loading: authLoading } = useAuth();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filter state
  const [filters, setFilters] = useState({
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

  // Fetch jobs
  useEffect(() => {
    if (!user || authLoading) return;

    const fetchJobs = async () => {
      try {
        setLoading(true);
        setError(null);

        const params: Record<string, any> = {
          page: filters.page,
          limit: filters.limit
        };

        if (filters.query) params.query = filters.query;
        if (filters.location) params.location = filters.location;
        if (filters.remote_type) params.remote_type = filters.remote_type;
        if (filters.min_salary) params.min_salary = parseInt(filters.min_salary);
        if (filters.max_salary) params.max_salary = parseInt(filters.max_salary);
        if (filters.experience_level) params.experience_level = filters.experience_level;
        if (filters.skills) params.skills = filters.skills.split(',').map((s: string) => s.trim());
        if (filters.job_type) params.job_type = filters.job_type;

        const response = await jobsApi.searchJobs(params);
        setJobs(response.results);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load jobs');
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, [user, authLoading, filters]);

  if (authLoading || !user) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Browse Jobs</h1>
              <p className="text-gray-600 text-sm mt-1">Find your next opportunity</p>
            </div>
            <div className="flex gap-2">
              <Link
                href="/jobs/applications"
                className="px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
              >
                My Applications
              </Link>
              <Link
                href="/jobs/saved"
                className="px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
              >
                Saved Jobs
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-4 gap-6">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <SearchFilter filters={filters} setFilters={setFilters} />
          </div>

          {/* Jobs List */}
          <div className="lg:col-span-3">
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <p className="text-red-700">{error}</p>
              </div>
            )}

            {loading ? (
              <div className="space-y-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="bg-white rounded-lg p-6 animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                  </div>
                ))}
              </div>
            ) : jobs.length > 0 ? (
              <div className="space-y-4">
                {jobs.map((job) => (
                  <JobCard 
                    key={job.id} 
                    job={convertToJobMatch(job)} 
                  />
                ))}
              </div>
            ) : (
              <div className="bg-white rounded-lg p-12 text-center">
                <p className="text-gray-600 text-lg mb-4">No jobs found</p>
                <p className="text-gray-500 text-sm">Try adjusting your search filters</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

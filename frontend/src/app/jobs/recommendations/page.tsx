'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import JobCard from '@/components/jobs/JobCard';
import JobFilters from '@/components/jobs/JobFilters';
import { JobsMarketplaceAPI } from '@/lib/api/premiumAPI';
import { JobMatch, JobFilters as JobFiltersType, JobRecommendationsResponse } from '@/types/jobs';

export default function JobRecommendationsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<JobRecommendationsResponse | null>(null);
  const [applyingJobId, setApplyingJobId] = useState<string | null>(null);

  // Filter state
  const [filters, setFilters] = useState<JobFiltersType>({
    minSkillMatch: 30,
    maxDistance: null,
    seniority: [],
    locationType: [],
    minSalary: null,
    maxAIRisk: null,
    industries: [],
    expandSearch: false,
  });

  // Fetch recommendations
  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);

    try {
      // Get user ID from localStorage or auth
      const userId = localStorage.getItem('userId') || 'dev_user_123';

      const response = await JobsMarketplaceAPI.getRecommendations({
        user_id: userId,
        min_skill_match: filters.minSkillMatch,
        max_distance_km: filters.maxDistance,
        expand_search: filters.expandSearch,
        limit: 20,
      });

      setRecommendations(response);
    } catch (err: any) {
      console.error('Failed to fetch recommendations:', err);
      setError(err.message || 'Failed to load job recommendations');
    } finally {
      setLoading(false);
    }
  };

  // Load on mount and when filters change
  useEffect(() => {
    fetchRecommendations();
  }, [filters.minSkillMatch, filters.maxDistance, filters.expandSearch]);

  // Apply to job with auto-tailor
  const handleApply = async (jobId: string) => {
    setApplyingJobId(jobId);

    try {
      const userId = localStorage.getItem('userId') || 'dev_user_123';

      const response = await JobsMarketplaceAPI.applyToJob({
        user_id: userId,
        job_id: jobId,
        auto_tailor: true,
        auto_cover_letter: true,
      });

      // Show success and redirect to application
      alert(`✅ Application submitted! Your resume has been auto-tailored for this role.`);
      router.push(`/jobs/applications`);
    } catch (err: any) {
      console.error('Application failed:', err);
      alert(`❌ Failed to apply: ${err.message}`);
    } finally {
      setApplyingJobId(null);
    }
  };

  // Client-side filtering (additional filters beyond API)
  const getFilteredJobs = (): JobMatch[] => {
    if (!recommendations?.recommendations) return [];

    let jobs = recommendations.recommendations;

    // Filter by seniority
    if (filters.seniority.length > 0) {
      jobs = jobs.filter(job => filters.seniority.includes(job.seniority));
    }

    // Filter by location type
    if (filters.locationType.length > 0) {
      jobs = jobs.filter(job => filters.locationType.includes(job.location_type));
    }

    // Filter by AI risk
    if (filters.maxAIRisk !== null) {
      jobs = jobs.filter(job => job.ai_displacement_risk <= filters.maxAIRisk!);
    }

    return jobs;
  };

  const filteredJobs = getFilteredJobs();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">🎯 AI-Matched Job Recommendations</h1>
          <p className="text-gray-600 mt-2">
            Personalized job matches based on your skills, goals, and preferences
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <JobFilters
              filters={filters}
              onChange={setFilters}
              userGoals={recommendations?.user_goals || []}
            />

            {/* Filter Summary */}
            {recommendations && (
              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="text-sm font-medium text-blue-900 mb-2">
                  📊 Filtering Results
                </div>
                <div className="text-xs text-blue-700 space-y-1">
                  <div>• Total jobs: {recommendations.total_before_filtering}</div>
                  <div>• After API filters: {recommendations.total}</div>
                  <div>• After UI filters: {filteredJobs.length}</div>
                  <div className="pt-2 border-t border-blue-300 mt-2">
                    • Active goals: {recommendations.user_goals.length}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Jobs List */}
          <div className="lg:col-span-3">
            {/* Loading State */}
            {loading && (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600"></div>
                <p className="text-gray-600 mt-4">Loading personalized recommendations...</p>
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
                <p className="text-red-800 font-medium">❌ {error}</p>
                <button
                  onClick={fetchRecommendations}
                  className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                >
                  Try Again
                </button>
              </div>
            )}

            {/* Jobs List */}
            {!loading && !error && recommendations && (
              <>
                {/* Summary Header */}
                <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
                  <div className="flex justify-between items-center">
                    <div>
                      <h2 className="text-xl font-semibold text-gray-900">
                        Showing {filteredJobs.length} jobs
                      </h2>
                      <p className="text-sm text-gray-600 mt-1">
                        {filters.expandSearch && '🔍 Expanded search active • '}
                        Skill match ≥ {filters.minSkillMatch}%
                        {filters.maxDistance && ` • Distance ≤ ${filters.maxDistance} km`}
                      </p>
                    </div>
                    <button
                      onClick={() => fetchRecommendations()}
                      className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
                    >
                      🔄 Refresh
                    </button>
                  </div>
                </div>

                {/* Jobs */}
                {filteredJobs.length > 0 ? (
                  <div className="space-y-4">
                    {filteredJobs.map((job) => (
                      <JobCard
                        key={job.id}
                        job={job}
                        onApply={handleApply}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
                    <p className="text-xl text-gray-600 mb-4">
                      😔 No jobs match your current filters
                    </p>
                    <p className="text-gray-500 mb-6">
                      Try adjusting your filters or enabling &quot;Expand Search&quot;
                    </p>
                    <button
                      onClick={() => {
                        setFilters({
                          ...filters,
                          expandSearch: true,
                          minSkillMatch: Math.max(10, filters.minSkillMatch - 20),
                        });
                      }}
                      className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
                    >
                      🔍 Expand Search
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {/* Applying Overlay */}
      {applyingJobId && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600 mb-4"></div>
              <p className="text-lg font-medium text-gray-900">Auto-Tailoring Your Resume...</p>
              <p className="text-sm text-gray-600 mt-2">
                AI is customizing your resume to match this job
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

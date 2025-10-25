'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/firebase';
import { jobsApi } from '@/lib/api';
import JobCard from '@/components/jobs/JobCard';

interface SavedJob {
  id: string;
  job_id: string;
  saved_at: string;
  notes: string | null;
  job: {
    id: string;
    title: string;
    company: string;
    location: string;
    remote_type: string;
    salary_min: number | null;
    salary_max: number | null;
    required_skills: string[];
    experience_level: string;
    job_type: string;
    match_score?: number;
  };
}

export default function SavedJobsPage() {
  const { user, isLoading } = useAuth();
  const [savedJobs, setSavedJobs] = useState<SavedJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user || isLoading) return;

    const fetchSavedJobs = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await jobsApi.getSavedJobs();
        setSavedJobs(response.results || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load saved jobs');
      } finally {
        setLoading(false);
      }
    };

    fetchSavedJobs();
  }, [user, isLoading]);

  const handleRemoveSaved = async (savedId: string) => {
    try {
      await jobsApi.removeSavedJob(savedId);
      setSavedJobs(savedJobs.filter(s => s.id !== savedId));
    } catch (err) {
      alert('Failed to remove job');
    }
  };

  if (isLoading || !user) {
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
              <h1 className="text-3xl font-bold text-gray-900">Saved Jobs</h1>
              <p className="text-gray-600 text-sm mt-1">Jobs you've bookmarked for later</p>
            </div>
            <Link
              href="/jobs/browse"
              className="px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
            >
              Browse More
            </Link>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-3xl mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {loading ? (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="bg-white rounded-lg p-6 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-2/3"></div>
              </div>
            ))}
          </div>
        ) : savedJobs.length > 0 ? (
          <div className="space-y-4">
            {savedJobs.map((saved) => (
              <div key={saved.id} className="bg-white rounded-lg p-6 border border-gray-200">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <Link href={`/jobs/${saved.job_id}`}>
                      <h2 className="text-xl font-semibold text-gray-900 hover:text-blue-600 cursor-pointer">
                        {saved.job.title}
                      </h2>
                    </Link>
                    <p className="text-gray-600">{saved.job.company}</p>
                    <p className="text-sm text-gray-500 mt-1">
                      Saved {new Date(saved.saved_at).toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={() => handleRemoveSaved(saved.id)}
                    className="px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded transition-colors"
                  >
                    Remove
                  </button>
                </div>

                {saved.notes && (
                  <p className="text-sm text-gray-700 bg-blue-50 p-3 rounded mb-4">
                    {saved.notes}
                  </p>
                )}

                <div className="grid grid-cols-3 gap-4 text-sm mb-4">
                  <div>
                    <p className="text-gray-600">Location</p>
                    <p className="font-semibold text-gray-900">{saved.job.location}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Type</p>
                    <p className="font-semibold text-gray-900 capitalize">{saved.job.job_type}</p>
                  </div>
                  {saved.job.salary_min && saved.job.salary_max && (
                    <div>
                      <p className="text-gray-600">Salary</p>
                      <p className="font-semibold text-gray-900">
                        ${saved.job.salary_min.toLocaleString()} - ${saved.job.salary_max.toLocaleString()}
                      </p>
                    </div>
                  )}
                </div>

                <Link
                  href={`/jobs/${saved.job_id}`}
                  className="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  View Details
                </Link>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg p-12 text-center">
            <p className="text-gray-600 text-lg mb-4">No saved jobs yet</p>
            <p className="text-gray-500 text-sm mb-6">
              Browse jobs and save the ones you like for later
            </p>
            <Link
              href="/jobs/browse"
              className="inline-block px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Start Browsing
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { JobsMarketplaceAPI } from '@/lib/api/premiumAPI';
import { Job } from '@/types/jobs';
import Link from 'next/link';

export default function JobSearchPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Search filters
  const [query, setQuery] = useState(searchParams?.get('q') || '');
  const [location, setLocation] = useState(searchParams?.get('location') || '');
  const [seniority, setSeniority] = useState(searchParams?.get('seniority') || '');
  const [remoteOnly, setRemoteOnly] = useState(searchParams?.get('remote') === 'true');
  const [minSalary, setMinSalary] = useState(searchParams?.get('minSalary') || '');

  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const limit = 20;

  useEffect(() => {
    performSearch();
  }, [page]);

  const performSearch = async () => {
    try {
      setLoading(true);
      setError(null);

      const params: any = {
        limit,
        offset: (page - 1) * limit,
      };

      if (query.trim()) params.query = query.trim();
      if (location.trim()) params.location = location.trim();
      if (seniority) params.seniority = seniority;
      if (remoteOnly) params.remote_only = true;
      if (minSalary) params.min_salary = parseInt(minSalary);

      const data = await JobsMarketplaceAPI.search(params);
      setJobs(data.jobs || []);
      setTotal(data.total || 0);
    } catch (err: any) {
      setError(err.message || 'Failed to search jobs');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    performSearch();
  };

  const handleReset = () => {
    setQuery('');
    setLocation('');
    setSeniority('');
    setRemoteOnly(false);
    setMinSalary('');
    setPage(1);
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Job Search</h1>
          <p className="text-gray-600">Search from thousands of job opportunities</p>
        </div>

        {/* Search Form */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <form onSubmit={handleSearch}>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
              {/* Job Title / Keywords */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Job Title / Keywords
                </label>
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="e.g. Software Engineer"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Location */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Location
                </label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g. San Francisco, CA"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Seniority */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Seniority Level
                </label>
                <select
                  value={seniority}
                  onChange={(e) => setSeniority(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Levels</option>
                  <option value="entry">Entry Level</option>
                  <option value="mid">Mid Level</option>
                  <option value="senior">Senior Level</option>
                  <option value="lead">Lead</option>
                  <option value="director">Director</option>
                  <option value="executive">Executive</option>
                </select>
              </div>

              {/* Min Salary */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Minimum Salary (USD)
                </label>
                <input
                  type="number"
                  value={minSalary}
                  onChange={(e) => setMinSalary(e.target.value)}
                  placeholder="e.g. 80000"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Remote Only */}
              <div className="flex items-center">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={remoteOnly}
                    onChange={(e) => setRemoteOnly(e.target.checked)}
                    className="h-5 w-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm font-medium text-gray-700">
                    Remote Only
                  </span>
                </label>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-blue-600 text-white py-2 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? 'Searching...' : 'Search Jobs'}
              </button>
              <button
                type="button"
                onClick={handleReset}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
              >
                Reset
              </button>
            </div>
          </form>
        </div>

        {/* Results Header */}
        {!loading && jobs.length > 0 && (
          <div className="mb-4 flex justify-between items-center">
            <div className="text-gray-600">
              Showing {(page - 1) * limit + 1}-{Math.min(page * limit, total)} of {total} jobs
            </div>
            <Link
              href="/jobs/recommendations"
              className="text-blue-600 hover:text-blue-700 font-medium flex items-center"
            >
              <svg className="h-5 w-5 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              Try AI Recommendations
            </Link>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Searching jobs...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center text-red-800">
              <svg className="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              {error}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && jobs.length === 0 && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h3>
            <p className="text-gray-600 mb-6">
              Try adjusting your search filters or exploring AI recommendations
            </p>
            <Link
              href="/jobs/recommendations"
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700"
            >
              View AI Recommendations
            </Link>
          </div>
        )}

        {/* Job Results */}
        {!loading && jobs.length > 0 && (
          <div className="space-y-4 mb-8">
            {jobs.map((job) => (
              <JobSearchCard key={job.id} job={job} />
            ))}
          </div>
        )}

        {/* Pagination */}
        {!loading && totalPages > 1 && (
          <div className="flex justify-center items-center gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Previous
            </button>
            <span className="px-4 py-2 text-gray-700">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-4 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function JobSearchCard({ job }: { job: Job }) {
  return (
    <Link href={`/jobs/${job.id}`}>
      <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-900 mb-1">{job.title}</h3>
            <div className="text-lg text-gray-700 mb-2">{job.company}</div>

            {/* Location */}
            <div className="flex items-center text-gray-600 text-sm mb-2">
              <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              </svg>
              <span>
                {job.location_city && job.location_state
                  ? `${job.location_city}, ${job.location_state}`
                  : job.location_country || 'Remote'}
              </span>
              <span className="mx-2">•</span>
              <span className="capitalize">{job.location_type}</span>
            </div>

            {/* Salary & Seniority */}
            <div className="flex items-center text-gray-600 text-sm mb-3">
              {job.salary_min && job.salary_max && (
                <>
                  <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>
                    ${(job.salary_min / 1000).toFixed(0)}k - ${(job.salary_max / 1000).toFixed(0)}k
                  </span>
                  <span className="mx-2">•</span>
                </>
              )}
              <span className="capitalize">{job.seniority} Level</span>
            </div>

            {/* Skills */}
            {job.skills_extracted && job.skills_extracted.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {job.skills_extracted.slice(0, 5).map((skill, idx) => (
                  <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium">
                    {skill}
                  </span>
                ))}
                {job.skills_extracted.length > 5 && (
                  <span className="px-2 py-1 bg-gray-100 text-gray-500 rounded text-xs">
                    +{job.skills_extracted.length - 5} more
                  </span>
                )}
              </div>
            )}
          </div>

          {/* Status Badge */}
          <div className="ml-4">
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
              job.status === 'active' ? 'bg-green-100 text-green-800' :
              job.status === 'closed' ? 'bg-gray-100 text-gray-800' :
              'bg-blue-100 text-blue-800'
            }`}>
              {job.status === 'active' ? 'Active' : job.status === 'closed' ? 'Closed' : 'Filled'}
            </span>
          </div>
        </div>

        {/* Posted Date */}
        {job.posted_at && (
          <div className="mt-4 text-xs text-gray-500">
            Posted {new Date(job.posted_at).toLocaleDateString()}
          </div>
        )}
      </div>
    </Link>
  );
}

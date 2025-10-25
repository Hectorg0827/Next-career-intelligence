'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { JobsMarketplaceAPI } from '@/lib/api/premiumAPI';
import { JobApplication } from '@/types/jobs';
import Link from 'next/link';

const STATUS_CONFIG = {
  submitted: { label: 'Submitted', color: 'bg-blue-100 text-blue-800', icon: '📤' },
  screening: { label: 'Screening', color: 'bg-yellow-100 text-yellow-800', icon: '📋' },
  interview: { label: 'Interview', color: 'bg-silver-light text-purple-800', icon: '🎤' },
  offer: { label: 'Offer', color: 'bg-green-100 text-green-800', icon: '🎉' },
  rejected: { label: 'Rejected', color: 'bg-red-100 text-red-800', icon: '❌' },
  accepted: { label: 'Accepted', color: 'bg-green-100 text-green-800', icon: '✅' },
  withdrawn: { label: 'Withdrawn', color: 'bg-gray-100 text-gray-800', icon: '🚫' },
};

export default function ApplicationsPage() {
  const router = useRouter();
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');

  useEffect(() => {
    fetchApplications();
  }, []);

  const fetchApplications = async () => {
    try {
      setLoading(true);
      setError(null);
      const userId = localStorage.getItem('userId') || 'demo-user';
      const data = await JobsMarketplaceAPI.getMyApplications(userId);
      setApplications(data.applications || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load applications');
    } finally {
      setLoading(false);
    }
  };

  const filteredApplications = applications.filter(app =>
    filterStatus === 'all' || app.status === filterStatus
  );

  const stats = {
    total: applications.length,
    submitted: applications.filter(a => a.status === 'submitted').length,
    screening: applications.filter(a => a.status === 'screening').length,
    interview: applications.filter(a => a.status === 'interview').length,
    offer: applications.filter(a => a.status === 'offer').length,
    rejected: applications.filter(a => a.status === 'rejected').length,
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your applications...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">My Applications</h1>
              <p className="text-gray-600">Track and manage your job applications</p>
            </div>
            <div className="flex gap-3">
              <Link
                href="/jobs/search"
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
              >
                Search Jobs
              </Link>
              <Link
                href="/jobs/recommendations"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
              >
                View Recommendations
              </Link>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          <StatCard label="Total" value={stats.total} color="bg-gray-100 text-gray-800" />
          <StatCard label="Submitted" value={stats.submitted} color="bg-blue-100 text-blue-800" />
          <StatCard label="Screening" value={stats.screening} color="bg-yellow-100 text-yellow-800" />
          <StatCard label="Interview" value={stats.interview} color="bg-silver-light text-purple-800" />
          <StatCard label="Offers" value={stats.offer} color="bg-green-100 text-green-800" />
          <StatCard label="Rejected" value={stats.rejected} color="bg-red-100 text-red-800" />
        </div>

        {/* Filter Tabs */}
        <div className="bg-white rounded-lg shadow-md mb-6">
          <div className="flex overflow-x-auto border-b border-gray-200">
            <FilterTab
              label="All"
              count={applications.length}
              active={filterStatus === 'all'}
              onClick={() => setFilterStatus('all')}
            />
            <FilterTab
              label="Submitted"
              count={stats.submitted}
              active={filterStatus === 'submitted'}
              onClick={() => setFilterStatus('submitted')}
            />
            <FilterTab
              label="Screening"
              count={stats.screening}
              active={filterStatus === 'screening'}
              onClick={() => setFilterStatus('screening')}
            />
            <FilterTab
              label="Interview"
              count={stats.interview}
              active={filterStatus === 'interview'}
              onClick={() => setFilterStatus('interview')}
            />
            <FilterTab
              label="Offer"
              count={stats.offer}
              active={filterStatus === 'offer'}
              onClick={() => setFilterStatus('offer')}
            />
            <FilterTab
              label="Rejected"
              count={stats.rejected}
              active={filterStatus === 'rejected'}
              onClick={() => setFilterStatus('rejected')}
            />
          </div>
        </div>

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
        {!error && filteredApplications.length === 0 && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {filterStatus === 'all' ? 'No applications yet' : `No ${filterStatus} applications`}
            </h3>
            <p className="text-gray-600 mb-6">
              {filterStatus === 'all'
                ? 'Start applying to jobs to track your applications here'
                : 'Try viewing all applications or applying to more jobs'}
            </p>
            <Link
              href="/jobs/recommendations"
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700"
            >
              Browse AI-Matched Jobs
            </Link>
          </div>
        )}

        {/* Applications List */}
        {filteredApplications.length > 0 && (
          <div className="space-y-4">
            {filteredApplications.map((application) => (
              <ApplicationCard key={application.id} application={application} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-4">
      <div className="text-sm text-gray-600 mb-1">{label}</div>
      <div className={`text-2xl font-bold ${color.split(' ')[1]}`}>{value}</div>
    </div>
  );
}

function FilterTab({
  label,
  count,
  active,
  onClick,
}: {
  label: string;
  count: number;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-6 py-3 font-medium whitespace-nowrap border-b-2 transition-colors ${
        active
          ? 'border-blue-600 text-blue-600'
          : 'border-transparent text-gray-600 hover:text-gray-900'
      }`}
    >
      {label} ({count})
    </button>
  );
}

function ApplicationCard({ application }: { application: JobApplication }) {
  const [expanded, setExpanded] = useState(false);
  const statusConfig = STATUS_CONFIG[application.status];
  const job = application.job;

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Main Card */}
      <div className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <div className="flex items-start justify-between mb-2">
              <div>
                <h3 className="text-xl font-bold text-gray-900">
                  {job?.title || 'Job Title'}
                </h3>
                <div className="text-lg text-gray-700">{job?.company || 'Company'}</div>
              </div>
              <span className={`ml-4 px-3 py-1 rounded-full text-sm font-medium ${statusConfig.color}`}>
                {statusConfig.icon} {statusConfig.label}
              </span>
            </div>

            {/* Job Details */}
            {job && (
              <div className="flex items-center text-gray-600 text-sm mb-3">
                {job.location_city && job.location_state && (
                  <>
                    <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    </svg>
                    <span>{job.location_city}, {job.location_state}</span>
                    <span className="mx-2">•</span>
                  </>
                )}
                <span className="capitalize">{job.location_type}</span>
                {job.seniority && (
                  <>
                    <span className="mx-2">•</span>
                    <span className="capitalize">{job.seniority} Level</span>
                  </>
                )}
              </div>
            )}

            {/* Timeline */}
            <div className="text-sm text-gray-600">
              <div className="flex items-center mb-1">
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span>Applied: {new Date(application.submitted_at).toLocaleDateString()}</span>
              </div>
              {application.response_received_at && (
                <div className="flex items-center">
                  <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <span>Response: {new Date(application.response_received_at).toLocaleDateString()}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          {job && (
            <Link
              href={`/jobs/${job.id}`}
              className="flex-1 text-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              View Job Details
            </Link>
          )}
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex-1 px-4 py-2 border border-blue-600 text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition-colors"
          >
            {expanded ? 'Hide Materials' : 'View Materials'}
          </button>
        </div>

        {/* Notes */}
        {application.notes && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <div className="text-sm font-medium text-gray-700 mb-1">Notes</div>
            <div className="text-sm text-gray-600">{application.notes}</div>
          </div>
        )}
      </div>

      {/* Expanded Section */}
      {expanded && (
        <div className="border-t border-gray-200 bg-gray-50 p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Tailored Resume */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                <svg className="h-5 w-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Tailored Resume
              </h4>
              <div className="bg-white rounded-lg p-4 border border-gray-200 max-h-64 overflow-y-auto">
                <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono">
                  {application.tailored_resume_text || 'No tailored resume available'}
                </pre>
              </div>
              <button className="mt-2 text-sm text-blue-600 hover:text-blue-700 font-medium">
                Download Resume
              </button>
            </div>

            {/* Cover Letter */}
            <div>
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                <svg className="h-5 w-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                Cover Letter
              </h4>
              <div className="bg-white rounded-lg p-4 border border-gray-200 max-h-64 overflow-y-auto">
                <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono">
                  {application.cover_letter_text || 'No cover letter available'}
                </pre>
              </div>
              <button className="mt-2 text-sm text-blue-600 hover:text-blue-700 font-medium">
                Download Cover Letter
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

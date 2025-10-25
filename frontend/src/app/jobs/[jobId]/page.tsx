'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { JobsMarketplaceAPI } from '@/lib/api/premiumAPI';
import { Job, JobMatch, getAIRiskBadge } from '@/types/jobs';

export default function JobDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params?.jobId as string;

  const [job, setJob] = useState<Job | JobMatch | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [applying, setApplying] = useState(false);

  useEffect(() => {
    if (jobId) {
      fetchJobDetails();
    }
  }, [jobId]);

  const fetchJobDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await JobsMarketplaceAPI.getJob(jobId);
      setJob(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load job details');
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async () => {
    try {
      setApplying(true);
      const userId = localStorage.getItem('userId') || 'demo-user';

      const result = await JobsMarketplaceAPI.applyToJob({
        user_id: userId,
        job_id: jobId,
        auto_tailor: true,
        auto_cover_letter: true,
      });

      alert(`Applied successfully! Application ID: ${result.application_id}`);
      router.push('/jobs/applications');
    } catch (err: any) {
      alert(`Failed to apply: ${err.message}`);
    } finally {
      setApplying(false);
    }
  };

  const isJobMatch = (job: Job | JobMatch): job is JobMatch => {
    return 'match_score' in job;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading job details...</p>
        </div>
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
          <div className="text-red-600 text-center mb-4">
            <svg className="mx-auto h-12 w-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p className="font-medium">{error || 'Job not found'}</p>
          </div>
          <button
            onClick={() => router.push('/jobs')}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700"
          >
            Back to Jobs
          </button>
        </div>
      </div>
    );
  }

  const matchJob = isJobMatch(job) ? job : null;
  const aiRiskBadge = matchJob ? getAIRiskBadge(matchJob.ai_displacement_risk) : null;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <button
          onClick={() => router.back()}
          className="mb-4 flex items-center text-gray-600 hover:text-gray-900"
        >
          <svg className="h-5 w-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </button>

        {/* Header Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-start mb-4">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{job.title}</h1>
              <div className="text-xl text-gray-700 mb-2">{job.company}</div>

              {/* Location */}
              <div className="flex items-center text-gray-600 mb-2">
                <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span>
                  {job.location_city && job.location_state
                    ? `${job.location_city}, ${job.location_state}`
                    : job.location_country || 'Remote'}
                </span>
                <span className="mx-2">•</span>
                <span className="capitalize">{job.location_type}</span>
                {matchJob?.distance_km && (
                  <>
                    <span className="mx-2">•</span>
                    <span>{Math.round(matchJob.distance_km)} km away</span>
                  </>
                )}
              </div>

              {/* Salary & Seniority */}
              <div className="flex items-center text-gray-600 mb-4">
                {job.salary_min && job.salary_max && (
                  <>
                    <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>
                      ${(job.salary_min / 1000).toFixed(0)}k - ${(job.salary_max / 1000).toFixed(0)}k {job.salary_currency || 'USD'}
                    </span>
                    <span className="mx-2">•</span>
                  </>
                )}
                <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <span className="capitalize">{job.seniority} Level</span>
              </div>
            </div>

            {/* Match Score & Risk Badge */}
            {matchJob && (
              <div className="ml-4 text-right">
                <div className="inline-flex items-center bg-blue-100 text-blue-800 px-4 py-2 rounded-lg font-bold text-lg mb-2">
                  <svg className="h-5 w-5 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                  {matchJob.match_score}% Match
                </div>
                {aiRiskBadge && (
                  <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                    aiRiskBadge.color === 'green' ? 'bg-green-100 text-green-800' :
                    aiRiskBadge.color === 'blue' ? 'bg-blue-100 text-blue-800' :
                    aiRiskBadge.color === 'yellow' ? 'bg-yellow-100 text-yellow-800' :
                    aiRiskBadge.color === 'orange' ? 'bg-orange-100 text-orange-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    <svg className="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v3.57A22.952 22.952 0 0110 13a22.95 22.95 0 01-8-1.43V8a2 2 0 012-2h2zm2-1a1 1 0 011-1h2a1 1 0 011 1v1H8V5zm1 5a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clipRule="evenodd" />
                    </svg>
                    {aiRiskBadge.percentage}% AI Risk
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Apply Button */}
          <div className="flex gap-3">
            <button
              onClick={handleApply}
              disabled={applying || job.status !== 'active'}
              className={`flex-1 flex items-center justify-center px-6 py-3 rounded-lg font-medium transition-colors ${
                applying || job.status !== 'active'
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {applying ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Applying...
                </>
              ) : (
                <>
                  <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Apply with Auto-Tailor
                </>
              )}
            </button>
            {job.apply_url && (
              <a
                href={job.apply_url}
                target="_blank"
                rel="noopener noreferrer"
                className="px-6 py-3 border-2 border-blue-600 text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition-colors"
              >
                Apply on Company Site
              </a>
            )}
          </div>
        </div>

        {/* Match Breakdown (if available) */}
        {matchJob?.match_details && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Match Analysis</h2>

            {/* Why Matched */}
            <div className="mb-6 p-4 bg-blue-50 rounded-lg">
              <p className="text-gray-800">{matchJob.match_details.why_matched}</p>
            </div>

            {/* Score Breakdown */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
              <ScoreCard label="Skill Fit" score={matchJob.match_details.skill_fit_score} />
              <ScoreCard label="Career Trajectory" score={matchJob.match_details.trajectory_fit_score} />
              <ScoreCard label="Value Match" score={matchJob.match_details.value_match_score} />
              <ScoreCard label="Logistics" score={matchJob.match_details.logistics_fit_score} />
              <ScoreCard label="Growth Potential" score={matchJob.match_details.growth_potential_score} />
              <ScoreCard label="Overall" score={matchJob.match_details.overall_score} />
            </div>

            {/* Match Highlights */}
            {matchJob.match_details.match_highlights.length > 0 && (
              <div className="mb-4">
                <h3 className="font-semibold text-gray-900 mb-2">Strengths</h3>
                <ul className="space-y-2">
                  {matchJob.match_details.match_highlights.map((highlight, idx) => (
                    <li key={idx} className="flex items-start text-green-700">
                      <svg className="h-5 w-5 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      {highlight}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Skill Gaps */}
            {matchJob.match_details.skill_gaps.length > 0 && (
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Skills to Learn</h3>
                <div className="flex flex-wrap gap-2">
                  {matchJob.match_details.skill_gaps.map((skill, idx) => (
                    <span key={idx} className="px-3 py-1 bg-orange-100 text-orange-800 rounded-full text-sm">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Goal Relevance */}
            {matchJob.relevant_goals && matchJob.relevant_goals.length > 0 && (
              <div className="mt-6 p-4 bg-silver-soft rounded-lg">
                <h3 className="font-semibold text-gray-900 mb-2">Helps You Achieve</h3>
                <ul className="space-y-2">
                  {matchJob.relevant_goals.map((goal) => (
                    <li key={goal.goal_id} className="text-purple-800">
                      <div className="font-medium">{goal.goal_title}</div>
                      <div className="text-sm text-gold-primary">
                        Matches: {goal.overlap_keywords.join(', ')}
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Job Description */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Job Description</h2>
          <div className="prose max-w-none text-gray-700 whitespace-pre-wrap">
            {job.description}
          </div>
        </div>

        {/* Required Skills */}
        {job.skills_extracted && job.skills_extracted.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Required Skills</h2>
            <div className="flex flex-wrap gap-2">
              {job.skills_extracted.map((skill, idx) => (
                <span key={idx} className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm font-medium">
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Additional Info */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Additional Information</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            {job.industry && (
              <div>
                <div className="font-medium text-gray-700">Industry</div>
                <div className="text-gray-600">{job.industry}</div>
              </div>
            )}
            <div>
              <div className="font-medium text-gray-700">Job Status</div>
              <div className="text-gray-600 capitalize">{job.status}</div>
            </div>
            {job.posted_at && (
              <div>
                <div className="font-medium text-gray-700">Posted</div>
                <div className="text-gray-600">{new Date(job.posted_at).toLocaleDateString()}</div>
              </div>
            )}
            {job.expires_at && (
              <div>
                <div className="font-medium text-gray-700">Expires</div>
                <div className="text-gray-600">{new Date(job.expires_at).toLocaleDateString()}</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function ScoreCard({ label, score }: { label: string; score: number }) {
  return (
    <div className="p-4 border border-gray-200 rounded-lg">
      <div className="text-sm text-gray-600 mb-1">{label}</div>
      <div className="flex items-center">
        <div className="text-2xl font-bold text-gray-900">{score}</div>
        <div className="text-sm text-gray-500 ml-1">/100</div>
      </div>
      <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full ${
            score >= 80 ? 'bg-green-500' :
            score >= 60 ? 'bg-blue-500' :
            score >= 40 ? 'bg-yellow-500' :
            'bg-orange-500'
          }`}
          style={{ width: `${score}%` }}
        ></div>
      </div>
    </div>
  );
}

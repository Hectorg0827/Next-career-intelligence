'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { InterviewerAPI } from '@/lib/api/premiumAPI';
import Link from 'next/link';

interface InterviewSession {
  session_id: string;
  target_role: string;
  seniority_level: string;
  interview_type: string;
  num_questions: number;
  status: 'in_progress' | 'completed';
  created_at: string;
  completed_at?: string;
  suggestions_generated?: number;
}

export default function SessionsHistoryPage() {
  const router = useRouter();
  const [sessions, setSessions] = useState<InterviewSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<'all' | 'completed' | 'in_progress'>('all');

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      setError(null);
      const userId = localStorage.getItem('userId') || 'demo-user';
      const data = await InterviewerAPI.getSessions(userId);
      setSessions(data.sessions || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load sessions');
    } finally {
      setLoading(false);
    }
  };

  const filteredSessions = sessions.filter((session) =>
    filterStatus === 'all' ? true : session.status === filterStatus
  );

  const stats = {
    total: sessions.length,
    completed: sessions.filter((s) => s.status === 'completed').length,
    inProgress: sessions.filter((s) => s.status === 'in_progress').length,
    totalSuggestions: sessions.reduce((sum, s) => sum + (s.suggestions_generated || 0), 0),
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your sessions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Interview Sessions</h1>
              <p className="text-gray-600">Review your practice sessions and generated resume bullets</p>
            </div>
            <Link
              href="/interviewer/setup"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center"
            >
              <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Session
            </Link>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-600 mb-1">Total Sessions</div>
            <div className="text-3xl font-bold text-gray-900">{stats.total}</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-600 mb-1">Completed</div>
            <div className="text-3xl font-bold text-green-600">{stats.completed}</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-600 mb-1">In Progress</div>
            <div className="text-3xl font-bold text-yellow-600">{stats.inProgress}</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-600 mb-1">Resume Bullets</div>
            <div className="text-3xl font-bold text-blue-600">{stats.totalSuggestions}</div>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="bg-white rounded-lg shadow-md mb-6">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setFilterStatus('all')}
              className={`px-6 py-3 font-medium border-b-2 transition-colors ${
                filterStatus === 'all'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              All ({sessions.length})
            </button>
            <button
              onClick={() => setFilterStatus('completed')}
              className={`px-6 py-3 font-medium border-b-2 transition-colors ${
                filterStatus === 'completed'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Completed ({stats.completed})
            </button>
            <button
              onClick={() => setFilterStatus('in_progress')}
              className={`px-6 py-3 font-medium border-b-2 transition-colors ${
                filterStatus === 'in_progress'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              In Progress ({stats.inProgress})
            </button>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center text-red-800">
              <svg className="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              {error}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!error && filteredSessions.length === 0 && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
              />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {filterStatus === 'all' ? 'No sessions yet' : `No ${filterStatus.replace('_', ' ')} sessions`}
            </h3>
            <p className="text-gray-600 mb-6">
              {filterStatus === 'all'
                ? 'Start your first interview practice session to get personalized STAR questions'
                : 'Try changing the filter or start a new practice session'}
            </p>
            <Link
              href="/interviewer/setup"
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700"
            >
              <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Start First Session
            </Link>
          </div>
        )}

        {/* Sessions List */}
        {filteredSessions.length > 0 && (
          <div className="space-y-4">
            {filteredSessions.map((session) => (
              <SessionCard key={session.session_id} session={session} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function SessionCard({ session }: { session: InterviewSession }) {
  const router = useRouter();

  const handleViewSession = () => {
    if (session.status === 'completed') {
      router.push(`/interviewer/sessions/${session.session_id}`);
    } else {
      router.push(`/interviewer/practice?session=${session.session_id}`);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center mb-2">
            <h3 className="text-xl font-bold text-gray-900">{session.target_role}</h3>
            <span
              className={`ml-3 px-3 py-1 rounded-full text-xs font-medium ${
                session.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
              }`}
            >
              {session.status === 'completed' ? '✅ Completed' : '⏳ In Progress'}
            </span>
          </div>

          <div className="flex items-center text-gray-600 text-sm mb-3">
            <span className="capitalize">{session.seniority_level} Level</span>
            <span className="mx-2">•</span>
            <span className="capitalize">{session.interview_type}</span>
            <span className="mx-2">•</span>
            <span>{session.num_questions} Questions</span>
          </div>

          <div className="flex items-center text-gray-600 text-sm mb-4">
            <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <span>Started {new Date(session.created_at).toLocaleDateString()}</span>
            {session.completed_at && (
              <>
                <span className="mx-2">•</span>
                <span>Completed {new Date(session.completed_at).toLocaleDateString()}</span>
              </>
            )}
          </div>

          {session.suggestions_generated !== undefined && session.suggestions_generated > 0 && (
            <div className="inline-flex items-center px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm font-medium">
              <svg className="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                <path
                  fillRule="evenodd"
                  d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z"
                  clipRule="evenodd"
                />
              </svg>
              {session.suggestions_generated} Resume Bullets Generated
            </div>
          )}
        </div>

        <button
          onClick={handleViewSession}
          className="ml-4 px-4 py-2 border border-blue-600 text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition-colors"
        >
          {session.status === 'completed' ? 'View Results' : 'Continue'}
        </button>
      </div>
    </div>
  );
}

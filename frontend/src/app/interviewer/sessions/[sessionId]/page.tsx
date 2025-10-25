'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { InterviewerAPI } from '@/lib/api/premiumAPI';
import Link from 'next/link';

interface SessionDetail {
  session_id: string;
  target_role: string;
  seniority_level: string;
  interview_type: string;
  status: string;
  created_at: string;
  completed_at?: string;
  questions_and_answers: Array<{
    question: string;
    answer: string;
    star_breakdown?: {
      situation?: string;
      task?: string;
      action?: string;
      result?: string;
    };
  }>;
  suggestions: Array<{
    id: string;
    suggestion_type: string;
    description: string;
    reasoning: string;
    status: 'pending' | 'accepted' | 'rejected';
  }>;
}

export default function SessionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params?.sessionId as string;

  const [session, setSession] = useState<SessionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedQuestions, setExpandedQuestions] = useState<{ [key: number]: boolean }>({});

  useEffect(() => {
    if (sessionId) {
      fetchSessionDetail();
    }
  }, [sessionId]);

  const fetchSessionDetail = async () => {
    try {
      setLoading(true);
      setError(null);
      const userId = localStorage.getItem('userId') || 'demo-user';
      const data = await InterviewerAPI.getSession(sessionId, userId);
      setSession(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load session details');
    } finally {
      setLoading(false);
    }
  };

  const toggleQuestion = (index: number) => {
    setExpandedQuestions((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading session details...</p>
        </div>
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
          <div className="text-red-600 text-center mb-4">
            <svg className="mx-auto h-12 w-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <p className="font-medium">{error || 'Session not found'}</p>
          </div>
          <button
            onClick={() => router.push('/interviewer/sessions')}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700"
          >
            Back to Sessions
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/interviewer/sessions')}
            className="mb-4 flex items-center text-gray-600 hover:text-gray-900"
          >
            <svg className="h-5 w-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Sessions
          </button>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-start">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{session.target_role} Interview</h1>
                <div className="flex items-center text-gray-600 mb-4">
                  <span className="capitalize">{session.seniority_level} Level</span>
                  <span className="mx-2">•</span>
                  <span className="capitalize">{session.interview_type}</span>
                  <span className="mx-2">•</span>
                  <span>{session.questions_and_answers?.length || 0} Questions</span>
                </div>
                <div className="text-sm text-gray-600">
                  Completed {session.completed_at ? new Date(session.completed_at).toLocaleDateString() : 'N/A'}
                </div>
              </div>
              <span className="px-4 py-2 bg-green-100 text-green-800 rounded-full font-medium">
                ✅ Completed
              </span>
            </div>
          </div>
        </div>

        {/* Resume Suggestions */}
        {session.suggestions && session.suggestions.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Generated Resume Bullets</h2>
            <div className="space-y-4">
              {session.suggestions.map((suggestion) => (
                <div key={suggestion.id} className="bg-white rounded-lg shadow-md p-6">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium mr-2">
                          {suggestion.suggestion_type}
                        </span>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium ${
                            suggestion.status === 'accepted'
                              ? 'bg-green-100 text-green-800'
                              : suggestion.status === 'rejected'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}
                        >
                          {suggestion.status === 'accepted' && '✅ Accepted'}
                          {suggestion.status === 'rejected' && '❌ Rejected'}
                          {suggestion.status === 'pending' && '⏳ Pending'}
                        </span>
                      </div>
                      <p className="text-gray-900 font-medium mb-2">{suggestion.description}</p>
                      <p className="text-sm text-gray-600">{suggestion.reasoning}</p>
                    </div>
                    {suggestion.status === 'pending' && (
                      <div className="ml-4 flex gap-2">
                        <Link
                          href="/resume-studio/suggestions"
                          className="px-3 py-1 bg-blue-600 text-white rounded text-sm font-medium hover:bg-blue-700"
                        >
                          Review
                        </Link>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Questions & Answers */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Questions & Answers</h2>
          <div className="space-y-4">
            {session.questions_and_answers?.map((qa, index) => (
              <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="p-6">
                  <div className="flex items-start mb-4">
                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mr-4">
                      <span className="font-bold text-blue-600">{index + 1}</span>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">{qa.question}</h3>

                      {/* Answer */}
                      <div className="bg-gray-50 rounded-lg p-4 mb-4">
                        <div className="text-sm font-medium text-gray-700 mb-2">Your Answer:</div>
                        <p className="text-gray-800 whitespace-pre-wrap">{qa.answer}</p>
                      </div>

                      {/* STAR Breakdown */}
                      {qa.star_breakdown && (
                        <button
                          onClick={() => toggleQuestion(index)}
                          className="text-blue-600 hover:text-blue-700 font-medium text-sm flex items-center"
                        >
                          {expandedQuestions[index] ? 'Hide' : 'Show'} STAR Breakdown
                          <svg
                            className={`ml-1 h-4 w-4 transform transition-transform ${
                              expandedQuestions[index] ? 'rotate-180' : ''
                            }`}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                        </button>
                      )}
                    </div>
                  </div>
                </div>

                {/* Expanded STAR Breakdown */}
                {expandedQuestions[index] && qa.star_breakdown && (
                  <div className="border-t border-gray-200 bg-gray-50 p-6">
                    <h4 className="font-semibold text-gray-900 mb-4">STAR Method Analysis</h4>
                    <div className="grid md:grid-cols-2 gap-4">
                      {qa.star_breakdown.situation && (
                        <STARComponent
                          label="Situation"
                          value={qa.star_breakdown.situation}
                          color="green"
                          icon="S"
                        />
                      )}
                      {qa.star_breakdown.task && (
                        <STARComponent label="Task" value={qa.star_breakdown.task} color="blue" icon="T" />
                      )}
                      {qa.star_breakdown.action && (
                        <STARComponent label="Action" value={qa.star_breakdown.action} color="purple" icon="A" />
                      )}
                      {qa.star_breakdown.result && (
                        <STARComponent label="Result" value={qa.star_breakdown.result} color="orange" icon="R" />
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <Link
            href="/interviewer/setup"
            className="flex-1 text-center px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Start New Session
          </Link>
          <Link
            href="/resume-studio/profile"
            className="flex-1 text-center px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
          >
            View Resume Profile
          </Link>
        </div>
      </div>
    </div>
  );
}

function STARComponent({ label, value, color, icon }: { label: string; value: string; color: string; icon: string }) {
  const colorClasses = {
    green: 'bg-green-100 text-green-600 border-green-200',
    blue: 'bg-blue-100 text-blue-600 border-blue-200',
    purple: 'bg-silver-light text-gold-primary border-silver-soft',
    orange: 'bg-orange-100 text-orange-600 border-orange-200',
  };

  return (
    <div className={`p-4 rounded-lg border-2 ${colorClasses[color as keyof typeof colorClasses]}`}>
      <div className="flex items-center mb-2">
        <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center mr-2">
          <span className="font-bold">{icon}</span>
        </div>
        <span className="font-semibold">{label}</span>
      </div>
      <p className="text-sm text-gray-800">{value}</p>
    </div>
  );
}

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { InterviewerAPI } from '@/lib/api/premiumAPI';

const ROLES = [
  'Software Engineer',
  'Product Manager',
  'Data Scientist',
  'Designer',
  'Marketing Manager',
  'Sales Representative',
  'Business Analyst',
  'Project Manager',
  'DevOps Engineer',
  'QA Engineer',
  'Other',
];

const SENIORITY_LEVELS = [
  { value: 'entry', label: 'Entry Level', description: '0-2 years experience' },
  { value: 'mid', label: 'Mid Level', description: '3-5 years experience' },
  { value: 'senior', label: 'Senior', description: '6-10 years experience' },
  { value: 'lead', label: 'Lead', description: '10+ years, leading teams' },
  { value: 'director', label: 'Director', description: 'Managing multiple teams' },
];

const INTERVIEW_TYPES = [
  { value: 'behavioral', label: 'Behavioral', description: 'STAR method questions about past experiences' },
  { value: 'technical', label: 'Technical', description: 'Role-specific technical questions' },
  { value: 'leadership', label: 'Leadership', description: 'Questions about team management and strategy' },
];

export default function InterviewSetupPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [selectedRole, setSelectedRole] = useState('');
  const [customRole, setCustomRole] = useState('');
  const [seniority, setSeniority] = useState('mid');
  const [interviewType, setInterviewType] = useState('behavioral');
  const [numQuestions, setNumQuestions] = useState(5);

  const handleStartInterview = async () => {
    const role = selectedRole === 'Other' ? customRole : selectedRole;

    if (!role) {
      setError('Please select or enter a role');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const userId = localStorage.getItem('userId') || 'demo-user';

      const response = await InterviewerAPI.startSession({
        user_id: userId,
        target_role: role,
        seniority_level: seniority,
        interview_type: interviewType,
        num_questions: numQuestions,
      });

      // Store session ID and navigate to practice
      localStorage.setItem('currentInterviewSession', response.session_id);
      router.push(`/interviewer/practice?session=${response.session_id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to start interview session');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/interviewer')}
            className="mb-4 flex items-center text-gray-600 hover:text-gray-900"
          >
            <svg className="h-5 w-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back
          </button>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Setup Interview Practice</h1>
          <p className="text-gray-600">Configure your practice session to get role-specific questions</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-8">
          {/* Role Selection */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Target Role *
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
              {ROLES.map((role) => (
                <button
                  key={role}
                  onClick={() => setSelectedRole(role)}
                  className={`px-4 py-3 rounded-lg border-2 font-medium transition-colors ${
                    selectedRole === role
                      ? 'border-blue-600 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-gray-300 text-gray-700'
                  }`}
                >
                  {role}
                </button>
              ))}
            </div>
            {selectedRole === 'Other' && (
              <input
                type="text"
                value={customRole}
                onChange={(e) => setCustomRole(e.target.value)}
                placeholder="Enter your target role..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            )}
          </div>

          {/* Seniority Level */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Seniority Level *
            </label>
            <div className="space-y-3">
              {SENIORITY_LEVELS.map((level) => (
                <button
                  key={level.value}
                  onClick={() => setSeniority(level.value)}
                  className={`w-full px-4 py-3 rounded-lg border-2 font-medium transition-colors text-left ${
                    seniority === level.value
                      ? 'border-blue-600 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-gray-300 text-gray-700'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-semibold">{level.label}</div>
                      <div className="text-sm opacity-75">{level.description}</div>
                    </div>
                    {seniority === level.value && (
                      <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Interview Type */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Interview Type *
            </label>
            <div className="space-y-3">
              {INTERVIEW_TYPES.map((type) => (
                <button
                  key={type.value}
                  onClick={() => setInterviewType(type.value)}
                  className={`w-full px-4 py-3 rounded-lg border-2 font-medium transition-colors text-left ${
                    interviewType === type.value
                      ? 'border-blue-600 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-gray-300 text-gray-700'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-semibold">{type.label}</div>
                      <div className="text-sm opacity-75">{type.description}</div>
                    </div>
                    {interviewType === type.value && (
                      <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Number of Questions */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Number of Questions: {numQuestions}
            </label>
            <input
              type="range"
              min="3"
              max="10"
              value={numQuestions}
              onChange={(e) => setNumQuestions(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>3 questions</span>
              <span>10 questions</span>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center text-red-800">
                <svg className="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                {error}
              </div>
            </div>
          )}

          {/* Start Button */}
          <button
            onClick={handleStartInterview}
            disabled={loading || !selectedRole || (selectedRole === 'Other' && !customRole)}
            className="w-full py-4 bg-blue-600 text-white rounded-lg font-medium text-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-3"></div>
                Starting Interview...
              </>
            ) : (
              <>
                <svg className="h-6 w-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Start Interview Practice
              </>
            )}
          </button>

          {/* Info Box */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <div className="flex items-start">
              <svg className="h-5 w-5 text-blue-600 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <div className="text-sm text-blue-800">
                <p className="font-medium mb-1">Tips for a great practice session:</p>
                <ul className="list-disc list-inside space-y-1 text-blue-700">
                  <li>Use the STAR method to structure your answers</li>
                  <li>Include specific, quantifiable results</li>
                  <li>Be honest - this helps generate accurate resume bullets</li>
                  <li>Take your time - there's no time limit</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

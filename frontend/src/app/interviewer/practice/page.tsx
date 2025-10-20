'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { InterviewerAPI } from '@/lib/api/premiumAPI';

interface Question {
  question: string;
  index: number;
}

interface SessionData {
  session_id: string;
  questions: Question[];
  target_role: string;
  seniority_level: string;
  interview_type: string;
}

export default function InterviewPracticePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const sessionId = searchParams?.get('session');

  const [session, setSession] = useState<SessionData | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answer, setAnswer] = useState('');
  const [answers, setAnswers] = useState<{ [key: number]: string }>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [completed, setCompleted] = useState(false);

  useEffect(() => {
    if (sessionId) {
      fetchSession();
    } else {
      setError('No session ID provided');
      setLoading(false);
    }
  }, [sessionId]);

  const fetchSession = async () => {
    try {
      setLoading(true);
      const userId = localStorage.getItem('userId') || 'demo-user';
      const data = await InterviewerAPI.getSession(sessionId!, userId);
      setSession(data);

      // Check if there are saved answers
      if (data.answers) {
        setAnswers(data.answers);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load session');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!answer.trim()) {
      alert('Please provide an answer before continuing');
      return;
    }

    try {
      setSubmitting(true);
      const userId = localStorage.getItem('userId') || 'demo-user';

      await InterviewerAPI.submitAnswer({
        session_id: sessionId!,
        user_id: userId,
        question_index: currentQuestionIndex,
        answer: answer.trim(),
      });

      // Save answer locally
      setAnswers((prev) => ({
        ...prev,
        [currentQuestionIndex]: answer.trim(),
      }));

      // Move to next question or complete
      if (currentQuestionIndex < (session?.questions.length || 0) - 1) {
        setCurrentQuestionIndex(currentQuestionIndex + 1);
        setAnswer('');
      } else {
        // All questions answered
        await handleCompleteInterview();
      }
    } catch (err: any) {
      alert(`Failed to submit answer: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const handleCompleteInterview = async () => {
    try {
      setSubmitting(true);
      const userId = localStorage.getItem('userId') || 'demo-user';

      const result = await InterviewerAPI.completeInterview({
        session_id: sessionId!,
        user_id: userId,
      });

      setCompleted(true);

      // Show success message and redirect after a moment
      setTimeout(() => {
        router.push(`/interviewer/sessions/${sessionId}`);
      }, 2000);
    } catch (err: any) {
      alert(`Failed to complete interview: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
      setAnswer(answers[currentQuestionIndex - 1] || '');
    }
  };

  const handleSkip = () => {
    if (currentQuestionIndex < (session?.questions.length || 0) - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setAnswer(answers[currentQuestionIndex + 1] || '');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading interview session...</p>
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
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p className="font-medium">{error || 'Session not found'}</p>
          </div>
          <button
            onClick={() => router.push('/interviewer')}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700"
          >
            Back to Interviewer
          </button>
        </div>
      </div>
    );
  }

  if (completed) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="h-8 w-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Interview Complete!</h2>
          <p className="text-gray-600 mb-6">
            Great job! We're analyzing your answers and extracting achievements for your resume.
          </p>
          <div className="animate-pulse text-blue-600">Redirecting to results...</div>
        </div>
      </div>
    );
  }

  const currentQuestion = session.questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / session.questions.length) * 100;
  const isLastQuestion = currentQuestionIndex === session.questions.length - 1;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {session.target_role} Interview
              </h1>
              <p className="text-gray-600 capitalize">
                {session.seniority_level} Level • {session.interview_type}
              </p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-600">Question</div>
              <div className="text-2xl font-bold text-blue-600">
                {currentQuestionIndex + 1} / {session.questions.length}
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-6">
          <div className="flex items-start mb-6">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mr-4">
              <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                {currentQuestion.question}
              </h2>
              <p className="text-sm text-gray-500">
                Use the STAR method: Situation, Task, Action, Result
              </p>
            </div>
          </div>

          {/* Answer Input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your Answer
            </label>
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Describe your experience using the STAR method...

Situation: Set the context
Task: What was your responsibility?
Action: What specific steps did you take?
Result: What measurable outcomes did you achieve?"
              rows={12}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
            <div className="flex justify-between items-center mt-2">
              <span className="text-sm text-gray-500">
                {answer.length} characters
              </span>
              <span className="text-sm text-gray-500">
                Tip: Include numbers and specific outcomes
              </span>
            </div>
          </div>

          {/* Navigation Buttons */}
          <div className="flex gap-3">
            <button
              onClick={handlePrevious}
              disabled={currentQuestionIndex === 0}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            <button
              onClick={handleSkip}
              disabled={isLastQuestion}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Skip
            </button>
            <button
              onClick={handleSubmitAnswer}
              disabled={submitting}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
            >
              {submitting ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  {isLastQuestion ? 'Completing...' : 'Saving...'}
                </>
              ) : (
                <>
                  {isLastQuestion ? 'Complete Interview' : 'Next Question'}
                  <svg className="ml-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </>
              )}
            </button>
          </div>
        </div>

        {/* STAR Tips */}
        <div className="bg-blue-50 rounded-lg p-6">
          <h3 className="font-semibold text-gray-900 mb-3">STAR Method Quick Guide</h3>
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div>
              <div className="font-medium text-blue-900 mb-1">✅ Do:</div>
              <ul className="text-blue-800 space-y-1">
                <li>• Be specific with numbers and metrics</li>
                <li>• Focus on YOUR actions and contributions</li>
                <li>• Explain the impact of your work</li>
                <li>• Use past tense for completed projects</li>
              </ul>
            </div>
            <div>
              <div className="font-medium text-blue-900 mb-1">❌ Don't:</div>
              <ul className="text-blue-800 space-y-1">
                <li>• Use vague terms like "helped" or "worked on"</li>
                <li>• Forget to mention the outcome</li>
                <li>• Take credit for team achievements alone</li>
                <li>• Rush - take your time crafting responses</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

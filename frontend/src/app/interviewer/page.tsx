'use client';

import Link from 'next/link';

export default function InterviewerLandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI Interview Practice
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Practice STAR method interviews with AI, extract achievements from your experience, and generate compelling resume bullets
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          {/* Start Practice Card */}
          <Link href="/interviewer/setup">
            <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow cursor-pointer border-2 border-transparent hover:border-blue-500">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-6">
                <svg className="h-8 w-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-3">Start Practice Session</h2>
              <p className="text-gray-600 mb-4">
                Begin a new interview practice session. Select your target role and seniority to get tailored STAR questions.
              </p>
              <div className="flex items-center text-blue-600 font-medium">
                Start Interview
                <svg className="ml-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </Link>

          {/* Session History Card */}
          <Link href="/interviewer/sessions">
            <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow cursor-pointer border-2 border-transparent hover:border-indigo-500">
              <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mb-6">
                <svg className="h-8 w-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-3">Session History</h2>
              <p className="text-gray-600 mb-4">
                Review past interview sessions, see your answers, and track the resume bullets generated from your practice.
              </p>
              <div className="flex items-center text-indigo-600 font-medium">
                View History
                <svg className="ml-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </Link>
        </div>

        {/* What is STAR? */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">What is the STAR Method?</h2>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-green-600">S</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Situation</h3>
              <p className="text-gray-600 text-sm">
                Set the scene and context for your story
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">T</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Task</h3>
              <p className="text-gray-600 text-sm">
                Describe your responsibility or challenge
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-purple-600">A</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Action</h3>
              <p className="text-gray-600 text-sm">
                Explain the steps you took to solve it
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-orange-600">R</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Result</h3>
              <p className="text-gray-600 text-sm">
                Share the quantifiable outcomes achieved
              </p>
            </div>
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-xl font-bold text-blue-600">1</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Choose Your Role</h3>
              <p className="text-gray-600 text-sm">
                Select the role and seniority level you're preparing for
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-xl font-bold text-blue-600">2</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Answer STAR Questions</h3>
              <p className="text-gray-600 text-sm">
                Practice with role-specific behavioral questions
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-xl font-bold text-blue-600">3</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Get Resume Bullets</h3>
              <p className="text-gray-600 text-sm">
                AI extracts achievements and suggests resume improvements
              </p>
            </div>
          </div>
        </div>

        {/* Benefits */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Why Practice with AI?</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <BenefitItem icon="🎯" text="Role-specific questions tailored to your target position" />
            <BenefitItem icon="📊" text="Extract quantifiable achievements from your experiences" />
            <BenefitItem icon="✨" text="Generate compelling resume bullets automatically" />
            <BenefitItem icon="🔄" text="Practice unlimited times without pressure" />
            <BenefitItem icon="📈" text="Track your improvement over multiple sessions" />
            <BenefitItem icon="💡" text="Learn what great STAR answers look like" />
            <BenefitItem icon="⏱️" text="Practice on your own schedule, anytime" />
            <BenefitItem icon="🎓" text="Get feedback on your storytelling structure" />
          </div>
        </div>
      </div>
    </div>
  );
}

function BenefitItem({ icon, text }: { icon: string; text: string }) {
  return (
    <div className="flex items-center p-3 bg-gray-50 rounded-lg">
      <span className="text-2xl mr-3">{icon}</span>
      <span className="text-gray-700">{text}</span>
    </div>
  );
}

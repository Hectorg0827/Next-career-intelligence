'use client';

import Link from 'next/link';

export default function CoachLandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI Career Coach
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Get personalized career guidance, set SMART goals, and receive actionable advice to accelerate your career growth
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-2 gap-6 mb-12">
          {/* Chat Card */}
          <Link href="/coach/chat">
            <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow cursor-pointer border-2 border-transparent hover:border-purple-500">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mb-6">
                <svg className="h-8 w-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-3">Chat with Coach</h2>
              <p className="text-gray-600 mb-4">
                Have a conversation with your AI career coach. Get personalized advice on career moves, skill development, and job search strategies.
              </p>
              <div className="flex items-center text-purple-600 font-medium">
                Start Chatting
                <svg className="ml-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </Link>

          {/* Goals Card */}
          <Link href="/coach/goals">
            <div className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow cursor-pointer border-2 border-transparent hover:border-blue-500">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-6">
                <svg className="h-8 w-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-3">My Goals</h2>
              <p className="text-gray-600 mb-4">
                Track your SMART career goals, monitor progress, and celebrate achievements. Your coach helps you set and reach meaningful milestones.
              </p>
              <div className="flex items-center text-blue-600 font-medium">
                View Goals
                <svg className="ml-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </Link>
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-xl font-bold text-purple-600">1</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Share Your Situation</h3>
              <p className="text-gray-600 text-sm">
                Tell your coach about your current role, aspirations, and challenges
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-xl font-bold text-purple-600">2</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Get Personalized Advice</h3>
              <p className="text-gray-600 text-sm">
                Receive tailored guidance based on your career profile and goals
              </p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-xl font-bold text-purple-600">3</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Take Action</h3>
              <p className="text-gray-600 text-sm">
                Follow actionable steps and track your progress toward your goals
              </p>
            </div>
          </div>
        </div>

        {/* Features List */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">What Your Coach Can Help With</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <FeatureItem icon="🎯" text="Set and track SMART career goals" />
            <FeatureItem icon="💼" text="Navigate career transitions" />
            <FeatureItem icon="📈" text="Identify skill gaps and learning paths" />
            <FeatureItem icon="💰" text="Negotiate salary and benefits" />
            <FeatureItem icon="🚀" text="Plan for promotions and advancement" />
            <FeatureItem icon="🤝" text="Build professional networks" />
            <FeatureItem icon="⚖️" text="Achieve work-life balance" />
            <FeatureItem icon="📝" text="Improve resume and LinkedIn profile" />
          </div>
        </div>
      </div>
    </div>
  );
}

function FeatureItem({ icon, text }: { icon: string; text: string }) {
  return (
    <div className="flex items-center p-3 bg-gray-50 rounded-lg">
      <span className="text-2xl mr-3">{icon}</span>
      <span className="text-gray-700">{text}</span>
    </div>
  );
}

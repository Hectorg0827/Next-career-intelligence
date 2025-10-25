'use client';

import React from 'react';
import Link from 'next/link';

export default function JobsLandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            💼 Jobs Marketplace
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            AI-powered job matching with intelligent filtering. Find roles that align with your goals,
            match your skills, and reduce automation risk.
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <div className="text-4xl mb-3">🎯</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Goal-Based Matching</h3>
            <p className="text-sm text-gray-600">
              Jobs automatically filtered by your career goals
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <div className="text-4xl mb-3">🧠</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Skill Matching</h3>
            <p className="text-sm text-gray-600">
              Customize minimum skill overlap threshold
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <div className="text-4xl mb-3">📍</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Distance Filtering</h3>
            <p className="text-sm text-gray-600">
              Find jobs near you with geographic precision
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            <div className="text-4xl mb-3">🤖</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Risk Analysis</h3>
            <p className="text-sm text-gray-600">
              See automation probability (5-95%) for each job
            </p>
          </div>
        </div>

        {/* CTA Sections */}
        <div className="grid md:grid-cols-2 gap-8">
          {/* AI Recommendations */}
          <Link href="/jobs/recommendations">
            <div className="bg-gradient-to-br from-blue-600 to-blue-700 text-white p-8 rounded-lg shadow-lg hover:shadow-xl transition-all cursor-pointer transform hover:scale-105">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="inline-block px-3 py-1 bg-white bg-opacity-20 rounded-full text-sm font-medium mb-3">
                    ⭐ Premium
                  </div>
                  <h2 className="text-2xl font-bold mb-2">AI Recommendations</h2>
                  <p className="text-blue-100">
                    Get personalized job matches with multi-objective AI scoring
                  </p>
                </div>
                <div className="text-4xl">🎯</div>
              </div>

              <div className="space-y-2 mt-6">
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-blue-200">✓</span>
                  <span>Match score breakdown</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-blue-200">✓</span>
                  <span>Goal alignment indicators</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-blue-200">✓</span>
                  <span>AI displacement risk</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-blue-200">✓</span>
                  <span>Auto-tailor resume on apply</span>
                </div>
              </div>

              <div className="mt-6 text-center font-semibold">
                View My Recommendations →
              </div>
            </div>
          </Link>

          {/* Job Search */}
          <Link href="/jobs/search">
            <div className="bg-white border-2 border-gray-300 p-8 rounded-lg shadow-md hover:shadow-xl transition-all cursor-pointer transform hover:scale-105">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="inline-block px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium mb-3">
                    Free
                  </div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Job Search</h2>
                  <p className="text-gray-600">
                    Browse all available jobs with basic search and filtering
                  </p>
                </div>
                <div className="text-4xl">🔍</div>
              </div>

              <div className="space-y-2 mt-6">
                <div className="flex items-center gap-2 text-sm text-gray-700">
                  <span className="text-gray-400">✓</span>
                  <span>Search by keywords</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-700">
                  <span className="text-gray-400">✓</span>
                  <span>Filter by location</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-700">
                  <span className="text-gray-400">✓</span>
                  <span>Filter by seniority</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-700">
                  <span className="text-gray-400">✓</span>
                  <span>Remote/hybrid/onsite</span>
                </div>
              </div>

              <div className="mt-6 text-center font-semibold text-gray-900">
                Browse Jobs →
              </div>
            </div>
          </Link>
        </div>

        {/* Applications Link */}
        <div className="mt-8 text-center">
          <Link
            href="/jobs/applications"
            className="inline-flex items-center gap-2 px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            📋 View My Applications
          </Link>
        </div>

        {/* Info Box */}
        <div className="mt-16 bg-silver-soft border border-silver-soft rounded-lg p-8">
          <h3 className="text-xl font-semibold text-royal-navy mb-4">
            🚀 How It Works
          </h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <div className="text-3xl mb-2">1️⃣</div>
              <h4 className="font-semibold text-gray-900 mb-1">Set Your Goals</h4>
              <p className="text-sm text-gray-600">
                Define your career aspirations in the Career Coach
              </p>
            </div>
            <div>
              <div className="text-3xl mb-2">2️⃣</div>
              <h4 className="font-semibold text-gray-900 mb-1">Get Matched</h4>
              <p className="text-sm text-gray-600">
                AI analyzes jobs based on 5 scoring components
              </p>
            </div>
            <div>
              <div className="text-3xl mb-2">3️⃣</div>
              <h4 className="font-semibold text-gray-900 mb-1">Apply Instantly</h4>
              <p className="text-sm text-gray-600">
                Auto-tailor your resume and cover letter for each job
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

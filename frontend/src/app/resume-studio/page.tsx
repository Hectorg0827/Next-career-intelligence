'use client';

import React from 'react';
import Link from 'next/link';

export default function ResumeStudioLanding() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-silver-soft to-white">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <div className="inline-block px-4 py-2 bg-silver-light text-purple-800 rounded-full text-sm font-semibold mb-4">
            📄 Single Source of Truth (SSOT)
          </div>
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Resume Studio
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Your career profile is the foundation. Upload once, use everywhere.
            AI-powered suggestions from Coach and Interviewer await your approval.
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <Link href="/resume-studio/upload">
            <div className="bg-white p-6 rounded-lg shadow-md border-2 border-silver-soft hover:border-gold-hover transition-all cursor-pointer transform hover:scale-105">
              <div className="text-4xl mb-3">📤</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Upload Resume</h3>
              <p className="text-sm text-gray-600 mb-4">
                Upload PDF, DOCX, or TXT. AI will parse and create your profile.
              </p>
              <div className="text-gold-primary font-medium">Upload Now →</div>
            </div>
          </Link>

          <Link href="/resume-studio/profile">
            <div className="bg-white p-6 rounded-lg shadow-md border-2 border-blue-200 hover:border-blue-400 transition-all cursor-pointer transform hover:scale-105">
              <div className="text-4xl mb-3">👤</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">View Profile</h3>
              <p className="text-sm text-gray-600 mb-4">
                See your complete career profile - the single source of truth.
              </p>
              <div className="text-blue-600 font-medium">View Profile →</div>
            </div>
          </Link>

          <Link href="/resume-studio/suggestions">
            <div className="bg-white p-6 rounded-lg shadow-md border-2 border-green-200 hover:border-green-400 transition-all cursor-pointer transform hover:scale-105">
              <div className="text-4xl mb-3">📥</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Suggestions Inbox</h3>
              <p className="text-sm text-gray-600 mb-4">
                Review AI suggestions from Coach and Interviewer.
              </p>
              <div className="text-green-600 font-medium">Review Suggestions →</div>
            </div>
          </Link>
        </div>

        {/* How It Works */}
        <div className="bg-white border border-gray-200 rounded-lg p-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            🔄 How Resume Studio Works
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="text-5xl mb-4">1️⃣</div>
              <h3 className="font-semibold text-gray-900 mb-2">Upload & Parse</h3>
              <p className="text-sm text-gray-600">
                Upload your resume. AI extracts all information and creates your structured profile.
              </p>
            </div>
            <div className="text-center">
              <div className="text-5xl mb-4">2️⃣</div>
              <h3 className="font-semibold text-gray-900 mb-2">Use Across Platform</h3>
              <p className="text-sm text-gray-600">
                Your profile powers Coach, Interviewer, and Jobs Marketplace. One source, everywhere.
              </p>
            </div>
            <div className="text-center">
              <div className="text-5xl mb-4">3️⃣</div>
              <h3 className="font-semibold text-gray-900 mb-2">Review & Improve</h3>
              <p className="text-sm text-gray-600">
                AI generates suggestions. You review and approve before they're applied.
              </p>
            </div>
          </div>
        </div>

        {/* SSOT Explanation */}
        <div className="bg-silver-soft border border-silver-soft rounded-lg p-8">
          <h2 className="text-2xl font-bold text-royal-navy mb-4">
            📄 What is Single Source of Truth (SSOT)?
          </h2>
          <div className="space-y-4 text-gray-700">
            <p>
              Your <strong>Resume Studio profile</strong> is the authoritative record of your career.
              All other services (Coach, Interviewer, Jobs) <strong>read from it</strong> but never modify it directly.
            </p>
            <div className="grid md:grid-cols-2 gap-4 mt-6">
              <div className="bg-white p-4 rounded-lg">
                <h3 className="font-semibold text-green-900 mb-2">✅ What SSOT Means:</h3>
                <ul className="space-y-1 text-sm">
                  <li>• One place to update your info</li>
                  <li>• No conflicting versions</li>
                  <li>• Full version history</li>
                  <li>• You control all changes</li>
                </ul>
              </div>
              <div className="bg-white p-4 rounded-lg">
                <h3 className="font-semibold text-blue-900 mb-2">🔒 How It's Protected:</h3>
                <ul className="space-y-1 text-sm">
                  <li>• AI can only suggest changes</li>
                  <li>• You approve or reject</li>
                  <li>• Provenance tracking</li>
                  <li>• GDPR compliant</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-12 grid md:grid-cols-2 gap-6">
          <div className="bg-gradient-to-br from-gold-primary to-gold-accent text-white p-8 rounded-lg">
            <h3 className="text-2xl font-bold mb-2">New User?</h3>
            <p className="text-silver-light mb-6">
              Start by uploading your resume. We'll create your profile in seconds.
            </p>
            <Link
              href="/resume-studio/upload"
              className="inline-block px-6 py-3 bg-white text-gold-accent rounded-lg hover:bg-silver-soft transition-colors font-semibold"
            >
              Upload Resume
            </Link>
          </div>

          <div className="bg-gradient-to-br from-blue-600 to-blue-700 text-white p-8 rounded-lg">
            <h3 className="text-2xl font-bold mb-2">Returning User?</h3>
            <p className="text-blue-100 mb-6">
              View your profile or check your suggestions inbox.
            </p>
            <div className="flex gap-3">
              <Link
                href="/resume-studio/profile"
                className="px-4 py-2 bg-white text-blue-700 rounded-lg hover:bg-blue-50 transition-colors font-semibold"
              >
                View Profile
              </Link>
              <Link
                href="/resume-studio/suggestions"
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-400 transition-colors font-semibold"
              >
                Suggestions
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

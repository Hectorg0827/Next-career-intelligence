'use client';

import React, { useState, useEffect } from 'react';
import SuggestionsInbox from '@/components/resume-studio/SuggestionsInbox';
import { SuggestionsAPI } from '@/lib/api/premiumAPI';
import { ProfileSuggestion } from '@/types/resume';

export default function SuggestionsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<ProfileSuggestion[]>([]);

  // Fetch suggestions
  const fetchSuggestions = async () => {
    setLoading(true);
    setError(null);

    try {
      const userId = localStorage.getItem('userId') || 'dev_user_123';
      const response = await SuggestionsAPI.getPending(userId);
      setSuggestions(response.suggestions || []);
    } catch (err: any) {
      console.error('Failed to fetch suggestions:', err);
      setError(err.message || 'Failed to load suggestions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSuggestions();
  }, []);

  // Handle suggestion handled
  const handleSuggestionHandled = () => {
    // Refresh suggestions list
    fetchSuggestions();
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Suggestions Inbox</h1>
          <p className="text-gray-600">
            Review AI-generated suggestions from Career Coach and Interviewer AI
          </p>
        </div>

        {/* Info Banner */}
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-8">
          <div className="flex items-start gap-3">
            <span className="text-2xl">💡</span>
            <div>
              <h3 className="font-semibold text-purple-900 mb-1">How Suggestions Work</h3>
              <p className="text-sm text-purple-800">
                As you use <strong>Career Coach</strong> and <strong>Interviewer AI</strong>, they
                analyze your conversations and practice sessions to suggest improvements to your
                profile. <strong>You have full control</strong> - accept or reject each suggestion.
                Accepted suggestions are immediately applied to your profile.
              </p>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-600 mb-4"></div>
            <p className="text-gray-600">Loading suggestions...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <p className="text-red-800 font-medium">❌ {error}</p>
            <button
              onClick={fetchSuggestions}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Suggestions Inbox */}
        {!loading && !error && (
          <SuggestionsInbox
            userId={localStorage.getItem('userId') || 'dev_user_123'}
            suggestions={suggestions}
            onSuggestionHandled={handleSuggestionHandled}
          />
        )}
      </div>
    </div>
  );
}

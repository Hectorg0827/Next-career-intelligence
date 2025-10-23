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
      const response = await SuggestionsAPI.getPendingSuggestions(userId);
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
    <div className="min-h-screen py-8 bg-gray-50">
      <div className="max-w-6xl px-4 mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="mb-2 text-3xl font-bold text-gray-900">Suggestions Inbox</h1>
          <p className="text-gray-600">
            Review AI-generated suggestions from Career Coach and Interviewer AI
          </p>
        </div>

        {/* Info Banner */}
        <div className="p-4 mb-8 border border-purple-200 rounded-lg bg-purple-50">
          <div className="flex items-start gap-3">
            <span className="text-2xl">💡</span>
            <div>
              <h3 className="mb-1 font-semibold text-purple-900">How Suggestions Work</h3>
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
          <div className="py-12 text-center">
            <div className="inline-block w-12 h-12 mb-4 border-t-2 border-b-2 border-purple-600 rounded-full animate-spin"></div>
            <p className="text-gray-600">Loading suggestions...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="p-6 text-center border border-red-200 rounded-lg bg-red-50">
            <p className="font-medium text-red-800">❌ {error}</p>
            <button
              onClick={fetchSuggestions}
              className="px-4 py-2 mt-4 text-white bg-red-600 rounded-lg hover:bg-red-700"
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

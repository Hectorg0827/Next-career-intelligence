'use client';

import React, { useState } from 'react';
import { ProfileSuggestion, SuggestionType } from '@/types/resume';
import { ResumeStudioAPI } from '@/lib/api/premiumAPI';

interface SuggestionsInboxProps {
  userId: string;
  suggestions: ProfileSuggestion[];
  onSuggestionHandled?: () => void;
}

export default function SuggestionsInbox({ userId, suggestions, onSuggestionHandled }: SuggestionsInboxProps) {
  const [processingId, setProcessingId] = useState<string | null>(null);

  // Handle accept/reject suggestion
  const handleSuggestion = async (suggestionId: string, accept: boolean) => {
    setProcessingId(suggestionId);

    try {
      await ResumeStudioAPI.applySuggestion({
        user_id: userId,
        suggestion_id: suggestionId,
        accept,
      });

      onSuggestionHandled?.();
    } catch (error: any) {
      console.error('Failed to handle suggestion:', error);
      alert(`Failed to ${accept ? 'accept' : 'reject'} suggestion`);
    } finally {
      setProcessingId(null);
    }
  };

  // Filter suggestions by status
  const pendingSuggestions = suggestions.filter(s => s.status === 'pending');
  const reviewedSuggestions = suggestions.filter(s => s.status !== 'pending');

  // Get suggestion icon and color
  const getSuggestionStyle = (type: SuggestionType) => {
    const styles: Record<SuggestionType, { icon: string; color: string; bg: string }> = {
      add_experience_bullet: { icon: '💼', color: 'text-blue-800', bg: 'bg-blue-50' },
      update_experience_bullet: { icon: '✏️', color: 'text-purple-800', bg: 'bg-purple-50' },
      add_skill: { icon: '🧠', color: 'text-green-800', bg: 'bg-green-50' },
      add_project: { icon: '🚀', color: 'text-orange-800', bg: 'bg-orange-50' },
      update_summary: { icon: '📝', color: 'text-indigo-800', bg: 'bg-indigo-50' },
      add_achievement: { icon: '🏆', color: 'text-yellow-800', bg: 'bg-yellow-50' },
      add_certification: { icon: '📜', color: 'text-red-800', bg: 'bg-red-50' },
      improve_wording: { icon: '✨', color: 'text-pink-800', bg: 'bg-pink-50' },
    };
    return styles[type] || { icon: '📌', color: 'text-gray-800', bg: 'bg-gray-50' };
  };

  // Format suggestion type for display
  const formatSuggestionType = (type: SuggestionType): string => {
    return type
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Get source badge color
  const getSourceBadge = (source: string) => {
    const badges: Record<string, { label: string; color: string }> = {
      coach: { label: '🧑‍🏫 Coach', color: 'bg-purple-100 text-purple-800' },
      interviewer: { label: '🎤 Interviewer', color: 'bg-blue-100 text-blue-800' },
      auto: { label: '🤖 Auto', color: 'bg-gray-100 text-gray-800' },
    };
    return badges[source] || { label: source, color: 'bg-gray-100 text-gray-800' };
  };

  if (suggestions.length === 0) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
        <div className="text-6xl mb-4">📭</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">No Suggestions Yet</h3>
        <p className="text-gray-600">
          As you use Career Coach and Interviewer AI, suggestions will appear here for you to review
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Pending Suggestions */}
      {pendingSuggestions.length > 0 && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-900">
              Pending Suggestions ({pendingSuggestions.length})
            </h2>
            <div className="text-sm text-gray-600">
              Review and apply AI suggestions to your profile
            </div>
          </div>

          <div className="space-y-4">
            {pendingSuggestions.map((suggestion) => {
              const style = getSuggestionStyle(suggestion.suggestion_type);
              const source = getSourceBadge(suggestion.source);
              const isProcessing = processingId === suggestion.id;

              return (
                <div
                  key={suggestion.id}
                  className={`border-2 border-gray-200 rounded-lg p-6 transition-all ${
                    isProcessing ? 'opacity-50' : 'hover:border-blue-300'
                  }`}
                >
                  {/* Header */}
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-start gap-3">
                      <span className="text-3xl">{style.icon}</span>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {formatSuggestionType(suggestion.suggestion_type)}
                        </h3>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`px-2 py-1 rounded text-xs ${source.color}`}>
                            {source.label}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(suggestion.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Reasoning */}
                  {suggestion.reasoning && (
                    <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-700">
                        <span className="font-medium">Why:</span> {suggestion.reasoning}
                      </p>
                    </div>
                  )}

                  {/* Suggested Content */}
                  <div className={`p-4 ${style.bg} rounded-lg mb-4`}>
                    <div className="text-sm font-medium text-gray-700 mb-2">Suggested Change:</div>
                    {typeof suggestion.suggested_data === 'string' ? (
                      <p className={`text-sm ${style.color}`}>{suggestion.suggested_data}</p>
                    ) : (
                      <pre className={`text-sm ${style.color} whitespace-pre-wrap`}>
                        {JSON.stringify(suggestion.suggested_data, null, 2)}
                      </pre>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex gap-3">
                    <button
                      onClick={() => handleSuggestion(suggestion.id, true)}
                      disabled={isProcessing}
                      className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isProcessing ? 'Applying...' : '✓ Accept & Apply'}
                    </button>
                    <button
                      onClick={() => handleSuggestion(suggestion.id, false)}
                      disabled={isProcessing}
                      className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isProcessing ? 'Rejecting...' : '✕ Reject'}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Reviewed Suggestions */}
      {reviewedSuggestions.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Previously Reviewed ({reviewedSuggestions.length})
          </h2>

          <div className="space-y-3">
            {reviewedSuggestions.map((suggestion) => {
              const style = getSuggestionStyle(suggestion.suggestion_type);
              const source = getSourceBadge(suggestion.source);

              return (
                <div
                  key={suggestion.id}
                  className={`border border-gray-200 rounded-lg p-4 ${
                    suggestion.status === 'accepted' ? 'bg-green-50' : 'bg-red-50'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-3">
                      <span className="text-xl">{style.icon}</span>
                      <div>
                        <h4 className="font-medium text-gray-900">
                          {formatSuggestionType(suggestion.suggestion_type)}
                        </h4>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`px-2 py-1 rounded text-xs ${source.color}`}>
                            {source.label}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(suggestion.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div>
                      {suggestion.status === 'accepted' ? (
                        <span className="px-3 py-1 bg-green-600 text-white rounded-full text-sm font-medium">
                          ✓ Accepted
                        </span>
                      ) : (
                        <span className="px-3 py-1 bg-red-600 text-white rounded-full text-sm font-medium">
                          ✕ Rejected
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

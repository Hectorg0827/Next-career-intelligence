/**
 * AI Profile Assistant Component
 * 
 * Displays profile analysis, completeness score, and AI-powered suggestions
 * for profile improvement.
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  CheckCircle, 
  AlertCircle, 
  TrendingUp, 
  Sparkles, 
  Loader2,
  ChevronRight 
} from 'lucide-react';
import { apiClient } from '@/lib/api-client';

interface ProfileAnalysis {
  completeness_level: string;
  completeness_score: number;
  missing_fields: string[];
  incomplete_fields: string[];
  suggestions_count: number;
  inferred_skills: string[];
  strengths: string[];
  weaknesses: string[];
}

interface ProfileSuggestion {
  field: string;
  suggestion_type: string;
  current_value?: string;
  suggested_value: string;
  reasoning: string;
  priority: number;
  impact_score: number;
}

interface AIProfileAssistantProps {
  compact?: boolean;
  showInferredSkills?: boolean;
  maxSuggestions?: number;
}

export default function AIProfileAssistant({ 
  compact = false,
  showInferredSkills = true,
  maxSuggestions = 5 
}: AIProfileAssistantProps) {
  const router = useRouter();
  const [analysis, setAnalysis] = useState<ProfileAnalysis | null>(null);
  const [suggestions, setSuggestions] = useState<ProfileSuggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [inferring, setInferring] = useState(false);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetchProfileAnalysis();
  }, []);

  const fetchProfileAnalysis = async () => {
    try {
      setLoading(true);
      
      // Fetch analysis and suggestions in parallel
      const [analysisRes, suggestionsRes] = await Promise.all([
        apiClient.get('/ai/profile/analysis'),
        apiClient.get('/ai/profile/suggestions')
      ]);

      if (analysisRes.success && analysisRes.analysis) {
        setAnalysis(analysisRes.analysis);
      }

      if (suggestionsRes.success && suggestionsRes.suggestions) {
        setSuggestions(suggestionsRes.suggestions.slice(0, maxSuggestions));
      }
    } catch (error) {
      console.error('Failed to fetch profile analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInferData = async () => {
    try {
      setInferring(true);
      const response = await apiClient.post('/ai/profile/infer');
      
      if (response.success && response.inferred_data) {
        // Show success message
        alert(`AI inferred ${response.inferred_count} fields! Review and apply them in your profile.`);
        // Optionally navigate to profile edit page
        router.push('/quick-profile');
      }
    } catch (error) {
      console.error('Failed to infer data:', error);
      alert('Failed to infer profile data. Please try again.');
    } finally {
      setInferring(false);
    }
  };

  const handleGenerateSummary = async () => {
    try {
      setGenerating(true);
      const response = await apiClient.post('/ai/profile/generate-summary');
      
      if (response.success && response.summary) {
        // Show summary in a modal or navigate to profile editor
        alert(`AI Generated Summary:\n\n${response.summary}\n\nCopy this to your profile!`);
      }
    } catch (error) {
      console.error('Failed to generate summary:', error);
      alert('Failed to generate summary. Make sure your profile has enough information.');
    } finally {
      setGenerating(false);
    }
  };

  const getLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'perfect':
        return 'text-green-600 dark:text-green-400';
      case 'excellent':
        return 'text-green-500 dark:text-green-400';
      case 'good':
        return 'text-blue-500 dark:text-blue-400';
      case 'basic':
        return 'text-yellow-500 dark:text-yellow-400';
      default:
        return 'text-red-500 dark:text-red-400';
    }
  };

  const getProgressColor = (score: number) => {
    if (score >= 0.9) return 'bg-green-600';
    if (score >= 0.75) return 'bg-green-500';
    if (score >= 0.5) return 'bg-blue-500';
    if (score >= 0.3) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <div className="glass-card p-6">
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
        </div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="glass-card p-6">
        <p className="text-center text-ink-300">
          Unable to load profile analysis
        </p>
      </div>
    );
  }

  const percentage = Math.round(analysis.completeness_score * 100);

  if (compact) {
    return (
      <div className="glass-card p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary-500" />
            <h3 className="font-semibold text-white">Profile Strength</h3>
          </div>
          <span className={`text-2xl font-bold ${getLevelColor(analysis.completeness_level)}`}>
            {percentage}%
          </span>
        </div>
        
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-3">
          <div 
            className={`${getProgressColor(analysis.completeness_score)} h-2 rounded-full transition-all duration-500`}
            style={{ width: `${percentage}%` }}
          />
        </div>

        {analysis.suggestions_count > 0 && (
          <button
            onClick={() => router.push('/profile')}
            className="w-full text-sm text-primary-500 hover:text-primary-400 font-medium flex items-center justify-center gap-1"
          >
            {analysis.suggestions_count} Improvements Available
            <ChevronRight className="w-4 h-4" />
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Completeness Score Card */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-4">
          <Sparkles className="w-6 h-6 text-primary-500" />
          <h3 className="text-xl font-semibold text-white">
            Profile Intelligence
          </h3>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between items-baseline mb-2">
            <span className="text-3xl font-bold text-white">{percentage}%</span>
            <span className={`text-lg font-semibold ${getLevelColor(analysis.completeness_level)}`}>
              {analysis.completeness_level.charAt(0).toUpperCase() + analysis.completeness_level.slice(1)}
            </span>
          </div>
          
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
            <div 
              className={`${getProgressColor(analysis.completeness_score)} h-3 rounded-full transition-all duration-500`}
              style={{ width: `${percentage}%` }}
            />
          </div>
        </div>

        {/* Strengths */}
        {analysis.strengths.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-green-600 dark:text-green-400 mb-2 flex items-center gap-2">
              <CheckCircle className="w-4 h-4" />
              Strengths
            </h4>
            <ul className="space-y-1">
              {analysis.strengths.map((strength, idx) => (
                <li key={idx} className="text-sm text-ink-200 pl-6">
                  • {strength}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Weaknesses/Areas to Improve */}
        {analysis.weaknesses.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-semibold text-yellow-600 dark:text-yellow-400 mb-2 flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              Areas to Improve
            </h4>
            <ul className="space-y-1">
              {analysis.weaknesses.map((weakness, idx) => (
                <li key={idx} className="text-sm text-ink-200 pl-6">
                  • {weakness}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-3 mt-6">
          <button
            onClick={handleInferData}
            disabled={inferring}
            className="flex-1 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {inferring ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Inferring...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Quick Fill Profile
              </>
            )}
          </button>

          <button
            onClick={handleGenerateSummary}
            disabled={generating}
            className="flex-1 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {generating ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <TrendingUp className="w-4 h-4" />
                Generate Summary
              </>
            )}
          </button>
        </div>
      </div>

      {/* AI Suggestions */}
      {suggestions.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            AI Suggestions ({suggestions.length})
          </h3>
          
          <div className="space-y-3">
            {suggestions.map((suggestion, idx) => (
              <div 
                key={idx}
                className="p-4 bg-white/5 rounded-lg border border-white/10 hover:border-primary-500/50 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-white capitalize">
                      {suggestion.field.replace(/_/g, ' ')}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      suggestion.priority === 1 
                        ? 'bg-red-500/20 text-red-400'
                        : suggestion.priority === 2
                        ? 'bg-yellow-500/20 text-yellow-400'
                        : 'bg-blue-500/20 text-blue-400'
                    }`}>
                      Priority {suggestion.priority}
                    </span>
                  </div>
                  <span className="text-xs text-ink-300">
                    +{Math.round(suggestion.impact_score * 100)}% impact
                  </span>
                </div>
                
                <p className="text-sm text-ink-200 mb-2">
                  {suggestion.reasoning}
                </p>
                
                {suggestion.suggested_value && (
                  <div className="text-xs text-primary-400 bg-primary-500/10 px-3 py-2 rounded">
                    💡 Suggestion: {suggestion.suggested_value}
                  </div>
                )}
              </div>
            ))}
          </div>

          {analysis.suggestions_count > suggestions.length && (
            <button
              onClick={() => router.push('/profile')}
              className="w-full mt-4 text-sm text-primary-500 hover:text-primary-400 font-medium flex items-center justify-center gap-1"
            >
              View All {analysis.suggestions_count} Suggestions
              <ChevronRight className="w-4 h-4" />
            </button>
          )}
        </div>
      )}

      {/* Inferred Skills */}
      {showInferredSkills && analysis.inferred_skills.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            AI Detected Skills
          </h3>
          <p className="text-sm text-ink-300 mb-3">
            Based on your experience, we found these skills:
          </p>
          <div className="flex flex-wrap gap-2">
            {analysis.inferred_skills.map((skill, idx) => (
              <span 
                key={idx}
                className="px-3 py-1 bg-primary-500/20 text-primary-300 text-sm rounded-full border border-primary-500/30"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

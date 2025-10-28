/**
 * Premium API Service
 * Unified service for Resume Studio, Career Coach, and Interviewer AI
 * All services communicate harmoniously through this layer
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Helper for authenticated requests
async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem('authToken');

  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// ========================================
// RESUME STUDIO API
// ========================================

export const ResumeStudioAPI = {
  /**
   * Ingest and parse resume/profile
   */
  async ingestResume(data: {
    text?: string;
    file?: File;
    user_id: string;
  }) {
    const formData = new FormData();
    if (data.file) {
      formData.append('file', data.file);
    }

    const body = {
      text: data.text,
      user_id: data.user_id,
      privacy_consent: {
        store_profile: true,
        ai_processing: true,
        data_retention: true,
      },
      user_region: 'US',
    };

    return fetchWithAuth(`${API_BASE}/resume-studio/ingest`, {
      method: 'POST',
      body: data.file ? formData : JSON.stringify(body),
      ...(data.file && { headers: {} }), // Let browser set Content-Type for FormData
    });
  },

  /**
   * Confirm and save parsed profile
   */
  async saveProfile(userId: string, profileData: any) {
    // This would create/update the career profile
    // For now, profiles are created via ingest
    return { success: true };
  },

  /**
   * Get user's career profile
   */
  async getProfile(userId: string) {
    return fetchWithAuth(`${API_BASE}/resume-studio/profile/${userId}`);
  },

  /**
   * Tailor resume for job
   */
  async tailorResume(data: {
    user_id: string;
    job_description: any;
  }) {
    return fetchWithAuth(`${API_BASE}/resume-studio/tailor`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Generate cover letter
   */
  async generateCoverLetter(data: {
    user_id: string;
    job_description: any;
  }) {
    return fetchWithAuth(`${API_BASE}/resume-studio/cover-letter/tailor`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Apply user-approved suggestion
   */
  async applySuggestion(data: {
    user_id: string;
    suggestion_id: string;
    user_confirmed: boolean;
  }) {
    return fetchWithAuth(`${API_BASE}/resume-studio/suggestions/apply`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};

// ========================================
// CAREER COACH API
// ========================================

export const CareerCoachAPI = {
  /**
   * Chat with Career Coach
   */
  async chat(data: {
    user_id: string;
    message: string;
    conversation_id?: string;
    conversation_type?: string;
  }) {
    return fetchWithAuth(`${API_BASE}/coach/chat`, {
      method: 'POST',
      body: JSON.stringify({
        ...data,
        conversation_type: data.conversation_type || 'general',
      }),
    });
  },

  /**
   * Create career goal
   */
  async createGoal(data: {
    user_id: string;
    goal: any;
  }) {
    return fetchWithAuth(`${API_BASE}/coach/goals`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Get all goals for user
   */
  async getGoals(userId: string) {
    return fetchWithAuth(`${API_BASE}/coach/goals/${userId}`);
  },

  /**
   * Update goal progress
   */
  async updateGoal(goalId: string, data: {
    user_id: string;
    updates: any;
  }) {
    return fetchWithAuth(`${API_BASE}/coach/goals/${goalId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },
};

// ========================================
// INTERVIEWER AI API
// ========================================

export const InterviewerAPI = {
  /**
   * Start interview session
   */
  async startInterview(data: {
    user_id: string;
    role_title: string;
    company_name?: string;
    job_description?: any;
    interview_type?: string;
  }) {
    return fetchWithAuth(`${API_BASE}/interviewer/start`, {
      method: 'POST',
      body: JSON.stringify({
        ...data,
        interview_type: data.interview_type || 'behavioral',
      }),
    });
  },

  /**
   * Submit answer to question
   */
  async submitAnswer(data: {
    session_id: string;
    user_id: string;
    question_index: number;
    answer: string;
  }) {
    return fetchWithAuth(`${API_BASE}/interviewer/answer`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Complete interview and get suggestions
   */
  async completeInterview(data: {
    session_id: string;
    user_id: string;
  }) {
    return fetchWithAuth(`${API_BASE}/interviewer/complete`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Get all interview sessions
   */
  async getSessions(userId: string) {
    return fetchWithAuth(`${API_BASE}/interviewer/sessions/${userId}`);
  },

  /**
   * Get specific session details
   */
  async getSession(sessionId: string, userId: string) {
    return fetchWithAuth(`${API_BASE}/interviewer/session/${sessionId}?user_id=${userId}`);
  },
};

// ========================================
// SUGGESTIONS API (Unified inbox)
// ========================================

export const SuggestionsAPI = {
  /**
   * Get all pending suggestions from Coach + Interviewer
   */
  async getPendingSuggestions(userId: string) {
    // This would query profile_suggestions table
    // For now, suggestions come embedded in Coach/Interviewer responses
    return { suggestions: [] };
  },

  /**
   * Accept suggestion (sends to Resume Studio)
   */
  async acceptSuggestion(userId: string, suggestionId: string) {
    return ResumeStudioAPI.applySuggestion({
      user_id: userId,
      suggestion_id: suggestionId,
      user_confirmed: true,
    });
  },

  /**
   * Reject suggestion
   */
  async rejectSuggestion(userId: string, suggestionId: string) {
    // Mark as rejected in database
    return { success: true };
  },
};

// ========================================
// SUBSCRIPTION API
// ========================================

export const SubscriptionAPI = {
  /**
   * Create checkout session
   */
  async createCheckout(data: {
    plan: 'premium' | 'enterprise';
    billing_period: 'monthly' | 'yearly';
  }) {
    return fetchWithAuth(`${API_BASE}/subscription/checkout`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Get current subscription
   */
  async getSubscription(userId: string) {
    return fetchWithAuth(`${API_BASE}/subscription/${userId}`);
  },

  /**
   * Cancel subscription
   */
  async cancelSubscription(subscriptionId: string) {
    return fetchWithAuth(`${API_BASE}/subscription/${subscriptionId}/cancel`, {
      method: 'POST',
    });
  },
};

// ========================================
// UNIFIED SERVICE (Orchestrator)
// ========================================

/**
 * UnifiedService orchestrates Coach, Resume, and Goals
 * Ensures they work harmoniously together
 */
export const UnifiedService = {
  /**
   * Complete onboarding flow:
   * 1. Ingest resume → Resume Studio
   * 2. Extract initial goals → Coach
   * 3. Return suggestions
   */
  async completeOnboarding(data: {
    user_id: string;
    resume_text?: string;
    resume_file?: File;
    career_aspirations?: string;
  }) {
    try {
      // Step 1: Ingest resume
      const ingestResult = await ResumeStudioAPI.ingestResume({
        text: data.resume_text,
        file: data.resume_file,
        user_id: data.user_id,
      });

      // Step 2: If career aspirations provided, discuss with coach
      let coachResult = null;
      if (data.career_aspirations) {
        coachResult = await CareerCoachAPI.chat({
          user_id: data.user_id,
          message: `I want to: ${data.career_aspirations}. Can you help me create a goal and suggest improvements?`,
          conversation_type: 'goal_setting',
        });
      }

      return {
        profile_created: true,
        ingest_result: ingestResult,
        coach_suggestions: coachResult,
        next_steps: [
          'Review parsed profile for accuracy',
          'Complete any open questions',
          'Review AI suggestions',
        ],
      };
    } catch (error) {
      console.error('Onboarding error:', error);
      throw error;
    }
  },

  /**
   * Process interview results and sync with goals
   * 1. Complete interview → get suggestions
   * 2. Create goal from interview insights
   * 3. Add suggestions to inbox
   */
  async processInterviewResults(data: {
    user_id: string;
    session_id: string;
    create_goal_from_insights?: boolean;
  }) {
    try {
      // Complete interview
      const interviewResult = await InterviewerAPI.completeInterview({
        session_id: data.session_id,
        user_id: data.user_id,
      });

      // If create goal requested, extract insights and create goal
      if (data.create_goal_from_insights && interviewResult.evidence_summaries?.length > 0) {
        const insights = interviewResult.evidence_summaries
          .map((e: any) => e.summary)
          .join('; ');

        const coachResult = await CareerCoachAPI.chat({
          user_id: data.user_id,
          message: `Based on my interview, here are my accomplishments: ${insights}. Can you help me create a goal to build on these?`,
          conversation_type: 'goal_setting',
        });

        return {
          interview_result: interviewResult,
          goal_created: coachResult.goal_updates?.length > 0,
          coach_suggestions: coachResult,
        };
      }

      return { interview_result: interviewResult };
    } catch (error) {
      console.error('Interview processing error:', error);
      throw error;
    }
  },

  /**
   * Sync goal progress with profile updates
   * When profile improves, update relevant goals
   */
  async syncGoalProgress(userId: string) {
    try {
      const [profile, goals] = await Promise.all([
        ResumeStudioAPI.getProfile(userId),
        CareerCoachAPI.getGoals(userId),
      ]);

      // Check each active goal against profile
      const updates: any[] = [];

      for (const goal of goals.goals) {
        if (goal.status !== 'active') continue;

        // Example: If goal is "Learn Python" and Python is now in skills
        const goalSkills = this._extractSkillsFromGoal(goal);
        const profileSkills = profile.profile_data?.skills?.hard || [];

        const skillsAcquired = goalSkills.filter((s: string) =>
          profileSkills.some((ps: string) => ps.toLowerCase().includes(s.toLowerCase()))
        );

        if (skillsAcquired.length > 0) {
          const progress = Math.min(100, (skillsAcquired.length / goalSkills.length) * 100);

          updates.push(
            CareerCoachAPI.updateGoal(goal.id, {
              user_id: userId,
              updates: {
                progress_percentage: Math.round(progress),
              },
            })
          );
        }
      }

      await Promise.all(updates);

      return {
        goals_synced: updates.length,
        message: `Updated ${updates.length} goals based on profile changes`,
      };
    } catch (error) {
      console.error('Goal sync error:', error);
      throw error;
    }
  },

  /**
   * Helper: Extract skills mentioned in goal
   */
  _extractSkillsFromGoal(goal: any): string[] {
    const text = `${goal.goal_title} ${goal.specific || ''}`.toLowerCase();
    const commonSkills = ['python', 'java', 'react', 'sql', 'aws', 'docker', 'kubernetes'];
    return commonSkills.filter(skill => text.includes(skill));
  },
};

// ========================================
// JOBS MARKETPLACE API (v2.0 Enhanced)
// ========================================

export const JobsMarketplaceAPI = {
  /**
   * Search jobs (public endpoint)
   */
  async searchJobs(params: {
    query?: string;
    location?: string;
    seniority?: string;
    remote_only?: boolean;
    min_salary?: number;
    skills?: string[];
    limit?: number;
    offset?: number;
  }) {
    const queryParams = new URLSearchParams();
    if (params.query) queryParams.append('query', params.query);
    if (params.location) queryParams.append('location', params.location);
    if (params.seniority) queryParams.append('seniority', params.seniority);
    if (params.remote_only) queryParams.append('remote_only', 'true');
    if (params.min_salary) queryParams.append('min_salary', params.min_salary.toString());
    if (params.skills) params.skills.forEach(s => queryParams.append('skills', s));
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.offset) queryParams.append('offset', params.offset.toString());

    return fetchWithAuth(`${API_BASE}/jobs/search?${queryParams.toString()}`);
  },

  /**
   * Get AI-matched recommendations with enhanced filtering (Premium)
   */
  async getRecommendations(params: {
    user_id?: string;
    refresh?: boolean;
    limit?: number;
    min_skill_match?: number; // 0-100, default 30
    max_distance_km?: number | null;
    expand_search?: boolean;
  }) {
    const queryParams = new URLSearchParams();
    if (params.user_id) queryParams.append('user_id', params.user_id);
    if (params.refresh) queryParams.append('refresh', 'true');
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.min_skill_match !== undefined) {
      queryParams.append('min_skill_match', params.min_skill_match.toString());
    }
    if (params.max_distance_km !== undefined && params.max_distance_km !== null) {
      queryParams.append('max_distance_km', params.max_distance_km.toString());
    }
    if (params.expand_search) queryParams.append('expand_search', 'true');

    return fetchWithAuth(`${API_BASE}/jobs/recommendations?${queryParams.toString()}`);
  },

  /**
   * Get job details
   */
  async getJobDetails(jobId: string) {
    return fetchWithAuth(`${API_BASE}/jobs/jobs/${jobId}`);
  },

  /**
   * Apply to job with auto-tailor (Premium)
   */
  async applyToJob(data: {
    user_id: string;
    job_id: string;
    auto_tailor?: boolean;
    auto_cover_letter?: boolean;
    custom_message?: string;
  }) {
    return fetchWithAuth(`${API_BASE}/jobs/apply`, {
      method: 'POST',
      body: JSON.stringify({
        ...data,
        auto_tailor: data.auto_tailor !== false, // Default true
        auto_cover_letter: data.auto_cover_letter !== false, // Default true
      }),
    });
  },

  /**
   * Get user's applications
   */
  async getMyApplications(userId: string) {
    return fetchWithAuth(`${API_BASE}/jobs/applications/my?user_id=${userId}`);
  },

  /**
   * Get job preferences
   */
  async getPreferences(userId: string) {
    return fetchWithAuth(`${API_BASE}/jobs/preferences?user_id=${userId}`);
  },

  /**
   * Update job preferences
   */
  async updatePreferences(userId: string, preferences: {
    desired_titles?: string[];
    desired_industries?: string[];
    desired_locations?: string[];
    remote_only?: boolean;
    work_arrangement?: string;
    salary_min?: number;
    salary_max?: number;
    company_size_preference?: string[];
    auto_apply_enabled?: boolean;
    home_latitude?: number;
    home_longitude?: number;
  }) {
    return fetchWithAuth(`${API_BASE}/jobs/preferences?user_id=${userId}`, {
      method: 'PUT',
      body: JSON.stringify(preferences),
    });
  },
};

export default {
  ResumeStudioAPI,
  CareerCoachAPI,
  InterviewerAPI,
  SuggestionsAPI,
  SubscriptionAPI,
  UnifiedService,
  JobsMarketplaceAPI,
};

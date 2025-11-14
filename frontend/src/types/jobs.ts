/**
 * Job Marketplace Types
 * Enhanced with v2.0 filtering features
 */

export interface Job {
  id: string;
  title: string;
  company: string;
  employer_id?: string;
  description: string;
  location_city?: string;
  location_state?: string;
  location_country?: string;
  location_type: 'remote' | 'onsite' | 'hybrid';
  latitude?: number;
  longitude?: number;
  seniority: 'entry' | 'mid' | 'senior' | 'lead' | 'director' | 'executive';
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  skills_extracted: string[];
  industry?: string;
  posted_at?: string;
  expires_at?: string;
  apply_url?: string;
  status: 'active' | 'closed' | 'filled';
  is_spam: boolean;
}

export interface JobMatch extends Job {
  // Enhanced v2.0 fields
  match_score: number;
  ai_displacement_risk: number; // 5-95%
  distance_km?: number | null;
  goal_relevance_score: number; // 0-100
  relevant_goals: RelevantGoal[];
  match_details: MatchDetails;
}

export interface RelevantGoal {
  goal_id: string;
  goal_title: string;
  overlap_keywords: string[];
}

export interface MatchDetails {
  overall_score: number;
  skill_fit_score: number;
  trajectory_fit_score: number;
  value_match_score: number;
  logistics_fit_score: number;
  growth_potential_score: number;
  penalties: number;
  match_highlights: string[];
  skill_gaps: string[];
  displacement_risk_improvement: number;
  why_matched: string;
}

export interface JobRecommendationsResponse {
  recommendations: JobMatch[];
  total: number;
  total_before_filtering: number;
  filters_applied: {
    min_skill_match: number;
    max_distance_km: number | null;
    goals_count: number;
    expand_search: boolean;
  };
  user_goals: Array<{ id: string; title: string }>;
  profile_id: string;
}

export interface JobSearchParams {
  query?: string;
  location?: string;
  seniority?: string;
  remote_only?: boolean;
  min_salary?: number;
  skills?: string[];
  limit?: number;
  offset?: number;
}

export interface JobRecommendationParams {
  user_id?: string;
  refresh?: boolean;
  limit?: number;
  min_skill_match?: number; // 0-100
  max_distance_km?: number | null;
  expand_search?: boolean;
}

export interface JobApplication {
  id: string;
  user_id: string;
  job_id: string;
  job?: Job;
  tailored_resume_text: string;
  cover_letter_text: string;
  status: 'submitted' | 'screening' | 'interview' | 'offer' | 'rejected' | 'accepted' | 'withdrawn';
  submitted_at: string;
  response_received_at?: string;
  notes?: string;
}

export interface JobPreferences {
  user_id: string;
  desired_titles: string[];
  desired_industries: string[];
  desired_locations: string[];
  remote_only: boolean;
  work_arrangement?: 'remote' | 'hybrid' | 'onsite' | 'flexible';
  salary_min?: number;
  salary_max?: number;
  company_size_preference?: string[];
  auto_apply_enabled: boolean;
  home_latitude?: number;
  home_longitude?: number;
}

export interface ApplyToJobRequest {
  user_id: string;
  job_id: string;
  auto_tailor?: boolean;
  auto_cover_letter?: boolean;
  custom_message?: string;
}

export interface ApplyToJobResponse {
  success: boolean;
  application_id: string;
  job_title: string;
  company: string;
  tailored_resume?: any;
  cover_letter?: any;
  apply_url?: string;
  message: string;
}

// UI-specific types
export interface JobFilters {
  minSkillMatch: number; // 0-100
  maxDistance: number | null; // km
  seniority: string[];
  locationType: ('remote' | 'onsite' | 'hybrid')[];
  minSalary: number | null;
  maxAIRisk: number | null; // 0-100
  industries: string[];
  expandSearch: boolean;
}

export type AIRiskLevel = 'very-low' | 'low' | 'medium' | 'high' | 'very-high';

export interface AIRiskBadge {
  level: AIRiskLevel;
  percentage: number;
  label: string;
  color: string;
}

export function getAIRiskBadge(risk: number): AIRiskBadge {
  if (risk < 15) {
    return {
      level: 'very-low',
      percentage: risk,
      label: 'Very Low Risk',
      color: 'green',
    };
  } else if (risk < 30) {
    return {
      level: 'low',
      percentage: risk,
      label: 'Low Risk',
      color: 'blue',
    };
  } else if (risk < 50) {
    return {
      level: 'medium',
      percentage: risk,
      label: 'Medium Risk',
      color: 'yellow',
    };
  } else if (risk < 70) {
    return {
      level: 'high',
      percentage: risk,
      label: 'High Risk',
      color: 'orange',
    };
  } else {
    return {
      level: 'very-high',
      percentage: risk,
      label: 'Very High Risk',
      color: 'red',
    };
  }
}

// Additional type aliases for API compatibility
export type JobSearchQuery = JobSearchParams;

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  perPage: number;
  hasMore: boolean;
}

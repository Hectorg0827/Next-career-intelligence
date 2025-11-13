/**
 * Dashboard API Client
 *
 * API functions for fetching dashboard data
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Get authentication token from localStorage
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('token');
}

/**
 * Fetch with authentication
 */
async function authenticatedFetch(endpoint: string, options: RequestInit = {}) {
  const token = getAuthToken();

  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

/**
 * Career Health Score interfaces
 */
export interface CareerHealthScore {
  overall_score: number;
  grade: string;
  breakdown: {
    profile_completeness: number;
    skill_currency: number;
    market_activity: number;
    goal_progress: number;
    network_strength?: number;
  };
  recommendations: string[];
  trend?: 'improving' | 'stable' | 'declining';
}

export interface PriorityAction {
  type: 'warning' | 'opportunity';
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
}

export interface JobRecommendation {
  id: string;
  title: string;
  company: string;
  location: string;
  is_remote?: boolean;
  salary_min?: number;
  salary_max?: number;
  match_score: number;
  required_skills?: string[];
  skill_gaps?: string[];
}

/**
 * Fetch Career Health Score
 */
export async function fetchCareerHealthScore(): Promise<CareerHealthScore> {
  return authenticatedFetch('/api/career-health/score');
}

/**
 * Fetch Priority Actions
 */
export async function fetchPriorityActions(): Promise<{ actions: PriorityAction[] }> {
  return authenticatedFetch('/api/career-health/actions');
}

/**
 * Fetch Job Recommendations
 */
export async function fetchJobRecommendations(limit: number = 10): Promise<{ jobs: JobRecommendation[] }> {
  return authenticatedFetch(`/api/jobs/recommendations?limit=${limit}`);
}

/**
 * Refresh Career Health Score
 */
export async function refreshCareerHealthScore(): Promise<{ status: string; score: number; grade: string }> {
  return authenticatedFetch('/api/career-health/refresh', { method: 'POST' });
}

/**
 * Fetch complete dashboard data in parallel
 */
export async function fetchDashboardData() {
  try {
    const [healthScore, priorityActions, jobRecommendations] = await Promise.allSettled([
      fetchCareerHealthScore(),
      fetchPriorityActions(),
      fetchJobRecommendations(3),
    ]);

    return {
      healthScore: healthScore.status === 'fulfilled' ? healthScore.value : null,
      priorityActions: priorityActions.status === 'fulfilled' ? priorityActions.value.actions : [],
      jobRecommendations: jobRecommendations.status === 'fulfilled' ? jobRecommendations.value.jobs : [],
    };
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error);
    throw error;
  }
}

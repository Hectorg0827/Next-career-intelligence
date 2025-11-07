/**
 * API Client for backend communication
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import { OnboardingData } from '@/types/onboarding';
import { UserProfile } from '@/types/user';
import { Job, JobApplication, JobSearchQuery, PaginatedResponse } from '@/types/jobs';
import { ResumeData, ResumeFeedback, ResumeProfile } from '@/types/resume';
import type {
  AnalysisRequestPayload,
  AnalysisResult,
  CareerPath,
  CareerPathRequest,
  Goal,
  GoalRequest,
  Trajectory,
} from '@/types/intelligence';
import { Conversation, Message } from '@/types/coach';
import { InterviewSession } from '@/types/interviewer';

const PROD_BACKEND_URL = 'https://next-career-backend-795538981829.us-central1.run.app';
const LEGACY_BACKEND_FRAGMENT = 'next-backend-795538981829.us-central1.run.app';

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null;

const ensureArray = <T = unknown>(value: T | T[] | undefined | null): T[] => {
  if (value === undefined || value === null) {
    return [];
  }

  return Array.isArray(value) ? value : [value];
};

const getString = (record: Record<string, unknown>, key: string): string | undefined => {
  const value = record[key];
  return typeof value === 'string' ? value : undefined;
};

const getNumber = (record: Record<string, unknown>, key: string): number | undefined => {
  const value = record[key];
  return typeof value === 'number' ? value : undefined;
};

const getValue = <T = unknown>(record: Record<string, unknown>, key: string): T | undefined => {
  return record[key] as T | undefined;
};

const toReadableStrings = (entries: unknown): string[] =>
  ensureArray(entries)
    .map((item) => {
      if (item === null || item === undefined) {
        return '';
      }

      if (typeof item === 'string') {
        return item.trim();
      }

      if (typeof item === 'number') {
        return item.toString();
      }

      if (isRecord(item)) {
        if (typeof item.name === 'string' && item.importance) {
          return `${item.name} (importance ${item.importance})`;
        }

        if (typeof item.name === 'string' && item.growth) {
          return `${item.name} (${item.growth})`;
        }

        if (typeof item.title === 'string' && item.description) {
          return `${item.title}: ${item.description}`;
        }

        const joined = Object.values(item)
          .filter((value) => value !== null && value !== undefined && value !== '')
          .map((value) =>
            typeof value === 'string' || typeof value === 'number'
              ? value.toString()
              : ''
          )
          .filter(Boolean)
          .join(' • ');

        return joined || JSON.stringify(item);
      }

      return String(item);
    })
    .filter(Boolean);

const uniqueStrings = (values: string[]): string[] => Array.from(new Set(values));

type IndustryBenchmarks = Record<string, unknown>;

const normalizeAnalysisResult = (raw: Record<string, unknown>): AnalysisResult => {
  const normalized: AnalysisResult = { ...raw } as AnalysisResult;

  const riskCandidate = (raw['risk'] ?? raw['ai_displacement_risk']) as
    | Record<string, unknown>
    | undefined;

  if (isRecord(riskCandidate)) {
    normalized.risk = {
      level: getString(riskCandidate, 'level') ?? 'Unknown',
      score: getNumber(riskCandidate, 'score') ?? getNumber(riskCandidate, 'value'),
      justification: getString(riskCandidate, 'justification') ?? getString(riskCandidate, 'reasoning'),
      velocity: getString(riskCandidate, 'velocity'),
      augmentation_potential: getString(riskCandidate, 'augmentation_potential'),
    };
  }

  const compatibilityCandidate = raw['compatibility'] as Record<string, unknown> | number | undefined;
  const compatibilityHighlights = toReadableStrings(
    isRecord(compatibilityCandidate) ? getValue(compatibilityCandidate, 'highlights') : undefined
  );

  const metadataCandidate = (() => {
    const value = raw['metadata'] ?? raw['industry_benchmarks'];
    return isRecord(value) ? value : undefined;
  })();

  const benchmarksRecord =
    metadataCandidate && isRecord(getValue(metadataCandidate, 'benchmarks'))
      ? (getValue(metadataCandidate, 'benchmarks') as Record<string, unknown>)
      : undefined;

  const skillDemandRecord =
    benchmarksRecord && isRecord(getValue(benchmarksRecord, 'skill_demand'))
      ? (getValue(benchmarksRecord, 'skill_demand') as Record<string, unknown>)
      : undefined;

  const benchmarkHighlights = skillDemandRecord
    ? toReadableStrings(
        getValue(skillDemandRecord, 'top_skills') ?? getValue(skillDemandRecord, 'highlights')
      )
    : [];

  const humanAdvantageHighlights = toReadableStrings(raw['human_advantage_factors']);

  const allHighlights = uniqueStrings([
    ...compatibilityHighlights,
    ...humanAdvantageHighlights,
    ...benchmarkHighlights,
  ]);

  const compatibilityScore = (() => {
    if (isRecord(compatibilityCandidate)) {
      const score = getNumber(compatibilityCandidate, 'score');
      if (typeof score === 'number') {
        return score;
      }
    }

    if (typeof raw['compatibility_score'] === 'number') {
      return raw['compatibility_score'] as number;
    }

    if (typeof compatibilityCandidate === 'number') {
      return compatibilityCandidate;
    }

    return 0;
  })();

  normalized.compatibility = {
    score: compatibilityScore,
    highlights: allHighlights.length ? allHighlights : undefined,
  };

  const gaps = uniqueStrings([
    ...toReadableStrings(raw['gaps']),
    ...toReadableStrings(raw['skill_gaps']),
  ]);
  if (gaps.length) {
    normalized.gaps = gaps;
  }

  const nextSteps = uniqueStrings([
    ...toReadableStrings(raw['next_steps']),
    ...toReadableStrings(raw['recommended_training']),
  ]);
  if (nextSteps.length) {
    normalized.next_steps = nextSteps;
  }

  const coachQuestions = uniqueStrings([
    ...toReadableStrings(raw['coach_questions']),
    ...toReadableStrings(raw['transition_pathways']),
  ]);
  if (coachQuestions.length) {
    normalized.coach_questions = coachQuestions;
  }

  if (metadataCandidate) {
    if (benchmarksRecord) {
      normalized.industry_benchmarks = benchmarksRecord as IndustryBenchmarks;
    } else {
      normalized.industry_benchmarks = metadataCandidate as IndustryBenchmarks;
    }
  } else if (isRecord(raw['industry_benchmarks'])) {
    normalized.industry_benchmarks = raw['industry_benchmarks'] as IndustryBenchmarks;
  }

  return normalized;
};

const resolveApiBaseUrl = () => {
  const envValue = process.env.NEXT_PUBLIC_API_URL?.trim();

  if (envValue) {
    const normalized = envValue.replace(/\/$/, '');

    if (normalized.includes(LEGACY_BACKEND_FRAGMENT)) {
      console.warn('Detected legacy Cloud Run host in NEXT_PUBLIC_API_URL. Falling back to next-career-backend service.');
      return PROD_BACKEND_URL;
    }

    return normalized;
  }

  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:8000';
  }

  if (process.env.VERCEL === '1' || process.env.NODE_ENV === 'production') {
    return PROD_BACKEND_URL;
  }

  return '';
};

const API_URL = resolveApiBaseUrl();

class APIClient {
  public client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_URL}/api`.replace('//api', '/api'),
      timeout: 180000, // 3 minutes for long AI analysis
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.client.interceptors.request.use(
      (config) => {
        if (typeof window !== 'undefined') {
          const token = localStorage.getItem('authToken');
          if (token) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401 && typeof window !== 'undefined') {
          localStorage.removeItem('authToken');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // ============================================
  // Health Check
  // ============================================
  async healthCheck(): Promise<unknown> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // ============================================
  // Onboarding & User Profile
  // ============================================
  async submitOnboarding(data: OnboardingData): Promise<UserProfile> {
    const response = await this.client.post('/users/onboarding', data);
    return response.data;
  }

  async getUserProfile(): Promise<UserProfile> {
    const response = await this.client.get('/users/profile');
    return response.data;
  }

  async updateUserProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    const response = await this.client.patch('/users/profile', data);
    return response.data;
  }

  async deleteUser(firebaseUid: string): Promise<void> {
    await this.client.delete(`/users/${firebaseUid}`);
  }

  // ============================================
  // Career Intelligence & Analysis
  // ============================================
  async analyzeCareer(payload: AnalysisRequestPayload): Promise<AnalysisResult> {
    const response = await this.client.post('/analyze', payload);
    return normalizeAnalysisResult(response.data as Record<string, unknown>);
  }

  async generateCareerTrajectory(data: { job_title: string; years_experience: number; }): Promise<Trajectory> {
    const response = await this.client.post('/analyze/trajectory', data);
    return response.data;
  }

  async generateCareerPaths(data: CareerPathRequest): Promise<CareerPath[]> {
    const response = await this.client.post('/analyze', data);
    return response.data;
  }

  // ============================================
  // Jobs Marketplace
  // ============================================
  async searchJobs(params: JobSearchQuery): Promise<PaginatedResponse<Job>> {
    const response = await this.client.get('/jobs/search', { params });
    return response.data;
  }

  async getJobDetails(jobId: string): Promise<Job> {
    const response = await this.client.get(`/jobs/${jobId}`);
    return response.data;
  }

  async applyForJob(jobId: string, applicationData: Record<string, unknown>): Promise<JobApplication> {
    const response = await this.client.post(`/jobs/${jobId}/apply`, applicationData);
    return response.data;
  }
  
  async getSavedJobs(): Promise<Job[]> {
      const response = await this.client.get('/jobs/saved');
      return response.data;
  }

  async saveJob(jobId: string): Promise<{ message: string }> {
      const response = await this.client.post(`/jobs/${jobId}/save`);
      return response.data;
  }

  async unsaveJob(jobId: string): Promise<{ message: string }> {
      const response = await this.client.delete(`/jobs/${jobId}/unsave`);
      return response.data;
  }

  async getJobRecommendations(): Promise<Job[]> {
      const response = await this.client.get('/jobs/recommendations');
      return response.data;
  }
  
  async getAppliedJobs(): Promise<JobApplication[]> {
      const response = await this.client.get('/jobs/applications');
      return response.data;
  }

  // ============================================
  // Resume Studio
  // ============================================
  async uploadResume(file: File): Promise<ResumeData> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post('/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async getResumeProfile(): Promise<ResumeProfile> {
    const response = await this.client.get('/resume/profile');
    return response.data;
  }

  async getResumeSuggestions(jobDescription: string): Promise<ResumeFeedback> {
    const response = await this.client.post('/resume/suggestions', { job_description: jobDescription });
    return response.data;
  }

  // ============================================
  // AI Career Coach
  // ============================================
  async getCoachConversations(): Promise<Conversation[]> {
    const response = await this.client.get('/coach/conversations');
    return response.data;
  }

  async startCoachConversation(topic: string): Promise<Conversation> {
    const response = await this.client.post('/coach/conversations', { topic });
    return response.data;
  }

  async coachChat(conversationId: string, message: string): Promise<Message> {
    const response = await this.client.post(`/coach/conversations/${conversationId}/chat`, { message });
    return response.data;
  }

  async getGoals(): Promise<Goal[]> {
    const response = await this.client.get('/coach/goals');
    return response.data;
  }

  async createGoal(goal: GoalRequest): Promise<Goal> {
    const response = await this.client.post('/coach/goals', goal);
    return response.data;
  }

  async updateGoal(goalId: string, updates: Partial<GoalRequest>): Promise<Goal> {
    const response = await this.client.patch(`/coach/goals/${goalId}`, updates);
    return response.data;
  }

  async deleteGoal(goalId: string): Promise<{ message: string }> {
    const response = await this.client.delete(`/coach/goals/${goalId}`);
    return response.data;
  }

  // ============================================
  // AI Interviewer
  // ============================================
  async createInterviewSession(setup: { job_title: string; interview_type: string; focus_areas: string[] }): Promise<InterviewSession> {
    const response = await this.client.post('/interviewer/sessions', setup);
    return response.data;
  }

  async getInterviewSessions(): Promise<InterviewSession[]> {
    const response = await this.client.get('/interviewer/sessions');
    return response.data;
  }

  async getInterviewSession(sessionId: string): Promise<InterviewSession> {
    const response = await this.client.get(`/interviewer/sessions/${sessionId}`);
    return response.data;
  }

  async submitInterviewResponse(sessionId: string, response: Record<string, unknown>): Promise<unknown> {
    const res = await this.client.post(`/interviewer/sessions/${sessionId}/responses`, response);
    return res.data;
  }

  // ============================================
  // Authentication (delegates to Firebase)
  // ============================================
  async requestPasswordReset(data: { email: string }): Promise<never> {
    void data;
    // This should be handled by Firebase, but for API compatibility
    throw new Error('Use Firebase resetPassword instead');
  }

  async resetPassword(payload: {
    email: string;
    reset_code: string;
    new_password: string;
    confirm_password: string;
  }): Promise<never> {
    void payload;
    // This should be handled by Firebase, but for API compatibility
    throw new Error('Use Firebase confirmPasswordReset instead');
  }

  async verifyEmail(data: { email: string; verification_code: string }): Promise<never> {
    void data;
    // This should be handled by Firebase, but for API compatibility
    throw new Error('Use Firebase email verification instead');
  }

  async resendVerificationCode(data: { email: string }): Promise<never> {
    void data;
    // This should be handled by Firebase, but for API compatibility
    throw new Error('Use Firebase sendEmailVerification instead');
  }

  // ============================================
  // Subscription Management
  // ============================================
  async getSubscriptionStatus(userId: string): Promise<unknown> {
    const response = await this.client.get(`/subscriptions/status/${userId}`);
    return response.data;
  }

  async createSubscription(data: Record<string, unknown>): Promise<unknown> {
    const response = await this.client.post('/subscriptions', data);
    return response.data;
  }

  async cancelSubscription(subscriptionId: string): Promise<unknown> {
    const response = await this.client.delete(`/subscriptions/${subscriptionId}`);
    return response.data;
  }

  async createPortalSession(): Promise<unknown> {
    const response = await this.client.post('/subscriptions/portal');
    return response.data;
  }
}

const apiClient = new APIClient();

// Grouped exports for easier importing
export const intelligenceApi = {
  analyzeCareer: apiClient.analyzeCareer.bind(apiClient),
  generateCareerTrajectory: apiClient.generateCareerTrajectory.bind(apiClient),
  generateCareerPaths: apiClient.generateCareerPaths.bind(apiClient),
};

export const jobsApi = {
  searchJobs: apiClient.searchJobs.bind(apiClient),
  getJobDetails: apiClient.getJobDetails.bind(apiClient),
  applyForJob: apiClient.applyForJob.bind(apiClient),
  getSavedJobs: apiClient.getSavedJobs.bind(apiClient),
  saveJob: apiClient.saveJob.bind(apiClient),
  unsaveJob: apiClient.unsaveJob.bind(apiClient),
  getJobRecommendations: apiClient.getJobRecommendations.bind(apiClient),
  getAppliedJobs: apiClient.getAppliedJobs.bind(apiClient),
};

export const resumeApi = {
  uploadResume: apiClient.uploadResume.bind(apiClient),
  getResumeProfile: apiClient.getResumeProfile.bind(apiClient),
  getResumeSuggestions: apiClient.getResumeSuggestions.bind(apiClient),
};

export const coachApi = {
  getCoachConversations: apiClient.getCoachConversations.bind(apiClient),
  startCoachConversation: apiClient.startCoachConversation.bind(apiClient),
  coachChat: apiClient.coachChat.bind(apiClient),
  getGoals: apiClient.getGoals.bind(apiClient),
  createGoal: apiClient.createGoal.bind(apiClient),
  updateGoal: apiClient.updateGoal.bind(apiClient),
  deleteGoal: apiClient.deleteGoal.bind(apiClient),
};

export const interviewerApi = {
  createInterviewSession: apiClient.createInterviewSession.bind(apiClient),
  getInterviewSessions: apiClient.getInterviewSessions.bind(apiClient),
  getInterviewSession: apiClient.getInterviewSession.bind(apiClient),
  submitInterviewResponse: apiClient.submitInterviewResponse.bind(apiClient),
};

export const userApi = {
    submitOnboarding: apiClient.submitOnboarding.bind(apiClient),
    getUserProfile: apiClient.getUserProfile.bind(apiClient),
    updateUserProfile: apiClient.updateUserProfile.bind(apiClient),
    deleteUser: apiClient.deleteUser.bind(apiClient),
};

export const subscriptionApi = {
  getSubscriptionStatus: apiClient.getSubscriptionStatus.bind(apiClient),
  createSubscription: apiClient.createSubscription.bind(apiClient),
  cancelSubscription: apiClient.cancelSubscription.bind(apiClient),
  createPortalSession: apiClient.createPortalSession.bind(apiClient),
};

// Default export for general use
export default apiClient;
// For backward compatibility with previous imports
export const getCoachConversations = apiClient.getCoachConversations.bind(apiClient);
export const coachChat = apiClient.coachChat.bind(apiClient);

// Backward compatibility exports
export const analyzeCareer = apiClient.analyzeCareer.bind(apiClient);
export const generateCareerRoadmap = apiClient.generateCareerPaths.bind(apiClient); // Map to existing method
// Export the apiClient instance as a named export (do not re-declare)
export { apiClient };


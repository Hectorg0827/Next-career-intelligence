/**
 * API Client for backend communication
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import { OnboardingData } from '@/types/onboarding';
import { UserProfile } from '@/types/user';
import { Job, JobApplication, JobSearchQuery, PaginatedResponse } from '@/types/jobs';
import { ResumeData, ResumeFeedback, ResumeProfile } from '@/types/resume';
import { AnalysisResult, CareerPath, CareerPathRequest, Goal, GoalRequest, Trajectory } from '@/types/intelligence';
import { Conversation, Message } from '@/types/coach';
import { InterviewSession, SessionFeedback } from '@/types/interviewer';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  public client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_URL}/api`,
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
  async healthCheck(): Promise<any> {
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

  // ============================================
  // Career Intelligence & Analysis
  // ============================================
  async analyzeCareer(data: { job_title: string; skills: string[]; location: string; }): Promise<AnalysisResult> {
    const response = await this.client.post('/analyze/career', data);
    return response.data;
  }

  async generateCareerTrajectory(data: { job_title: string; years_experience: number; }): Promise<Trajectory> {
    const response = await this.client.post('/analyze/trajectory', data);
    return response.data;
  }

  async generateCareerPaths(data: CareerPathRequest): Promise<CareerPath[]> {
    const response = await this.client.post('/analyze/career-paths', data);
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

  async applyForJob(jobId: string, applicationData: any): Promise<JobApplication> {
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

  async submitInterviewResponse(sessionId: string, response: any): Promise<any> {
    const res = await this.client.post(`/interviewer/sessions/${sessionId}/responses`, response);
    return res.data;
  }

  // ============================================
  // Authentication (delegates to Firebase)
  // ============================================
  async requestPasswordReset(data: { email: string }): Promise<any> {
    // This should be handled by Firebase, but for API compatibility
    throw new Error('Use Firebase resetPassword instead');
  }

  async resetPassword(data: { email: string; reset_code: string; new_password: string; confirm_password: string }): Promise<any> {
    // This should be handled by Firebase, but for API compatibility
    throw new Error('Use Firebase confirmPasswordReset instead');
  }

  async verifyEmail(data: { email: string; verification_code: string }): Promise<any> {
    // This should be handled by Firebase, but for API compatibility
    throw new Error('Use Firebase email verification instead');
  }

  async resendVerificationCode(data: { email: string }): Promise<any> {
    // This should be handled by Firebase, but for API compatibility
    throw new Error('Use Firebase sendEmailVerification instead');
  }

  // ============================================
  // Subscription Management
  // ============================================
  async getSubscriptionStatus(userId: string): Promise<any> {
    const response = await this.client.get(`/subscriptions/status/${userId}`);
    return response.data;
  }

  async createSubscription(data: any): Promise<any> {
    const response = await this.client.post('/subscriptions', data);
    return response.data;
  }

  async cancelSubscription(subscriptionId: string): Promise<any> {
    const response = await this.client.delete(`/subscriptions/${subscriptionId}`);
    return response.data;
  }

  async createPortalSession(): Promise<any> {
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


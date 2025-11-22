// API client for jobs marketplace

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  remote_policy?: string;
  employment_type?: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency?: string;
  description: string;
  required_skills?: string[];
  posted_at?: string;
  apply_url?: string;
  source?: string;
  external_url?: string;
  match_score?: number;
  displacement_risk?: number;
  goal_alignment?: number;
}

export interface JobsResponse {
  jobs: Job[];
  total: number;
  page: number;
  page_size: number;
}

export interface JobSearchParams {
  query?: string;
  location?: string;
  remote_type?: string;
  min_salary?: number;
  max_salary?: number;
  experience_level?: string;
  skills?: string[];
  job_type?: string;
  page?: number;
  limit?: number;
}

export const jobsApi = {
  /**
   * Search jobs with filters
   */
  async searchJobs(params: JobSearchParams = {}): Promise<JobsResponse> {
    const searchParams = new URLSearchParams();
    
    if (params.query) searchParams.append('query', params.query);
    if (params.location) searchParams.append('location', params.location);
    if (params.remote_type) searchParams.append('remote_type', params.remote_type);
    if (params.min_salary) searchParams.append('min_salary', params.min_salary.toString());
    if (params.max_salary) searchParams.append('max_salary', params.max_salary.toString());
    if (params.experience_level) searchParams.append('experience_level', params.experience_level);
    if (params.job_type) searchParams.append('job_type', params.job_type);
    if (params.skills) params.skills.forEach(skill => searchParams.append('skills', skill));
    searchParams.append('page', (params.page || 1).toString());
    searchParams.append('limit', (params.limit || 20).toString());

    const response = await fetch(`${API_BASE}/api/v1/marketplace/jobs?${searchParams}`, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch jobs');
    }

    const data = await response.json();
    return {
      jobs: data.jobs || [],
      total: data.total || 0,
      page: params.page || 1,
      page_size: params.limit || 20,
    };
  },

  /**
   * Get job details by ID
   */
  async getJob(jobId: string): Promise<Job> {
    const response = await fetch(`${API_BASE}/api/v1/marketplace/jobs/${jobId}`, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch job');
    }

    return response.json();
  },

  /**
   * Trigger job aggregator to fetch new jobs
   */
  async triggerAggregator(): Promise<{ status: string; message: string; sources: string[] }> {
    const response = await fetch(`${API_BASE}/api/job-scraper/run-aggregated`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to trigger job aggregator');
    }

    return response.json();
  },

  /**
   * Get aggregator health status
   */
  async getAggregatorHealth(): Promise<{
    status: string;
    total_active_jobs: number;
    stale_jobs_7d: number;
    last_check: string;
  }> {
    const response = await fetch(`${API_BASE}/api/job-scraper/health`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to get aggregator health');
    }

    return response.json();
  },

  /**
   * Apply to a job
   */
  async applyToJob(jobId: string, coverLetter?: string): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE}/api/v1/marketplace/jobs/${jobId}/apply`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ cover_letter: coverLetter }),
    });

    if (!response.ok) {
      throw new Error('Failed to apply to job');
    }

    return response.json();
  },

  /**
   * Save a job for later
   */
  async saveJob(jobId: string): Promise<{ success: boolean }> {
    const response = await fetch(`${API_BASE}/api/v1/marketplace/saved-jobs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ job_id: jobId }),
    });

    if (!response.ok) {
      throw new Error('Failed to save job');
    }

    return response.json();
  },
};

export interface AnalysisRequestPayload {
  job_title: string;
  skills: string[];
  location?: string;
  years_experience?: number;
  timeline?: string;
  additional_context?: Record<string, unknown>;
}

export interface RiskAssessment {
  level: string;
  score?: number;
  justification?: string;
  reasoning?: string;
  velocity?: string;
  augmentation_potential?: string;
  [key: string]: unknown;
}

export interface CompatibilityInsight {
  score?: number;
  highlights?: string[];
  methodology?: string;
  [key: string]: unknown;
}

export interface TrainingRecommendation {
  title: string;
  provider?: string;
  url?: string;
  duration?: string;
  skill_covered?: string;
  investment_level?: string;
  summary?: string;
  [key: string]: unknown;
}

export interface IndustryBenchmarks {
  industry?: string;
  region?: string;
  benchmarks?: Record<string, unknown>;
  published_at?: string;
  source?: string;
  [key: string]: unknown;
}

export interface AnalysisResult {
  analysis_id?: string;
  job_title?: string;
  summary?: string;
  risk?: RiskAssessment;
  ai_displacement_risk?: RiskAssessment;
  compatibility?: CompatibilityInsight;
  compatibility_score?: number;
  human_advantage_factors?: string[];
  gaps?: string[];
  skill_gaps?: string[];
  next_steps?: string[];
  recommended_training?: TrainingRecommendation[];
  coach_questions?: string[];
  transition_pathways?: Array<Record<string, unknown>>;
  industry_benchmarks?: IndustryBenchmarks;
  metadata?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface CareerPath {
  title: string;
  description?: string;
  probability?: number;
  timeline?: string;
  target_role?: string;
  highlights?: string[];
  metrics?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface CareerPathRequest {
  job_title: string;
  skills?: string[];
  location?: string;
  years_experience?: number;
  timeline?: string;
  preferences?: Record<string, unknown>;
}

export interface Goal {
  id: string;
  title: string;
  description?: string;
  completed?: boolean;
  created_at?: string;
  updated_at?: string;
  metadata?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface GoalRequest {
  title: string;
  description?: string;
  due?: string;
  category?: string;
  metadata?: Record<string, unknown>;
  [key: string]: unknown;
}

export type TrajectoryNode = {
  title: string;
  description?: string;
  probability?: number;
  timeline?: string;
  target_role?: string;
  role?: string;
  milestones?: string[];
  [key: string]: unknown;
};

export type Trajectory = TrajectoryNode[];

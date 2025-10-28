// Minimal type definitions to satisfy imports during build
// Expand these definitions with actual shapes when available.

export interface AnalysisResult {
  summary?: string;
  industry_benchmarks?: any;
  [key: string]: any;
}

export interface CareerPath {
  id?: string;
  title?: string;
  description?: string;
  timeline?: any;
  [key: string]: any;
}

export type CareerPathRequest = {
  job_title: string;
  skills?: string[];
  location?: string;
  years_experience?: number;
  timeline?: string;
  [key: string]: any;
};

export interface Goal {
  id?: string;
  title: string;
  description?: string;
  completed?: boolean;
  [key: string]: any;
}

export type GoalRequest = {
  title: string;
  description?: string;
  due?: string;
  [key: string]: any;
};

export type Trajectory = {
  [key: string]: any;
};

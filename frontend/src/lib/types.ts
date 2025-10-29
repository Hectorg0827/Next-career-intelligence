/**
 * TypeScript types and interfaces
 */

export interface AnalysisRequest {
  job_title: string;
  skills: string[];
  location: string;
  years_experience?: number;
}

export type RiskLevel = 'Low' | 'Medium' | 'High' | 'Critical';

export interface AIDisplacementRisk {
  level: RiskLevel;
  score: number;
  velocity: string;
  augmentation_potential: string;
  reasoning?: string;
}

export interface TransitionPathway {
  role: string;
  ease: number;
  required_skills: string[];
  estimated_training_time?: string;
  salary_potential?: string;
  demand_trend?: string;
}

export interface TrainingResource {
  title: string;
  provider: string;
  url: string;
  duration?: string;
  skill_covered: string;
  cost?: string;
  rating?: number;
}

export interface AnalysisResponse {
  analysis_id: string;
  job_title: string;
  ai_displacement_risk: AIDisplacementRisk;
  compatibility_score: number;
  human_advantage_factors: string[];
  transition_pathways: TransitionPathway[];
  skill_gaps: string[];
  recommended_training: TrainingResource[];
  created_at: string;
  metadata?: Record<string, any>;
  skill_insights?: {
    transferable_skills: string[];
    hidden_skills: string[];
    skill_clusters: {
      cluster_name: string;
      skills: string[];
      strength_score: number;
    }[];
    skill_gaps_analysis: {
      critical_gaps: string[];
      development_priority: string[];
      time_to_competency: string;
    };
    skill_strength_score?: {
      overall_score: number;
      breakdown: {
        technical: number;
        soft: number;
        domain: number;
      };
      interpretation: string;
    };
    transferable_to?: {
      skill: string;
      confidence: number;
      target_roles: string[];
      reasoning: string;
      source_skills: string[];
    }[];
    skill_gaps_for_growth?: {
      skill: string;
      priority: 'Critical' | 'High' | 'Medium' | 'Low';
      time_to_develop: string;
      resources: string[];
      why_important: string;
      estimated_learning_time: string;
      market_demand: string;
      learn_difficulty: string;
    }[];
  };
}

export interface JobSuggestion {
  code: string;
  title: string;
  description?: string;
}

export interface UserProfile {
  id: string;
  email: string;
  name?: string;
  created_at: string;
}

export interface AnalysisHistoryItem {
  analysis_id: string;
  job_title: string;
  risk_score: number;
  compatibility_score: number;
  created_at: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
  services: Record<string, string>;
}

// Additional types for dashboard features
export interface CareerAnalysis extends AnalysisResponse {}

export interface CareerRoadmapResponse {
  roadmap_id: string;
  job_title: string;
  timeline: string;
  pathways: TransitionPathway[];
  milestones: {
    phase: string;
    timeframe: string;
    objectives: string[];
    skills_to_develop: string[];
    resources_needed: TrainingResource[];
  }[];
  risk_assessment: AIDisplacementRisk;
  created_at: string;
  career_roadmap: {
    "3_year": {
      primary_path: {
        target_role: string;
        milestone_title: string;
        description: string;
        skills_to_develop?: string[];
        certifications?: string[];
        estimated_salary_range?: string;
        ai_resilience_score?: number;
      };
      alternative_paths: string[];
      skills_needed: string[];
      salary_projection: string;
    };
    "5_year": {
      primary_path: {
        target_role: string;
        milestone_title: string;
        description: string;
        skills_to_develop?: string[];
        certifications?: string[];
        estimated_salary_range?: string;
        ai_resilience_score?: number;
      };
      alternative_paths: string[];
      skills_needed: string[];
      salary_projection: string;
    };
    "10_year": {
      primary_path: {
        target_role: string;
        milestone_title: string;
        description: string;
        skills_to_develop?: string[];
        certifications?: string[];
        estimated_salary_range?: string;
        ai_resilience_score?: number;
      };
      alternative_paths: string[];
      skills_needed: string[];
      salary_projection: string;
    };
  };
}

export interface SankeyData {
  nodes: {
    id: number;
    name: string;
    category: 'current' | '3-year' | '3-year-alt' | '5-year' | '5-year-alt' | '10-year' | '10-year-alt';
  }[];
  links: {
    source: number;
    target: number;
    value: number;
    skill: string;
  }[];
}

export interface IndustryBenchmarks {
  industry: string;
  average_risk_score: number;
  top_risks: string[];
  emerging_trends: string[];
  salary_ranges: {
    entry: number;
    mid: number;
    senior: number;
  };
  demand_forecast: string;
  benchmarks?: {
    automation_risk_comparison: {
      your_score: number;
      industry_average: number;
      percentile: number;
      comparison_text: string;
      trend: "improving" | "declining" | "stable";
    };
    skill_demand?: {
      high_demand_skills: string[];
      emerging_skills: string[];
      declining_skills: string[];
      skill_gap_score: number;
      overall_score: number;
      top_skills: {
        skill: string;
        demand_score: number;
        growth_rate: string;
      }[];
      skill_gaps: {
        skill: string;
        importance: 'high' | 'medium' | 'low';
        demand_score: number;
      }[];
    };
    salary_benchmark?: {
      your_estimated_range: string;
      industry_median: string;
      percentile_25: string;
      percentile_50: string;
      percentile_75: string;
      percentile_90: string;
      your_position: string;
    };
    market_trends?: {
      trend_direction: "up" | "down" | "stable";
      growth_rate: string;
      demand_change: string;
      emerging_roles: string[];
      role_growth: string;
      hiring_difficulty: 'high' | 'medium' | 'low';
      remote_availability: string;
      top_hiring_industries: string[];
      career_pace: string;
      typical_years_to_next_level: number;
      readiness_score: number;
    };
    career_progression?: {
      next_roles: string[];
      time_to_promotion: string;
      skill_requirements: string[];
      salary_progression: string[];
      pace: string;
      typical_years_to_next_level: number;
      your_readiness_score: number;
    };
    competitive_position?: {
      overall_ranking: string;
      strengths: string[];
      weaknesses: string[];
      market_value: string;
      peer_ranking: string;
      areas_for_improvement: string[];
    };
  };
}

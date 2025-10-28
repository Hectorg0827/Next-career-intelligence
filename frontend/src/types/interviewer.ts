// Minimal interviewer types
export interface InterviewSession {
  id?: string;
  job_title?: string;
  interview_type?: string;
  focus_areas?: string[];
  created_at?: string | Date;
  [key: string]: any;
}

export interface SessionFeedback {
  id?: string;
  sessionId?: string;
  feedback?: string;
  rating?: number;
  [key: string]: any;
}

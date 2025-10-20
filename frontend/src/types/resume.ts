/**
 * Resume Studio Types
 * Single Source of Truth (SSOT) for career profiles
 */

export interface CareerProfile {
  id: string;
  user_id: string;
  profile_data: ProfileData;
  version: number;
  created_at: string;
  updated_at: string;
  metadata?: ProfileMetadata;
}

export interface ProfileData {
  personal_info: PersonalInfo;
  summary?: string;
  skills: Skills;
  work_history: WorkExperience[];
  education: Education[];
  certifications?: Certification[];
  projects?: Project[];
  publications?: Publication[];
  languages?: Language[];
  volunteer?: VolunteerExperience[];
  awards?: Award[];
}

export interface PersonalInfo {
  full_name: string;
  email: string;
  phone?: string;
  location_city?: string;
  location_state?: string;
  location_country?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  latitude?: number;
  longitude?: number;
}

export interface Skills {
  hard: string[];
  soft: string[];
  tools?: string[];
  languages_programming?: string[];
}

export interface WorkExperience {
  id?: string;
  title: string;
  company: string;
  location?: string;
  start_date: string; // YYYY-MM format
  end_date?: string; // YYYY-MM format or "present"
  is_current: boolean;
  description?: string;
  achievements: string[]; // Bullet points
  tech_stack?: string[];
  highlights?: string[];
}

export interface Education {
  id?: string;
  degree: string;
  field_of_study: string;
  institution: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  gpa?: string;
  honors?: string[];
  relevant_coursework?: string[];
}

export interface Certification {
  id?: string;
  name: string;
  issuing_organization: string;
  issue_date?: string;
  expiry_date?: string;
  credential_id?: string;
  credential_url?: string;
}

export interface Project {
  id?: string;
  name: string;
  description: string;
  role?: string;
  start_date?: string;
  end_date?: string;
  tech_stack?: string[];
  url?: string;
  github_url?: string;
  highlights?: string[];
}

export interface Publication {
  id?: string;
  title: string;
  publication_venue?: string;
  date?: string;
  url?: string;
  authors?: string[];
}

export interface Language {
  language: string;
  proficiency: 'native' | 'fluent' | 'professional' | 'intermediate' | 'basic';
}

export interface VolunteerExperience {
  id?: string;
  role: string;
  organization: string;
  start_date?: string;
  end_date?: string;
  description?: string;
  achievements?: string[];
}

export interface Award {
  id?: string;
  title: string;
  issuer?: string;
  date?: string;
  description?: string;
}

export interface ProfileMetadata {
  last_modified_by?: string; // Source of last change
  sources?: string[]; // Provenance tracking
  ai_displacement_risk?: {
    score: number;
    last_calculated: string;
  };
}

// Suggestions
export interface ProfileSuggestion {
  id: string;
  profile_id: string;
  suggestion_type: SuggestionType;
  suggested_data: any; // JSON object
  reasoning?: string;
  source: string; // 'coach', 'interviewer', 'auto'
  status: 'pending' | 'accepted' | 'rejected';
  created_at: string;
  reviewed_at?: string;
}

export type SuggestionType =
  | 'add_experience_bullet'
  | 'update_experience_bullet'
  | 'add_skill'
  | 'add_project'
  | 'update_summary'
  | 'add_achievement'
  | 'add_certification'
  | 'improve_wording';

// Resume Artifacts
export interface ResumeArtifact {
  id: string;
  profile_id: string;
  artifact_type: 'tailored_resume' | 'cover_letter' | 'base_resume';
  content: any; // JSON or text
  format?: 'json' | 'markdown' | 'html';
  job_id?: string; // For tailored resumes
  is_active: boolean;
  created_at: string;
  metadata?: {
    job_title?: string;
    company?: string;
    customizations?: string[];
  };
}

// Ingest Request
export interface IngestResumeRequest {
  user_id: string;
  text?: string;
  file?: File;
}

export interface IngestResumeResponse {
  success: boolean;
  profile_id: string;
  profile: CareerProfile;
  open_questions?: string[];
  confidence_score?: number;
  message: string;
}

// Tailor Request
export interface TailorResumeRequest {
  user_id: string;
  job_description: string;
  job_title?: string;
  company_name?: string;
  job_id?: string;
}

export interface TailorResumeResponse {
  success: boolean;
  artifact_id: string;
  tailored_resume: any;
  customizations: string[];
  message: string;
}

// Cover Letter Request
export interface TailorCoverLetterRequest {
  user_id: string;
  job_description: string;
  job_title?: string;
  company_name?: string;
  job_id?: string;
  tailored_resume_id?: string;
}

export interface TailorCoverLetterResponse {
  success: boolean;
  artifact_id: string;
  cover_letter: any;
  message: string;
}

// Apply Suggestion
export interface ApplySuggestionRequest {
  user_id: string;
  suggestion_id: string;
  accept: boolean;
}

export interface ApplySuggestionResponse {
  success: boolean;
  profile_id: string;
  updated_profile?: CareerProfile;
  message: string;
}

// UI State
export interface ResumeUploadState {
  step: 'upload' | 'parsing' | 'review' | 'complete';
  file?: File;
  uploadProgress: number;
  parsedProfile?: CareerProfile;
  openQuestions?: string[];
  error?: string;
}

export interface ProfileEditState {
  isEditing: boolean;
  section?: keyof ProfileData;
  originalData?: any;
  editedData?: any;
}

// File validation
export function validateResumeFile(file: File): { valid: boolean; error?: string } {
  const maxSize = 10 * 1024 * 1024; // 10MB
  const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];

  if (file.size > maxSize) {
    return { valid: false, error: 'File size must be under 10MB' };
  }

  if (!allowedTypes.includes(file.type)) {
    return { valid: false, error: 'Only PDF, DOCX, and TXT files are supported' };
  }

  return { valid: true };
}

// Format helpers
export function formatDate(dateStr?: string): string {
  if (!dateStr) return 'Present';
  if (dateStr.toLowerCase() === 'present') return 'Present';

  try {
    const [year, month] = dateStr.split('-');
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return `${monthNames[parseInt(month) - 1]} ${year}`;
  } catch {
    return dateStr;
  }
}

export function calculateDuration(startDate: string, endDate?: string): string {
  const start = new Date(startDate + '-01');
  const end = endDate && endDate.toLowerCase() !== 'present' ? new Date(endDate + '-01') : new Date();

  const months = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth());
  const years = Math.floor(months / 12);
  const remainingMonths = months % 12;

  if (years === 0) {
    return `${remainingMonths} month${remainingMonths !== 1 ? 's' : ''}`;
  } else if (remainingMonths === 0) {
    return `${years} year${years !== 1 ? 's' : ''}`;
  } else {
    return `${years} year${years !== 1 ? 's' : ''}, ${remainingMonths} month${remainingMonths !== 1 ? 's' : ''}`;
  }
}

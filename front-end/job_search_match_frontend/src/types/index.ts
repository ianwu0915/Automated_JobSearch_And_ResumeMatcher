//Auth Types
export type User = {
  user_id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  role: string;
};

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  full_name: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Resume Types
export interface Resume {
  resume_id: string;
  user_id: string;
  features: ResumeFeatures;
  raw_text: string;
  processed_date: string;
}

export interface ResumeFeatures {
  work_experience_years: number;
  skills: string[];
  word_frequencies: Record<string, number>;
}

// Job Types
export interface Job {
  job_id: string;
  title: string;
  company: string;
  location: string;
  workplace_type: string;
  listed_time: string;
  apply_url: string;  
  description: string;
  features: JobFeatures;
  processed_date: string;
}

export interface JobFeatures {
  required_experience_years: number;
  skills: string[];
  word_frequencies: Record<string, number>;
}

// For current Search Results
export interface JobMatch {
  resume_id: string;
  job_id: string;
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  required_experience_years: number;
  resume_experience_years: number;
  job: Job;
}

// For Job Match History
export interface JobMatchCardType {
  id: string;
  apply_url: string;
  company: string;
  created_at: string;
  job_id: string;
  listed_time: string;
  location: string;
  workplace_type: string;
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  required_experience_years: number;
  resume_experience_years: number;
  resume_id: string;
  title: string;
}

export interface JobSearchParams {
  keywords: string;
  location_name: string;
  experience_level: string[];
  job_type: string[];
  remote: string[];
  limit: number;
  user_id: string;
}

// API Types
export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
  statusCode?: number;
}

// Form Types
export interface FormError {
  field: string;
  message: string;
}

export interface JobSearchResponse {
  message: string;
  total_jobs: number;
  matches: JobMatch[];
}

export interface JobMatchHistoryResponse {
  message: string;
  matches: JobMatchCardType[];
}
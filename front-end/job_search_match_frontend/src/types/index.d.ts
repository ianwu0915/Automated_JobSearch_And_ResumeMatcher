export type User = {
    userId: string;
    email: string;
    fullName: string;
    isActive: boolean;
    isVerified: boolean;
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
    fullName: string;
    email: string;
    password: string;
}
export interface AuthResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
}
export interface Resume {
    resumeId: string;
    userId: string;
    features: ResumeFeatures;
    rawText: string;
    processedDate: string;
}
export interface ResumeFeatures {
    workExperienceYears: number;
    skills: string[];
    wordFrequencies: Record<string, number>;
}
export interface Job {
    jobId: string;
    title: string;
    company: string;
    location: string;
    workplaceType: string;
    listedTime: string;
    applyUrl: string;
    description: string;
    features: JobFeatures;
    processedDate: string;
}
export interface JobFeatures {
    requiredExperienceYears: number;
    skills: string[];
    wordFrequencies: Record<string, number>;
}
export interface JobMatch {
    resumeId: string;
    jobId: string;
    matchScore: number;
    matchedSkills: string[];
    missingSkills: string[];
    requiredExperienceYears: number;
    resumeExperienceYears: number;
    job: Job;
}
export interface JobSearchParams {
    keywords: string;
    location: string;
    experienceLevel: string[];
    jobType: string[];
    remote: string[];
    limit: number;
    userId: string;
}
export interface ApiResponse<T> {
    data?: T;
    message?: string;
    error?: string;
    statusCode?: number;
}
export interface FormError {
    field: string;
    message: string;
}
export interface JobSearchResponse {
    message: string;
    total_jobs: number;
    matches: JobMatch[];
}

import api from './api';
import { Job, JobMatch, JobSearchParams, JobSearchResponse } from '@/types';

const JOB_ENDPOINTS = {
  SEARCH_AND_MATCH: '/jobs/search_and_match',
  GET_JOB: '/jobs',
  GET_MATCH_HISTORY: '/matches/history',
};

export const jobService = {
  async searchAndMatchJobs(params: JobSearchParams): Promise<{ matches: JobMatch[] }> {
    // Convert the params to URLSearchParams for query string
    const queryParams = new URLSearchParams();
    queryParams.append('keywords', params.keywords);
    queryParams.append('location', params.location);
    params.experienceLevel.forEach(level => queryParams.append('experience_level', level));
    params.jobType.forEach(type => queryParams.append('job_type', type));
    params.remote.forEach(remote => queryParams.append('remote', remote));
    queryParams.append('limit', params.limit.toString());
    queryParams.append('user_id', params.userId);
    
    const response = await api.get<JobSearchResponse>(
      `${JOB_ENDPOINTS.SEARCH_AND_MATCH}?${queryParams.toString()}`
    );
    
    return response.data; // { message: string, total_jobs: number, matches: JobMatch[] }
  },
  
  async getJobById(jobId: string): Promise<Job> {
    const response = await api.get<Job>(`${JOB_ENDPOINTS.GET_JOB}/${jobId}`);
    return response.data;
  },
  
  async getMatchHistory(userId: string, limit: number = 50, minScore: number = 50): Promise<{ matches: JobMatch[] }> {
    const queryParams = new URLSearchParams();
    queryParams.append('user_id', userId);
    queryParams.append('limit', limit.toString());
    queryParams.append('min_score', minScore.toString());
    
    const response = await api.get<{ matches: JobMatch[] }>(
      `${JOB_ENDPOINTS.GET_MATCH_HISTORY}?${queryParams.toString()}`
    );
    
    return response.data;
  },
};
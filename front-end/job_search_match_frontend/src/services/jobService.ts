import api from './api';
import { Job, JobSearchParams, JobSearchResponse, JobMatch, JobMatchHistoryResponse } from '@/types';

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
    queryParams.append('location_name', params.location_name);
    params.experience_level.forEach(level => queryParams.append('experience', level));
    params.job_type.forEach(type => queryParams.append('job_type', type));
    params.remote.forEach(remote => queryParams.append('remote', remote));
    queryParams.append('limit', params.limit.toString() || '10');
    queryParams.append('user_id', params.user_id);

    console.log(queryParams.toString());
    
    const response = await api.get<JobSearchResponse>(
      `${JOB_ENDPOINTS.SEARCH_AND_MATCH}?${queryParams.toString()}`
    );
    
    return response.data; // { message: string, total_jobs: number, matches: JobMatch[] }
  },
  
  async getJobById(jobId: string): Promise<Job> {
    console.log("Getting job by id", jobId);
    const response = await api.get<Job>(`${JOB_ENDPOINTS.GET_JOB}/${jobId}`);
    return response.data;
  },
  
  async getMatchHistory(userId: string, limit: number = 50, minScore: number = 50): Promise<JobMatchHistoryResponse> {
    const queryParams = new URLSearchParams();
    queryParams.append('user_id', userId);
    queryParams.append('limit', limit.toString());
    queryParams.append('min_score', minScore.toString());
    
    const response = await api.get<JobMatchHistoryResponse>(
      `${JOB_ENDPOINTS.GET_MATCH_HISTORY}?${queryParams.toString()}`
    );
    
    return response.data;
  },
};
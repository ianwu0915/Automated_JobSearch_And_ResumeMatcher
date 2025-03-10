import { useState } from 'react';
import { JobMatch, JobSearchParams, JobMatchCardType } from '@/types';
import { jobService } from '@/services/jobService';

export const useJobSearch = () => {
  const [matches, setMatches] = useState<JobMatch[]>([]);
  const [matchHistory, setMatchHistory] = useState<JobMatchCardType[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [totalJobs, setTotalJobs] = useState<number>(0);

  const searchJobs = async (params: JobSearchParams) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await jobService.searchAndMatchJobs(params);
      
      setMatches(response.matches);
      setTotalJobs(response.matches.length);
      
      return response.matches;
    } catch (err) {
      console.error('Error searching jobs:', err);
      setError('Failed to search jobs. Please try again.');
      return [];
    } finally {
      setIsLoading(false);
    }
  };

  const getMatchHistory = async (userId: string, limit: number = 50, minScore: number = 50) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await jobService.getMatchHistory(userId, limit, minScore);
      
      setMatchHistory(response.matches);
      setTotalJobs(response.matches.length);
      
      return response.matches;
    } catch (err) {
      console.error('Error getting match history:', err);
      setError('Failed to get match history. Please try again.');
      return [];
    } finally {
      setIsLoading(false);
    }
  };

  return {
    matches,
    matchHistory,
    totalJobs,
    isLoading,
    error,
    searchJobs,
    getMatchHistory,
  };
};
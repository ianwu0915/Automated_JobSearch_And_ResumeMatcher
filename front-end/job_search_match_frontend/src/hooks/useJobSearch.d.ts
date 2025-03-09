import { JobMatch, JobSearchParams } from '@/types';
export declare const useJobSearch: () => {
    matches: JobMatch[];
    totalJobs: number;
    isLoading: boolean;
    error: string | null;
    searchJobs: (params: JobSearchParams) => Promise<JobMatch[]>;
    getMatchHistory: (userId: string, limit?: number, minScore?: number) => Promise<JobMatch[]>;
};

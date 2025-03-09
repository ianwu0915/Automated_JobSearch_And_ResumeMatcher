import { Job, JobMatch, JobSearchParams } from '@/types';
export declare const jobService: {
    searchAndMatchJobs(params: JobSearchParams): Promise<{
        matches: JobMatch[];
    }>;
    getJobById(jobId: string): Promise<Job>;
    getMatchHistory(userId: string, limit?: number, minScore?: number): Promise<{
        matches: JobMatch[];
    }>;
};

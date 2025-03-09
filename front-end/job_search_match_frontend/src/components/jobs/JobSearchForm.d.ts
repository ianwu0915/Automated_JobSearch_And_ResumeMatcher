import React from 'react';
import { JobSearchParams } from '@/types';
interface JobSearchFormProps {
    onSubmit: (values: JobSearchParams) => Promise<void>;
    isLoading: boolean;
    userId: string;
}
export declare const JobSearchForm: React.FC<JobSearchFormProps>;
export {};

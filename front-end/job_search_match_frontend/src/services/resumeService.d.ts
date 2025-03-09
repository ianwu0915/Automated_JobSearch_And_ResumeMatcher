import { ApiResponse, Resume } from "@/types";
export declare const resumeService: {
    uploadResume(file: File, userId: string): Promise<ApiResponse<{
        resumeId: string;
        features: any;
    }>>;
    getResumeByUserId(userId: string): Promise<Resume>;
};

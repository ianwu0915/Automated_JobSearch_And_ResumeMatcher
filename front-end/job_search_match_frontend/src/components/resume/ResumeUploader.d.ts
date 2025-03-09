import { ResumeFeatures } from "@/types";
interface ResumeUploaderProps {
    userId: string;
    onUpload: (file: File, userId: string) => Promise<{
        resumeId: string;
        features: ResumeFeatures;
    }>;
    currentResume?: {
        resumeId: string;
        fileName: string;
    };
}
export declare const ResumeUploader: ({ userId, onUpload, currentResume, }: ResumeUploaderProps) => import("react/jsx-runtime").JSX.Element;
export {};

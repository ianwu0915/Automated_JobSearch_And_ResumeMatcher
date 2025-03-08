import api from "./api";
import { ApiResponse, Resume } from "@/types";

const RESUME_ENDPOINTS = {
  UPLOAD: "/resumes/upload",
  GET_BY_USER: "/resumes/user",
};

export const resumeService = {
  async uploadResume(
    file: File,
    userId: string
  ): Promise<ApiResponse<{ resumeId: string; features: any }>> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post<
      ApiResponse<{ resumeId: string; features: any }>
    >(`${RESUME_ENDPOINTS.UPLOAD}?user_id=${userId}`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  },

  async getResumeByUserId(userId: string): Promise<Resume> {
    const response = await api.get<Resume>(
      `${RESUME_ENDPOINTS.GET_BY_USER}?user_id=${userId}`
    );
    return response.data;
  },
};

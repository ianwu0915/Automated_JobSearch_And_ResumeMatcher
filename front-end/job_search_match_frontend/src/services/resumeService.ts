import api from "./api";
import { ApiResponse, Resume } from "@/types";

console.log("resumeService module loaded");

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
    console.log("userId", userId);

    try {
      const response = await api.post<
        ApiResponse<{ resumeId: string; features: any }>
      >(`${RESUME_ENDPOINTS.UPLOAD}?user_id=${userId}`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      console.log("response", response);
      return response.data;
    } catch (error) {
      console.error("Error uploading resume:", error);
      throw error;
    }
  },

  async getResumeByUserId(userId: string): Promise<Resume> {
    console.log("getResumeByUserId called with:", userId);
    // Add this at the bottom of your file
    console.log("api instance:", api);
    console.log("Request interceptors:", api.interceptors.request);
    console.log("Response interceptors:", api.interceptors.response);
    console.log("api prototype:", Object.getPrototypeOf(api));

    const response = await api.get<Resume>(RESUME_ENDPOINTS.GET_BY_USER, {
      params: {
        user_id: userId,
      },
    });
    return response.data;
  },
};

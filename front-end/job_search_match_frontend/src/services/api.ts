import axios, { AxiosError, AxiosRequestConfig } from "axios";
import { camelizeKeys, decamelizeKeys } from "humps";
import { AuthResponse } from "@/types";

// Create axios instance
const api = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

// Track an ongoing refresh promise
let refreshTokenPromise: Promise<string> | null = null;

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // if (config.data) {
    //   config.data = decamelizeKeys(config.data);
    // }

    // if (config.params) {
    //   config.params = decamelizeKeys(config.params);
    // }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling token refresh
api.interceptors.response.use(
  (response) => {
    if (response.data) {
      // response.data = camelizeKeys(response.data);
    }
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (!refreshTokenPromise) {
        refreshTokenPromise = refreshAccessToken();
      }

      try {
        const newToken = await refreshTokenPromise;
        refreshTokenPromise = null; // Reset after refresh

        // Store new token
        localStorage.setItem("token", newToken);

        // Retry original request with new token
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
        }
        return api(originalRequest);
      } catch (refreshError) {
        refreshTokenPromise = null; // Reset in case of failure
        localStorage.removeItem("token");
        localStorage.removeItem("refreshToken");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Function to refresh the token
async function refreshAccessToken(): Promise<string> {
  const refreshToken = localStorage.getItem("refreshToken");

  if (!refreshToken) {
    localStorage.removeItem("token");
    localStorage.removeItem("refreshToken");
    window.location.href = "/login";
    throw new Error("No refresh token available");
  }

  const response = await axios.post<AuthResponse>(
    "/api/auth/refresh",
    decamelizeKeys({ refreshToken }),
    {
      baseURL: "/api",
      headers: { "Content-Type": "application/json" },
    }
  );

  const data = camelizeKeys(response.data) as AuthResponse;
  return data.access_token;
}

export default api;

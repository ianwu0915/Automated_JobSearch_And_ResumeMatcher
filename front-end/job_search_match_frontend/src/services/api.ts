import axios, { AxiosError, AxiosRequestConfig } from "axios";
import { camelizeKeys, decamelizeKeys } from "humps";
import { AuthResponse } from "@/types";

// Create axios instance
const api = axios.create({
  baseURL: "/api", // This will use the proxy set up in vite.config.js
  headers: {
    "Content-Type": "application/json",
  },
});

// Add console.log to verify the instance
console.log("api instance created:", api);

// Request interceptor for adding auth token and converting data to snake_case
api.interceptors.request.use(
  (config) => {
    // Add auth token
    console.log("api here", api);
    console.log("config", config);


    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Convert request data from camelCase to snake_case
    if (config.data) {
      console.log("config.data", config.data);
      config.data = decamelizeKeys(config.data);
    }

    // Convert URL params if they exist
    if (config.params) {
      console.log("config.params", config.params);
      config.params = decamelizeKeys(config.params);
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for handling token refresh and converting data to camelCase
api.interceptors.response.use(
  (response) => {
    // Convert response data from snake_case to camelCase
    if (response.data) {
      response.data = camelizeKeys(response.data);
    }
    console.log("response.data", response.data);
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & {
      _retry?: boolean;
    };

    // If 401 and not already retrying, attempt to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem("refreshToken");

        if (!refreshToken) {
          // No refresh token available, logout user
          localStorage.removeItem("token");
          localStorage.removeItem("refreshToken");
          window.location.href = "/login";
          return Promise.reject(error);
        }

        // Request new access token
        // Note: We're using axios directly here, not 'api', to avoid the request interceptor
        // We'll handle the snake_case manually
        const response = await axios.post<AuthResponse>(
          "/api/auth/refresh",
          // Convert to snake_case manually for this special case
          decamelizeKeys({ refreshToken }),
          {
            baseURL: "/api",
            headers: {
              "Content-Type": "application/json",
            },
          }
        );

        // Convert response data to camelCase manually since we're not using the api instance
        const data = camelizeKeys(response.data) as AuthResponse;
        const { access_token } = data;

        localStorage.setItem("token", access_token);

        // Retry original request with new token
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
        }
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh token is invalid or expired, logout user
        localStorage.removeItem("token");
        localStorage.removeItem("refreshToken");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;

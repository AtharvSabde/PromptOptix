import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 60000, // 60s for LLM calls
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const apiError = {
      error: error.response?.data?.error || error.response?.data?.detail?.error || 'Network error',
      message: error.response?.data?.message || error.response?.data?.detail?.message || error.message,
      status: error.response?.status,
      type: error.response?.data?.type || error.response?.data?.detail?.type,
    };
    return Promise.reject(apiError);
  }
);

export interface ApiError {
  error: string;
  message: string;
  status?: number;
  type?: string;
}

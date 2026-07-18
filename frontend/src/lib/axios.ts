import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - attach auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const tokenData = localStorage.getItem('auth-tokens');
    if (tokenData) {
      try {
        const tokens = JSON.parse(tokenData);
        if (tokens.accessToken) {
          config.headers.Authorization = `Bearer ${tokens.accessToken}`;
        }
      } catch {
        localStorage.removeItem('auth-tokens');
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors and token refresh
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error: AxiosError<{ message?: string; detail?: string }>) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Handle 401 - Token expired
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const tokenData = localStorage.getItem('auth-tokens');
      if (tokenData) {
        try {
          const tokens = JSON.parse(tokenData);
          const refreshResponse = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refreshToken: tokens.refreshToken,
          });

          const newTokens = refreshResponse.data.data;
          localStorage.setItem('auth-tokens', JSON.stringify(newTokens));

          originalRequest.headers.Authorization = `Bearer ${newTokens.accessToken}`;
          return apiClient(originalRequest);
        } catch {
          // Refresh failed - clear tokens and redirect to login
          localStorage.removeItem('auth-tokens');
          localStorage.removeItem('auth-user');
          window.location.href = '/login';
          return Promise.reject(error);
        }
      } else {
        window.location.href = '/login';
        return Promise.reject(error);
      }
    }

    // Handle 403 - Forbidden
    if (error.response?.status === 403) {
      toast.error('You do not have permission to perform this action.');
    }

    // Handle 404 - Not Found
    if (error.response?.status === 404) {
      toast.error('The requested resource was not found.');
    }

    // Handle 422 - Validation Error
    if (error.response?.status === 422) {
      const message = error.response.data?.detail || 'Validation error. Please check your input.';
      toast.error(message);
    }

    // Handle 500 - Server Error
    if (error.response?.status && error.response.status >= 500) {
      toast.error('An unexpected server error occurred. Please try again later.');
    }

    // Handle network errors
    if (!error.response) {
      toast.error('Network error. Please check your connection.');
    }

    return Promise.reject(error);
  }
);

export default apiClient;

// Convenience methods for common patterns
export const api = {
  get: <T>(url: string, params?: Record<string, unknown>) =>
    apiClient.get<T>(url, { params }),

  post: <T>(url: string, data?: unknown) =>
    apiClient.post<T>(url, data),

  put: <T>(url: string, data?: unknown) =>
    apiClient.put<T>(url, data),

  patch: <T>(url: string, data?: unknown) =>
    apiClient.patch<T>(url, data),

  delete: <T>(url: string) =>
    apiClient.delete<T>(url),
};

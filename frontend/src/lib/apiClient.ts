// frontend/src/lib/apiClient.ts
import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL ?? '/api';

export const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('accessToken');
  if (token) {
    config.headers = config.headers ?? {};
    config.headers['Authorization'] = `Bearer ${token}`;
  }

  return config;
});


api.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = 'Error occurred';
    if (axios.isAxiosError(error)) {
      const apiMessage = error.response?.data?.message;
      if (apiMessage != null) message = apiMessage;
      error.userMessage = message;
    }
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      sessionStorage.removeItem('accessToken');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    console.error('API error:', message);
    return Promise.reject(error);
  }
);

export default api;

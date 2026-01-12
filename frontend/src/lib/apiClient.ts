// frontend/src/lib/apiClient.ts
import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL ?? '/api';

export const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
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
    console.error('API error:', message);
    return Promise.reject(error);
  }
);

export default api;

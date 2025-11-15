// frontend/src/lib/apiClient.ts
import axios from 'axios';

export const api = axios.create({
  baseURL: '/api', // always use proxy path
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});

export default api;
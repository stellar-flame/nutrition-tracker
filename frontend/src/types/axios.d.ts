import 'axios';

declare module 'axios' {
  export interface AxiosError {
    userMessage?: string;
  }
}

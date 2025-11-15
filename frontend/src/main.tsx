import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import Index from "@/app/routes/index";
import "./styles/index.css";
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
const queryClient = new QueryClient();

createRoot(document.getElementById('root')!).render(
 <StrictMode>
    <QueryClientProvider client={queryClient}>
      <Index />
    </QueryClientProvider>
  </StrictMode>
)

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import Index from "@/app/routes/index";
import "./styles/index.css";

createRoot(document.getElementById('root')!).render(
 <StrictMode>
    <Index />
  </StrictMode>
)

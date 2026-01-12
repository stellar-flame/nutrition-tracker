
import type { NutritionSummary } from "@/types/nutrition";
import type { AxiosError } from 'axios';
import { api } from '@/lib/apiClient';
import { useQuery } from '@tanstack/react-query';
import { getToday } from './useDate';



async function fetchNutritionSummary(date:string): Promise<NutritionSummary> {
  const { data } = await api.get<NutritionSummary>('/nutrition/summary', {
    params: { date },
  });
  return data;
}

export function useNutritionSummary(date: string = getToday()) {
  return useQuery<NutritionSummary, AxiosError>({
    queryKey: ['nutrition-summary', date],
    queryFn: () => fetchNutritionSummary(date),
    staleTime: 60_000, // 1 minute
  });
}

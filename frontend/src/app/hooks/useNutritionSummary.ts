
import type { NutritionSummary } from "@/types/nutrition";
import { api } from '@/lib/apiClient';
import { useQuery } from '@tanstack/react-query';

function getToday(): string {
  return new Date().toISOString().slice(0, 10);
}

async function fetchNutritionSummary(date:string): Promise<NutritionSummary> {
  const { data } = await api.get<NutritionSummary>('/nutrition/summary', {
    params: { date },
  });
  return data;
}

export function useNutritionSummary(date: string = getToday()) {
  return useQuery({
    queryKey: ['nutrition-summary', date],
    queryFn: () => fetchNutritionSummary(date),
    staleTime: 60_000, // 1 minute
  });
}
import type { Meal } from '@/types/meals';
import { api } from '@/lib/apiClient';
import { useQuery } from '@tanstack/react-query';
import { getToday } from './useDate';


export async function fetchMeals(date: string): Promise<Meal[]> {
  const { data } = await api.get<Meal[]>('/nutrition/meals', {
    params: { date },
  });
  return data;
}

export function useMeals(date: string = getToday()) {
  return useQuery({
    queryKey: ['meals', date],
    queryFn: () => fetchMeals(date),
    staleTime: 60_000, // 1 minute
  });
}

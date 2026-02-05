import type { Meal } from '@/types/meals';
import { api } from '@/lib/apiClient';
import { useQuery } from '@tanstack/react-query';
import { getToday } from './useDate';
import type { AxiosError } from 'axios';
import { useQueryClient } from '@tanstack/react-query';


export async function fetchMeals(date: string): Promise<Meal[]> {
  const { data } = await api.get<Meal[]>('/nutrition/meals', {
    params: { date },
  });
  
  return data;
}

export async function createMeal(description: string, date: string): Promise<Meal> {
  const response = await api.post<Meal>('/nutrition/meals', { description, date });
  return response.data;
}
 

export function useMeals(date: string = getToday()) {
  const queryClient = useQueryClient();
  return useQuery<Meal[], AxiosError>({
    queryKey: ['meals', date],
    queryFn: () => fetchMeals(date),
    staleTime: 60_000, // 1 minute

     // Poll every 3 seconds if any meal is pending/processing
    refetchInterval: (query) => {
      const meals = query.state.data;
      const hasPending = meals?.some(
        (meal) => meal.status === 'pending'
      );

       // Invalidate nutrition summary when we refetch meals
      if (hasPending) {
        queryClient.invalidateQueries({ queryKey: ['nutrition-summary', date] });
      }
      return hasPending ? 3000 : false; // Poll while pending, stop when done
    },
  });
}

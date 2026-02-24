import type { Meal } from '@/types/meals';
import { api } from '@/lib/apiClient';
import { useQuery } from '@tanstack/react-query';
import { getToday, getCurrentTime} from './useDate';
import type { AxiosError } from 'axios';


export async function fetchMeals(date: string): Promise<Meal[]> {
  const { data } = await api.get<Meal[]>('/nutrition/meals', {
    params: { date },
  });
  
  return data;
}

export async function createMeal(description: string, date: string): Promise<Meal> {
  const response = await api.post<Meal>('/nutrition/meals', { description, date, time: getCurrentTime() });
  return response.data;
}
 

export function useMeals(date: string = getToday()) {
  return useQuery<Meal[], AxiosError>({
    queryKey: ['meals', date],
    queryFn: () => fetchMeals(date),
    staleTime: 60_000,
    
    // Transform data to mark stale pending as failed
    select: (meals) => {
      const now = Date.now();
      return meals.map((meal) => {
        if (meal.status !== 'pending') return meal;
        const createdAt = new Date(meal.created_at).getTime();
        console.log(`Checking meal ${meal.created_at} with status ${meal.status}`);
        console.log(`Current time: ${Date.now()}, Created at: ${meal.created_at}, Age: ${(now - createdAt) / 1000}s`);
        if (now - createdAt > 60_000) {
          return { ...meal, status: 'failed' as const }; // New object, not mutation
        }
        return meal;
      });
    },

    refetchInterval: (query) => {
      const meals = query.state.data;
      const now = Date.now();
      const hasActivePending = meals?.some((meal) => {
        if (meal.status !== 'pending') return false;
        const createdAt = new Date(meal.created_at).getTime();
        return now - createdAt <= 60_000;
      });
      return hasActivePending ? 3000 : false;
    },
  });
}

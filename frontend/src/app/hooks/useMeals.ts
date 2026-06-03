import type { Meal, PendingMeal } from '@/types/meals';
import { api } from '@/lib/apiClient';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getToday, getCurrentTime } from './useDate';
import type { AxiosError } from 'axios';


export async function fetchMeals(date: string): Promise<Meal[]> {
  const { data } = await api.get<Meal[]>('/nutrition/meals', {
    params: { date },
  });
  return data;
}

export async function createMeal(description: string, date: string): Promise<PendingMeal> {
  const response = await api.post<PendingMeal>('/nutrition/meals', { description, date, time: getCurrentTime() });
  return response.data;
}

async function deleteMeal(meal_id: number): Promise<void> {
  await api.delete(`/nutrition/meals/${meal_id}`);
}

export function useMeals(date: string = getToday()) {
  return useQuery<Meal[], AxiosError>({
    queryKey: ['meals', date],
    queryFn: () => fetchMeals(date),
  });
}

export function useDeleteMeal(date: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: deleteMeal,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['meals', date] });
      qc.invalidateQueries({ queryKey: ['nutrition-summary', date] });
    },
  });
}

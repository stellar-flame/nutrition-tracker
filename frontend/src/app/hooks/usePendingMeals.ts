import type { PendingMeal, MealApprovePayload } from '@/types/meals';
import { api } from '@/lib/apiClient';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getToday } from './useDate';
import type { AxiosError } from 'axios';


export async function fetchPendingMeals(date: string): Promise<PendingMeal[]> {
  const { data } = await api.get<PendingMeal[]>('/nutrition/pending-meals', { params: { date } });
  return data;
}

export async function approveMeal(meal_id: string, payload: MealApprovePayload) {
  const { data } = await api.post(`/nutrition/meals/${meal_id}/approve`, payload);
  return data;
}

export async function dismissMeal(meal_id: string) {
  await api.delete(`/nutrition/pending-meals/${meal_id}`);
}

export function usePendingMeals(date: string = getToday()) {
  return useQuery<PendingMeal[], AxiosError>({
    queryKey: ['pending-meals', date],
    queryFn: () => fetchPendingMeals(date),
    refetchInterval: (query) => {
      const hasPendingAI = query.state.data?.some(m => m.status === 'pending_ai');
      return hasPendingAI ? 3000 : false;
    },
  });
}

export function useApproveMeal() {
  const qc = useQueryClient();
  return useMutation<unknown, AxiosError, { meal_id: string; payload: MealApprovePayload }>({
    mutationFn: ({ meal_id, payload }) => approveMeal(meal_id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['pending-meals'] });
      qc.invalidateQueries({ queryKey: ['meals'] });
      qc.invalidateQueries({ queryKey: ['nutrition-summary'] });
    },
  });
}

export function useDismissMeal() {
  const qc = useQueryClient();
  return useMutation<unknown, AxiosError, string>({
    mutationFn: (meal_id) => dismissMeal(meal_id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['pending-meals'] });
    },
  });
}

import styles from './Meals.module.css';
import { useMeals, createMeal, useDeleteMeal } from '@/app/hooks/useMeals';
import { usePendingMeals, useApproveMeal, useDismissMeal } from '@/app/hooks/usePendingMeals';
import PendingMealCard from './PendingMealCard';
import { useState } from 'react';
import { getToday } from '@/app/hooks/useDate';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { MealItem } from '@/types/meals';


export default function Meals() {
    const today = getToday();
    const { data: meals = [], isLoading, error: errorLoadingMeals } = useMeals(today);
    const { data: pendingMeals = [] } = usePendingMeals(today);
    const approveMealMutation = useApproveMeal();
    const dismissMealMutation = useDismissMeal();
    const deleteMealMutation = useDeleteMeal(today);

    const qc = useQueryClient();
    const [newDesc, setNewDesc] = useState("");
    const [expandedMeals, setExpandedMeals] = useState<Set<number>>(new Set());

    const toggleMeal = (id: number) => {
        setExpandedMeals(prev => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id);
            else next.add(id);
            return next;
        });
    };

    const { mutate: mutateFn, isPending, error: errorAddingMeal, reset } = useMutation({
        mutationFn: (description: string) => createMeal(description, today),
        onSuccess: async () => {
            await Promise.all([
                qc.invalidateQueries({ queryKey: ['pending-meals', today] }),
                qc.invalidateQueries({ queryKey: ['nutrition-summary', today] }),
            ]);
            setNewDesc("");
        }
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newDesc.trim()) return;
        mutateFn(newDesc.trim());
    };

    if (isLoading) return <div>Loading…</div>;
    if (errorLoadingMeals) return <div role="alert">{errorLoadingMeals?.message ?? 'Failed to load'}</div>;

    return (
        <section role="region" aria-label="Meals logged today" className={styles.section}>
            <h2 className={styles.title}>Meals today</h2>

            {errorAddingMeal && (
                <div role="alert" className={styles.error}>
                    {errorAddingMeal?.message ?? 'Failed to add meal'}
                </div>
            )}

            <form role="form" className={styles.newMealForm} onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="New meal description"
                    value={newDesc}
                    onChange={(e) => {
                        if (errorAddingMeal) reset();
                        setNewDesc(e.target.value);
                    }}
                    disabled={isPending}
                />
                <button type="submit" disabled={isPending}>
                    {isPending ? 'Adding...' : 'Add'}
                </button>
            </form>

            {pendingMeals.length === 0 && meals.length === 0 && (
                <p className={styles.empty}>No meals logged yet.</p>
            )}

            {pendingMeals.length > 0 && (
                <>
                    <p className={styles.pendingSectionTitle}>Awaiting review</p>
                    <ul role="list" className={styles.list}>
                        {pendingMeals.map(meal => (
                            <PendingMealCard
                                key={meal.meal_id}
                                meal={meal}
                                isApproving={approveMealMutation.isPending}
                                onApprove={(items?: MealItem[]) =>
                                    approveMealMutation.mutate({ meal_id: meal.meal_id, payload: { items } })
                                }
                                onDismiss={() => dismissMealMutation.mutate(meal.meal_id)}
                            />
                        ))}
                    </ul>
                </>
            )}

            {meals.length > 0 && (
                <ul role="list" className={styles.list} style={{ marginTop: pendingMeals.length > 0 ? '16px' : undefined }}>
                    {meals.map((meal) => {
                        const totalKcal = meal.items.reduce((sum, it) => sum + it.caloriesKcal, 0);
                        const isExpanded = expandedMeals.has(meal.id);
                        return (
                            <li key={meal.id} role="listitem" className={styles.meal} aria-label={`${meal.description} at ${meal.time}`}>
                                <div className={styles.mealHeader}>
                                    <button
                                        className={styles.mealExpand}
                                        onClick={() => toggleMeal(meal.id)}
                                        aria-expanded={isExpanded}
                                        aria-controls={`items-${meal.id}`}
                                    >
                                        <div className={styles.mealMeta}>
                                            <span className={`${styles.chevron} ${isExpanded ? styles.chevronExpanded : ''}`}>▶</span>
                                            <strong className={styles.mealName}>{meal.description}</strong>
                                            <span className={styles.mealTime}>{meal.time}</span>
                                        </div>
                                        <div className={styles.mealTotal}>{totalKcal.toLocaleString()} kcal</div>
                                    </button>
                                    <button
                                        className={styles.deleteMealBtn}
                                        onClick={() => deleteMealMutation.mutate(meal.id)}
                                        disabled={deleteMealMutation.isPending}
                                        aria-label={`Delete ${meal.description}`}
                                    >×</button>
                                </div>

                                <ul
                                    role="list"
                                    className={`${styles.mealItems} ${isExpanded ? styles.mealItemsExpanded : ''}`}
                                    id={`items-${meal.id}`}
                                    aria-hidden={!isExpanded}
                                >
                                    {meal.items.map((it, i) => (
                                        <li key={i} role="listitem" className={styles.mealItem}>
                                            <div className={styles.itemHeader}>
                                                <span className={styles.itemDesc}>{it.description}</span>
                                                <span className={styles.itemCalories}>{it.caloriesKcal} kcal</span>
                                            </div>
                                            <div className={styles.itemNutrients}>
                                                <span className={styles.nutrient}><span className={styles.nutrientLabel}>Protein</span><span className={styles.nutrientValue}>{it.proteinG}g</span></span>
                                                <span className={styles.nutrient}><span className={styles.nutrientLabel}>Carbs</span><span className={styles.nutrientValue}>{it.carbsG}g</span></span>
                                                <span className={styles.nutrient}><span className={styles.nutrientLabel}>Fat</span><span className={styles.nutrientValue}>{it.fatG}g</span></span>
                                                <span className={styles.nutrient}><span className={styles.nutrientLabel}>Fiber</span><span className={styles.nutrientValue}>{it.fiberG}g</span></span>
                                                <span className={styles.nutrient}><span className={styles.nutrientLabel}>Sugar</span><span className={styles.nutrientValue}>{it.sugarG}g</span></span>
                                                <span className={styles.nutrient}><span className={styles.nutrientLabel}>Sodium</span><span className={styles.nutrientValue}>{it.sodiumMg}mg</span></span>
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            </li>
                        );
                    })}
                </ul>
            )}
        </section>
    );
}

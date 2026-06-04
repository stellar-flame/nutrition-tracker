import styles from './Meals.module.css';
import { useMeals, createMeal, useDeleteMeal, useUpdateServing } from '@/app/hooks/useMeals';
import { usePendingMeals, useApproveMeal, useDismissMeal } from '@/app/hooks/usePendingMeals';
import PendingMealCard from './PendingMealCard';
import { useState } from 'react';
import { getToday } from '@/app/hooks/useDate';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { MealItem } from '@/types/meals';

const STEP = 0.25;
const MIN_SERVING = 0.25;

function round2(n: number) {
    return Math.round(n * 100) / 100;
}

export default function Meals() {
    const today = getToday();
    const { data: meals = [], isLoading, error: errorLoadingMeals } = useMeals(today);
    const { data: pendingMeals = [] } = usePendingMeals(today);
    const approveMealMutation = useApproveMeal();
    const dismissMealMutation = useDismissMeal();
    const deleteMealMutation = useDeleteMeal(today);
    const updateServingMutation = useUpdateServing(today);

    const qc = useQueryClient();
    const [newDesc, setNewDesc] = useState("");
    const [expandedMeals, setExpandedMeals] = useState<Set<number>>(new Set());

    // Per-meal local item servings: Record<meal_id, serving_size[]>
    const [itemServings, setItemServings] = useState<Record<number, number[]>>({});

    const getItemServings = (mealId: number, items: MealItem[]) =>
        itemServings[mealId] ?? items.map(it => it.serving_size);

    const toggleMeal = (id: number) => {
        setExpandedMeals(prev => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id);
            else next.add(id);
            return next;
        });
    };

    const adjustItemServing = (mealId: number, items: MealItem[], itemIdx: number, delta: number) => {
        const current = getItemServings(mealId, items);
        const next = [...current];
        next[itemIdx] = Math.max(MIN_SERVING, round2(next[itemIdx] + delta));
        setItemServings(prev => ({ ...prev, [mealId]: next }));
    };

    const handleItemServingInput = (mealId: number, items: MealItem[], itemIdx: number, raw: string) => {
        const v = parseFloat(raw);
        if (!isNaN(v) && v >= MIN_SERVING) {
            const next = [...getItemServings(mealId, items)];
            next[itemIdx] = v;
            setItemServings(prev => ({ ...prev, [mealId]: next }));
        }
    };

    const handleSaveServing = (mealId: number, items: MealItem[]) => {
        const servings = getItemServings(mealId, items);
        updateServingMutation.mutate(
            { meal_id: mealId, item_servings: servings },
            { onSuccess: () => setItemServings(prev => { const next = { ...prev }; delete next[mealId]; return next; }) }
        );
    };

    const isDirty = (mealId: number, items: MealItem[]) => {
        const local = itemServings[mealId];
        if (!local) return false;
        return local.some((s, i) => s !== items[i].serving_size);
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
                        const servings = getItemServings(meal.id, meal.items);
                        const totalKcal = meal.items.reduce((sum, it, i) => sum + round2(it.caloriesKcal * servings[i]), 0);
                        const isExpanded = expandedMeals.has(meal.id);
                        const dirty = isDirty(meal.id, meal.items);

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
                                        <div className={styles.mealTotal}>{round2(totalKcal).toLocaleString()} kcal</div>
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
                                    {meal.items.map((it, i) => {
                                        const s = servings[i];
                                        return (
                                            <li key={i} role="listitem" className={styles.mealItem}>
                                                <div className={styles.itemHeader}>
                                                    <span className={styles.itemDesc}>{it.description}</span>
                                                    <div className={styles.itemActions}>
                                                        <div className={styles.servingControl}>
                                                            <button
                                                                className={styles.servingBtn}
                                                                onClick={() => adjustItemServing(meal.id, meal.items, i, -STEP)}
                                                                disabled={s <= MIN_SERVING}
                                                                aria-label="Decrease serving"
                                                            >−</button>
                                                            <input
                                                                className={styles.servingInput}
                                                                type="number"
                                                                step={STEP}
                                                                min={MIN_SERVING}
                                                                value={s}
                                                                onChange={e => handleItemServingInput(meal.id, meal.items, i, e.target.value)}
                                                            />
                                                            <button
                                                                className={styles.servingBtn}
                                                                onClick={() => adjustItemServing(meal.id, meal.items, i, STEP)}
                                                                aria-label="Increase serving"
                                                            >+</button>
                                                        </div>
                                                        <span className={styles.itemCalories}>{round2(it.caloriesKcal * s)} kcal</span>
                                                    </div>
                                                </div>
                                                <div className={styles.itemNutrients}>
                                                    <span className={styles.nutrient}><span className={styles.nutrientLabel}>Protein</span><span className={styles.nutrientValue}>{round2(it.proteinG * s)}g</span></span>
                                                    <span className={styles.nutrient}><span className={styles.nutrientLabel}>Carbs</span><span className={styles.nutrientValue}>{round2(it.carbsG * s)}g</span></span>
                                                    <span className={styles.nutrient}><span className={styles.nutrientLabel}>Fat</span><span className={styles.nutrientValue}>{round2(it.fatG * s)}g</span></span>
                                                    <span className={styles.nutrient}><span className={styles.nutrientLabel}>Fiber</span><span className={styles.nutrientValue}>{round2(it.fiberG * s)}g</span></span>
                                                    <span className={styles.nutrient}><span className={styles.nutrientLabel}>Sugar</span><span className={styles.nutrientValue}>{round2(it.sugarG * s)}g</span></span>
                                                    <span className={styles.nutrient}><span className={styles.nutrientLabel}>Sodium</span><span className={styles.nutrientValue}>{round2(it.sodiumMg * s)}mg</span></span>
                                                </div>
                                            </li>
                                        );
                                    })}
                                </ul>
                                {dirty && (
                                    <div className={styles.saveRow}>
                                        <button
                                            className={styles.saveMealServingBtn}
                                            onClick={() => handleSaveServing(meal.id, meal.items)}
                                            disabled={updateServingMutation.isPending}
                                        >Save</button>
                                    </div>
                                )}
                            </li>
                        );
                    })}
                </ul>
            )}
        </section>
    );
}

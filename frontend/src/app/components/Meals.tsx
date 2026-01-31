import styles from './Meals.module.css';
import { useMeals, createMeal } from '@/app/hooks/useMeals';
import { useState } from "react";
import { getToday } from '@/app/hooks/useDate';
import { useMutation, useQueryClient } from "@tanstack/react-query";



export default function Meals() {
    const { data: meals = [], isLoading, error: errorLoadingMeals } = useMeals(getToday());
    const qc = useQueryClient();
    const [newDesc, setNewDesc] = useState("");
    const [expandedMeals, setExpandedMeals] = useState<Set<string>>(new Set());
    
    const toggleMeal = (key: string) => {
        setExpandedMeals(prev => {
            const next = new Set(prev);
            if (next.has(key)) {
                next.delete(key);
            } else {
                next.add(key);
            }
            return next;
        });
    };
    const { mutate: mutateFn, isPending, error: errorAddingMeal, reset } = useMutation({  
        mutationFn: (description: string) => createMeal(description, getToday()),
        onSuccess: async () => {
            await Promise.all([
                qc.invalidateQueries({ queryKey: ["meals", getToday()] }),
                qc.invalidateQueries({ queryKey: ["nutrition-summary", getToday()] })
            ]);
            setNewDesc("");
        }
    });

    const add_meal_button_text = isPending ? "Adding..." : "Add";

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newDesc.trim()) return;
      mutateFn(newDesc.trim());
    };

    if (isLoading) return <div>Loading…</div>;
    if (errorLoadingMeals) return <div role="alert">{errorLoadingMeals?.message ?? 'Failed to load'}</div>;
    if (!meals) return <div>No data</div>;
    return (
    <section role="region" aria-label="Meals logged today" className={styles.section}>
      <h2 className={styles.title}>Meals today</h2>
      {/* add input box to capture new meal*/}
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
            setNewDesc(e.target.value)} 
          }

          disabled={isPending}
        />
        <button type="submit" disabled={isPending}>{add_meal_button_text}</button>
      </form>
      {meals.length === 0 ? (
        <p className={styles.empty}>No meals logged yet.</p>
      ) : (
        <ul role="list" className={styles.list}>
          {meals.map((meal, idx) => {
            const totalKcal = meal.items.reduce((sum, it) => sum + it.caloriesKcal, 0);
            const key = `${meal.date}-${meal.time}-${idx}`;
            const isExpanded = expandedMeals.has(key);
            
            return (
              <li key={key} role="listitem" className={styles.meal} aria-label={`${meal.description} at ${meal.time}`}>
                <button 
                  className={styles.mealHeader}
                  onClick={() => toggleMeal(key)}
                  aria-expanded={isExpanded}
                  aria-controls={`items-${key}`}
                >
                  <div className={styles.mealMeta}>
                    <span className={`${styles.chevron} ${isExpanded ? styles.chevronExpanded : ''}`}>▶</span>
                    <strong className={styles.mealName}>{meal.description}</strong>
                    <span className={styles.mealTime}>{meal.time}</span>
                  </div>
                  <div className={styles.mealTotal}>{totalKcal.toLocaleString()} kcal</div>
                </button>

                <ul role="list" className={`${styles.mealItems} ${isExpanded ? styles.mealItemsExpanded : ''}`} id={`items-${key}`} aria-hidden={!isExpanded}>
                  {meal.items.map((it, i) => (
                    <li key={i} role="listitem" className={styles.mealItem}>
                      <span className={styles.itemDesc}>{it.description}</span>
                      <span className={styles.itemMeta}>{it.caloriesKcal} kcal</span>
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
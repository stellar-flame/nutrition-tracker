import styles from './Meals.module.css';
import { useMeals, createMeal } from '@/app/hooks/useMeals';
import { useState } from "react";
import { getToday } from '@/app/hooks/useDate';
import { useQueryClient } from "@tanstack/react-query";



export default function Meals() {
    const { data: meals = [], isLoading, error } = useMeals(getToday());
    const qc = useQueryClient();
    const [newDesc, setNewDesc] = useState("");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newDesc.trim()) return;
        await createMeal(newDesc.trim(), getToday());
        await qc.invalidateQueries({ queryKey: ["meals", getToday()] });
        setNewDesc("");
    };

    if (isLoading) return <div>Loading…</div>;
    if (error) return <div role="alert">{error.userMessage ?? 'Failed to load'}</div>;
    if (!meals) return <div>No data</div>;
    return (
    <section role="region" aria-label="Meals logged today" className={styles.section}>
      <h2 className={styles.title}>Meals today</h2>
      {/* add input box to capture new meal*/}
      <form role="form" className={styles.newMealForm} onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Add new meal"
          value={newDesc}
          onChange={(e) => setNewDesc(e.target.value)}
        />
        <button type="submit">Add</button>
      </form>
      {meals.length === 0 ? (
        <p className={styles.empty}>No meals logged yet.</p>
      ) : (
        <ul role="list" className={styles.list}>
          {meals.map((meal, idx) => {
            const totalKcal = meal.items.reduce((sum, it) => sum + it.caloriesKcal, 0);
            const key = `${meal.date}-${meal.time}-${idx}`;
            return (
              <li key={key} role="listitem" className={styles.meal} aria-label={`${meal.description} at ${meal.time}`}>
                <div className={styles.mealHeader}>
                  <div className={styles.mealMeta}>
                    <strong className={styles.mealName}>{meal.description}</strong>
                    <span className={styles.mealTime}>{meal.time}</span>
                  </div>
                  <div className={styles.mealTotal}>{totalKcal.toLocaleString()} kcal</div>
                </div>

                <ul role="list" className={styles.mealItems}>
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
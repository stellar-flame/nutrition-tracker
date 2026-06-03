import { useState, useEffect } from 'react';
import type { PendingMeal, MealItem } from '@/types/meals';
import styles from './Meals.module.css';

interface Props {
  meal: PendingMeal;
  onApprove: (items?: MealItem[]) => void;
  onDismiss: () => void;
  isApproving: boolean;
}

const STEP = 0.25;
const MIN_SERVING = 0.25;

function round2(n: number) {
  return Math.round(n * 100) / 100;
}

function scaleItem(item: MealItem, serving: number): MealItem {
  return {
    description: item.description,
    caloriesKcal: round2(item.caloriesKcal * serving),
    proteinG: round2(item.proteinG * serving),
    carbsG: round2(item.carbsG * serving),
    fatG: round2(item.fatG * serving),
    fiberG: round2(item.fiberG * serving),
    sugarG: round2(item.sugarG * serving),
    sodiumMg: round2(item.sodiumMg * serving),
  };
}

export default function PendingMealCard({ meal, onApprove, onDismiss, isApproving }: Props) {
  const [servings, setServings] = useState<number[]>(() => meal.items.map(() => 1));
  const [kept, setKept] = useState<boolean[]>(() => meal.items.map(() => true));

  useEffect(() => {
    if (meal.items.length > 0) {
      setServings(meal.items.map(() => 1));
      setKept(meal.items.map(() => true));
    }
  }, [meal.items.length]);

  if (meal.status === 'pending_ai') {
    return (
      <li className={`${styles.meal} ${styles.mealPending}`}>
        <div className={styles.pendingHeader}>
          <span className={styles.pendingTitle}>{meal.description}</span>
          <span className={styles.pendingBadge}>
            <span className={styles.spinner}></span>
            Analyzing nutrition...
          </span>
        </div>
        <span className={styles.mealTime}>{meal.time}</span>
      </li>
    );
  }

  if (meal.status === 'failed') {
    return (
      <li className={`${styles.meal} ${styles.mealFailed}`}>
        <div className={styles.mealHeader}>
          <span className={styles.failedIndicator}>❌ {meal.description}</span>
          <span className={styles.failedMessage}>Failed to analyze nutrition</span>
          <span className={styles.mealTime}>{meal.time}</span>
        </div>
        <div className={styles.approvalActions}>
          <button className={styles.dismissButton} onClick={onDismiss}>Dismiss</button>
        </div>
      </li>
    );
  }

  const scaledItems = meal.items.map((item, i) => scaleItem(item, servings[i]));
  const totalKcal = scaledItems
    .filter((_, i) => kept[i])
    .reduce((s, it) => s + it.caloriesKcal, 0);
  const anyKept = kept.some(Boolean);

  const adjustServing = (i: number, delta: number) => {
    setServings(prev =>
      prev.map((s, idx) => idx === i ? Math.max(MIN_SERVING, round2(s + delta)) : s)
    );
  };

  const handleServingInput = (i: number, raw: string) => {
    const v = parseFloat(raw);
    if (!isNaN(v) && v >= MIN_SERVING) {
      setServings(prev => prev.map((s, idx) => idx === i ? v : s));
    }
  };

  const handleApprove = () => {
    const items = meal.items
      .filter((_, i) => kept[i])
      .map((item, i) => scaleItem(item, servings[i]));
    onApprove(items);
  };

  return (
    <li className={`${styles.meal} ${styles.mealApproval}`}>
      <div className={styles.approvalHeader}>
        <div className={styles.mealMeta}>
          <strong className={styles.mealName}>{meal.description}</strong>
          <span className={styles.mealTime}>{meal.time}</span>
        </div>
        <span className={styles.approvalTotal}>{round2(totalKcal).toLocaleString()} kcal</span>
      </div>

      <ul className={`${styles.mealItems} ${styles.mealItemsExpanded}`}>
        {meal.items.map((item, i) => {
         if (!kept[i]) return null;
          const scaled = scaledItems[i];
          return (
            <li key={i} className={styles.mealItem}>
              <div className={styles.itemHeader}>
                <span className={styles.itemDesc}>{item.description}</span>
                <div className={styles.itemActions}>
                  <div className={styles.servingControl}>
                    <button
                      className={styles.servingBtn}
                      onClick={() => adjustServing(i, -STEP)}
                      disabled={servings[i] <= MIN_SERVING}
                      aria-label="Decrease serving"
                    >−</button>
                    <input
                      className={styles.servingInput}
                      type="number"
                      step={STEP}
                      min={MIN_SERVING}
                      value={servings[i]}
                      onChange={e => handleServingInput(i, e.target.value)}
                    />
                    <button
                      className={styles.servingBtn}
                      onClick={() => adjustServing(i, STEP)}
                      aria-label="Increase serving"
                    >+</button>
                  </div>
                  <button
                    className={styles.removeItemBtn}
                    onClick={() => setKept(prev => prev.map((k, idx) => idx === i ? false : k))}
                    aria-label="Remove item"
                  >×</button>
                </div>
              </div>
              <div className={styles.itemNutrients}>
                <span className={styles.nutrient}><span className={styles.nutrientLabel}>Calories</span><span className={styles.nutrientValue}>{scaled.caloriesKcal} kcal</span></span>
                <span className={styles.nutrient}><span className={styles.nutrientLabel}>Protein</span><span className={styles.nutrientValue}>{scaled.proteinG}g</span></span>
                <span className={styles.nutrient}><span className={styles.nutrientLabel}>Carbs</span><span className={styles.nutrientValue}>{scaled.carbsG}g</span></span>
                <span className={styles.nutrient}><span className={styles.nutrientLabel}>Fat</span><span className={styles.nutrientValue}>{scaled.fatG}g</span></span>
                <span className={styles.nutrient}><span className={styles.nutrientLabel}>Fiber</span><span className={styles.nutrientValue}>{scaled.fiberG}g</span></span>
                <span className={styles.nutrient}><span className={styles.nutrientLabel}>Sugar</span><span className={styles.nutrientValue}>{scaled.sugarG}g</span></span>
                <span className={styles.nutrient}><span className={styles.nutrientLabel}>Sodium</span><span className={styles.nutrientValue}>{scaled.sodiumMg}mg</span></span>
              </div>
            </li>
          );
        })}
      </ul>

      <div className={styles.approvalActions}>
        <button
          className={styles.approveButton}
          onClick={handleApprove}
          disabled={isApproving || !anyKept}
        >
          {isApproving ? 'Approving...' : 'Approve'}
        </button>
        <button className={styles.dismissButton} onClick={onDismiss} disabled={isApproving}>
          Dismiss
        </button>
      </div>
    </li>
  );
}

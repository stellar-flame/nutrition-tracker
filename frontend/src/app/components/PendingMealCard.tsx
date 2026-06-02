import { useState } from 'react';
import type { PendingMeal, MealItem } from '@/types/meals';
import styles from './Meals.module.css';

interface Props {
  meal: PendingMeal;
  onApprove: (items?: MealItem[]) => void;
  onDismiss: () => void;
  isApproving: boolean;
}

export default function PendingMealCard({ meal, onApprove, onDismiss, isApproving }: Props) {
  const [editMode, setEditMode] = useState(false);
  const [editedItems, setEditedItems] = useState<MealItem[]>([]);

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

  const handleEditStart = () => {
    setEditedItems(meal.items.map(item => ({ ...item })));
    setEditMode(true);
  };

  const handleFieldChange = (idx: number, field: keyof MealItem, value: string) => {
    setEditedItems(prev =>
      prev.map((item, i) =>
        i === idx ? { ...item, [field]: field === 'description' ? value : parseFloat(value) || 0 } : item
      )
    );
  };

  const totalKcal = (editMode ? editedItems : meal.items).reduce((s, it) => s + it.caloriesKcal, 0);

  return (
    <li className={`${styles.meal} ${styles.mealApproval}`}>
      <div className={styles.approvalHeader}>
        <div className={styles.mealMeta}>
          <strong className={styles.mealName}>{meal.description}</strong>
          <span className={styles.mealTime}>{meal.time}</span>
        </div>
        <span className={styles.approvalTotal}>{totalKcal.toLocaleString()} kcal</span>
      </div>

      <ul className={`${styles.mealItems} ${styles.mealItemsExpanded}`}>
        {(editMode ? editedItems : meal.items).map((item, i) => (
          <li key={i} className={styles.mealItem}>
            {editMode ? (
              <div className={styles.editRow}>
                <input
                  className={styles.editDesc}
                  value={item.description}
                  onChange={e => handleFieldChange(i, 'description', e.target.value)}
                />
                <div className={styles.editNutrients}>
                  {(['caloriesKcal', 'proteinG', 'carbsG', 'fatG', 'fiberG', 'sugarG', 'sodiumMg'] as const).map(field => (
                    <label key={field} className={styles.editField}>
                      <span className={styles.nutrientLabel}>{fieldLabel(field)}</span>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        value={item[field]}
                        onChange={e => handleFieldChange(i, field, e.target.value)}
                        className={styles.editInput}
                      />
                    </label>
                  ))}
                </div>
              </div>
            ) : (
              <>
                <div className={styles.itemHeader}>
                  <span className={styles.itemDesc}>{item.description}</span>
                  <span className={styles.itemCalories}>{item.caloriesKcal} kcal</span>
                </div>
                <div className={styles.itemNutrients}>
                  <span className={styles.nutrient}><span className={styles.nutrientLabel}>Protein</span><span className={styles.nutrientValue}>{item.proteinG}g</span></span>
                  <span className={styles.nutrient}><span className={styles.nutrientLabel}>Carbs</span><span className={styles.nutrientValue}>{item.carbsG}g</span></span>
                  <span className={styles.nutrient}><span className={styles.nutrientLabel}>Fat</span><span className={styles.nutrientValue}>{item.fatG}g</span></span>
                  <span className={styles.nutrient}><span className={styles.nutrientLabel}>Fiber</span><span className={styles.nutrientValue}>{item.fiberG}g</span></span>
                  <span className={styles.nutrient}><span className={styles.nutrientLabel}>Sugar</span><span className={styles.nutrientValue}>{item.sugarG}g</span></span>
                  <span className={styles.nutrient}><span className={styles.nutrientLabel}>Sodium</span><span className={styles.nutrientValue}>{item.sodiumMg}mg</span></span>
                </div>
              </>
            )}
          </li>
        ))}
      </ul>

      <div className={styles.approvalActions}>
        {editMode ? (
          <>
            <button
              className={styles.approveButton}
              onClick={() => onApprove(editedItems)}
              disabled={isApproving}
            >
              {isApproving ? 'Saving...' : 'Save & Approve'}
            </button>
            <button className={styles.cancelButton} onClick={() => setEditMode(false)} disabled={isApproving}>
              Cancel
            </button>
          </>
        ) : (
          <>
            <button className={styles.approveButton} onClick={() => onApprove()} disabled={isApproving}>
              {isApproving ? 'Approving...' : 'Approve'}
            </button>
            <button className={styles.editButton} onClick={handleEditStart} disabled={isApproving}>
              Edit
            </button>
          </>
        )}
      </div>
    </li>
  );
}

function fieldLabel(field: keyof MealItem): string {
  const labels: Record<keyof MealItem, string> = {
    description: 'Description',
    caloriesKcal: 'Calories',
    proteinG: 'Protein (g)',
    carbsG: 'Carbs (g)',
    fatG: 'Fat (g)',
    fiberG: 'Fiber (g)',
    sugarG: 'Sugar (g)',
    sodiumMg: 'Sodium (mg)',
  };
  return labels[field];
}


import styles from './NutritionSummary.module.css';
import { useNutritionSummary } from '@/app/hooks/useNutritionSummary';

function StatRow({
  label,
  value,
  unit,
}: {
  label: string;
  value: number;
  unit: string;
}) {
  return (
    <div role="listitem" className={styles.row}>
      <span className={styles.label}>{label}</span>
      <strong className={styles.value} aria-label={`${label} value`}>
        {value.toLocaleString()} {unit}
      </strong>
    </div>
  );
}
export default function NutritionSummary() {

  const { data, isLoading, error } = useNutritionSummary();

  if (isLoading) return <div>Loading…</div>;
  if (error) return <div role="alert">Failed to load</div>;
  if (!data) return <div>No data</div>;
return (
    <section role="region" aria-label="Nutrition summary" className={styles.section}>
      <header className={styles.header}>
        <h2 className={styles.title}>Today’s nutrition</h2>
        <small className={styles.date}>{data.date}</small>
      </header>
      <div role="list" aria-label="Nutrition stats" className={styles.stats}>
        <StatRow label="Calories" value={data.caloriesKcal} unit="kcal" />
        <StatRow label="Protein" value={data.proteinG} unit="g" />
        <StatRow label="Carbohydrates" value={data.carbsG} unit="g" />
        <StatRow label="Fat" value={data.fatG} unit="g" />
        <StatRow label="Fiber" value={data.fiberG} unit="g" />
        <StatRow label="Sugar" value={data.sugarG} unit="g" />
        <StatRow label="Sodium" value={data.sodiumMg} unit="mg" />
      </div>
    </section>
  );
}
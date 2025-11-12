
import styles from './NutritionSummary.module.css';

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
    const data = { 
    date: '2024-06-01',
    caloriesKcal: 2200,
    proteinG: 150,
    carbsG: 250,
    fatG: 70,
    fiberG: 30,
    sugarG: 90,
    sodiumMg: 2300,
  };
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
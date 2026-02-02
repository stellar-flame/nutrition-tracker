import NutritionSummary from "@/app/components/NutritionSummary";
import Meals from "@/app/components/Meals";


export default function Index() {
  return (
    <main style={{ padding: 24 }}>
      <h1>Nutrition Tracker</h1>
      <NutritionSummary />
      <Meals />
    </main>
  );
}
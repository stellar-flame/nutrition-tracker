import NutritionSummary from "@/app/components/NutritionSummary";
import Meals from "@/app/components/Meals";
import { useAuth } from "@/app/auth/AuthContext";
import { useNavigate } from "react-router-dom";

export default function Index() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  return (
    <main style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Nutrition Tracker</h1>
        <button onClick={() => { logout(); navigate('/login'); }}>Logout</button>
      </div>
      <NutritionSummary />
      <Meals />
    </main>
  );
}
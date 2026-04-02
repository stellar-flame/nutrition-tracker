import NutritionSummary from "@/app/components/NutritionSummary";
import Meals from "@/app/components/Meals";
import { useAuth } from "@/app/auth/AuthContext";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/apiClient";
import styles from "./Index.module.css";

export default function Index() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const { data: user } = useQuery({
    queryKey: ['me'],
    queryFn: () => api.get('/users/me').then(r => r.data),
  });

  return (
    <main style={{ padding: 24 }}>
      <div className={styles.header}>
        <h1 className={styles.title}>
          Nutrition Tracker
          {user?.first_name && <span className={styles.greeting}>— {user.first_name}</span>}
        </h1>
        <button onClick={() => { logout(); navigate('/login'); }}>Logout</button>
      </div>
      <NutritionSummary />
      <Meals />
    </main>
  );
}
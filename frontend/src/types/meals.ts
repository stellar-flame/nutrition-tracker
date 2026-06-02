export interface MealItem {
    description: string;
    caloriesKcal: number;
    proteinG: number;
    carbsG: number;
    fatG: number;
    fiberG: number;
    sugarG: number;
    sodiumMg: number;
}

export interface Meal {
    description: string;
    items: MealItem[];
    date: string;
    time: string;
    created_at: string;
    serving_size: number;
    status: 'complete';
}

export type PendingMealStatus = 'pending_ai' | 'pending_approval' | 'failed';

export interface PendingMeal {
    meal_id: string;
    description: string;
    date: string;
    time: string;
    created_at: string;
    status: PendingMealStatus;
    items: MealItem[];
}

export interface MealApprovePayload {
    items?: MealItem[];
}


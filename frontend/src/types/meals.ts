export interface MealItem {
    description: string;   // description of the meal
    caloriesKcal: number; // kilocalories (kcal)
    proteinG: number;     // grams (g)
    carbsG: number;       // grams (g)
    fatG: number;         // grams (g)
    fiberG: number;       // grams (g)
    sugarG: number;       // grams (g)
    sodiumMg: number;     // milligrams (mg>
}

export interface Meal { 
    description: string;   // description of the meal
    items: MealItem[]; // array of meal items
    date: string;         // YYYY-MM-DD
    time: string;         // HH:MM (24-hour format)
    serving_size: number; // number of servings
}
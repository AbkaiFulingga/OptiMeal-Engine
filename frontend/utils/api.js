// frontend/utils/api.js
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiService {
  static async generateMealPlan(userPreferences) {
    try {
      const response = await fetch(`${API_BASE_URL}/generate-meal-plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userPreferences),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error generating meal plan:', error);
      throw error;
    }
  }

  static async getRecipes() {
    try {
      const response = await fetch(`${API_BASE_URL}/recipes`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching recipes:', error);
      throw error;
    }
  }

  static async getIngredients() {
    try {
      const response = await fetch(`${API_BASE_URL}/ingredients`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching ingredients:', error);
      throw error;
    }
  }
}

export default ApiService;
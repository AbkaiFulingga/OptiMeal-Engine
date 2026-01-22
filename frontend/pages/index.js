import Head from 'next/head';
import { useState } from 'react';
import axios from 'axios';

export default function Home() {
  const [preferences, setPreferences] = useState({
    dietary_restrictions: [],
    allergies: '',
    dislikes: '',
    target_protein_g: '',
    target_carbs_g: '',
    target_fat_g: '',
    target_calories: '',
    preferred_cuisines: '',
    cooking_skill_level: 'intermediate',
    max_cooking_time_min: 60,
    weekly_budget: 100,
    max_repeats_per_week: 2
  });
  
  const [loading, setLoading] = useState(false);
  const [mealPlan, setMealPlan] = useState(null);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setPreferences(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleDietaryChange = (e) => {
    const { value, checked } = e.target;
    setPreferences(prev => {
      const current = prev.dietary_restrictions || [];
      let updated;
      
      if (checked) {
        updated = [...current, value];
      } else {
        updated = current.filter(item => item !== value);
      }
      
      return { ...prev, dietary_restrictions: updated };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Format the preferences for the API
      const formattedPrefs = {
        ...preferences,
        allergies: preferences.allergies.split(',').map(a => a.trim()).filter(a => a),
        dislikes: preferences.dislikes.split(',').map(d => d.trim()).filter(d => d),
        preferred_cuisines: preferences.preferred_cuisines.split(',').map(c => c.trim()).filter(c => c),
        target_protein_g: preferences.target_protein_g ? parseInt(preferences.target_protein_g) : null,
        target_carbs_g: preferences.target_carbs_g ? parseInt(preferences.target_carbs_g) : null,
        target_fat_g: preferences.target_fat_g ? parseInt(preferences.target_fat_g) : null,
        target_calories: preferences.target_calories ? parseInt(preferences.target_calories) : null,
      };
      
      const response = await axios.post('http://localhost:8000/generate-meal-plan', formattedPrefs);
      setMealPlan(response.data);
    } catch (error) {
      console.error('Error generating meal plan:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>OptiMeal - AI Smart Meal Planner</title>
        <meta name="description" content="AI-powered meal planning and grocery optimization" />
      </Head>

      <header className="bg-blue-600 text-white p-4 shadow-md">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">OptiMeal</h1>
          <nav>
            <ul className="flex space-x-4">
              <li><a href="#" className="hover:underline">Home</a></li>
              <li><a href="#" className="hover:underline">About</a></li>
              <li><a href="#" className="hover:underline">Contact</a></li>
            </ul>
          </nav>
        </div>
      </header>

      <main className="container mx-auto p-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Form */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Your Preferences</h2>
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-gray-700 mb-2">Dietary Restrictions</label>
                <div className="space-y-2">
                  {['vegetarian', 'vegan', 'keto', 'paleo', 'halal', 'kosher', 'gluten_free', 'dairy_free'].map(option => (
                    <label key={option} className="inline-flex items-center mr-4">
                      <input
                        type="checkbox"
                        value={option}
                        onChange={handleDietaryChange}
                        className="form-checkbox h-4 w-4 text-blue-600"
                      />
                      <span className="ml-2 capitalize">{option.replace('_', ' ')}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="mb-4">
                <label htmlFor="allergies" className="block text-gray-700 mb-2">Allergies (comma separated)</label>
                <input
                  type="text"
                  id="allergies"
                  name="allergies"
                  value={preferences.allergies}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="e.g., nuts, dairy, gluten"
                />
              </div>

              <div className="mb-4">
                <label htmlFor="dislikes" className="block text-gray-700 mb-2">Foods to Avoid (comma separated)</label>
                <input
                  type="text"
                  id="dislikes"
                  name="dislikes"
                  value={preferences.dislikes}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="e.g., mushrooms, olives"
                />
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label htmlFor="target_protein_g" className="block text-gray-700 mb-2">Target Protein (g/day)</label>
                  <input
                    type="number"
                    id="target_protein_g"
                    name="target_protein_g"
                    value={preferences.target_protein_g}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>
                <div>
                  <label htmlFor="target_carbs_g" className="block text-gray-700 mb-2">Target Carbs (g/day)</label>
                  <input
                    type="number"
                    id="target_carbs_g"
                    name="target_carbs_g"
                    value={preferences.target_carbs_g}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label htmlFor="target_fat_g" className="block text-gray-700 mb-2">Target Fat (g/day)</label>
                  <input
                    type="number"
                    id="target_fat_g"
                    name="target_fat_g"
                    value={preferences.target_fat_g}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>
                <div>
                  <label htmlFor="target_calories" className="block text-gray-700 mb-2">Target Calories (kcal/day)</label>
                  <input
                    type="number"
                    id="target_calories"
                    name="target_calories"
                    value={preferences.target_calories}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>
              </div>

              <div className="mb-4">
                <label htmlFor="preferred_cuisines" className="block text-gray-700 mb-2">Preferred Cuisines (comma separated)</label>
                <input
                  type="text"
                  id="preferred_cuisines"
                  name="preferred_cuisines"
                  value={preferences.preferred_cuisines}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="e.g., Italian, Mexican, Asian"
                />
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label htmlFor="cooking_skill_level" className="block text-gray-700 mb-2">Cooking Skill Level</label>
                  <select
                    id="cooking_skill_level"
                    name="cooking_skill_level"
                    value={preferences.cooking_skill_level}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="max_cooking_time_min" className="block text-gray-700 mb-2">Max Cooking Time (min/meal)</label>
                  <input
                    type="number"
                    id="max_cooking_time_min"
                    name="max_cooking_time_min"
                    value={preferences.max_cooking_time_min}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <label htmlFor="weekly_budget" className="block text-gray-700 mb-2">Weekly Budget ($)</label>
                  <input
                    type="number"
                    id="weekly_budget"
                    name="weekly_budget"
                    value={preferences.weekly_budget}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>
                <div>
                  <label htmlFor="max_repeats_per_week" className="block text-gray-700 mb-2">Max Recipe Repetitions</label>
                  <input
                    type="number"
                    id="max_repeats_per_week"
                    name="max_repeats_per_week"
                    value={preferences.max_repeats_per_week}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className={`w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {loading ? 'Generating...' : 'Generate Meal Plan'}
              </button>
            </form>
          </div>

          {/* Results Panel */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Your Meal Plan</h2>
            
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-4">Generating your personalized meal plan...</p>
              </div>
            ) : mealPlan ? (
              <div>
                <div className="mb-6 p-4 bg-green-50 rounded-md border border-green-200">
                  <h3 className="font-medium text-green-800">Summary</h3>
                  <p className="text-gray-700">Week of: {new Date(mealPlan.week_start_date).toLocaleDateString()}</p>
                  <p className="text-gray-700">Total Cost: ${mealPlan.total_cost.toFixed(2)}</p>
                  <div className="grid grid-cols-2 gap-2 mt-2">
                    <p className="text-gray-700">Protein: {mealPlan.nutritional_summary.total_protein_g.toFixed(1)}g</p>
                    <p className="text-gray-700">Carbs: {mealPlan.nutritional_summary.total_carbs_g.toFixed(1)}g</p>
                    <p className="text-gray-700">Fat: {mealPlan.nutritional_summary.total_fat_g.toFixed(1)}g</p>
                    <p className="text-gray-700">Calories: {mealPlan.nutritional_summary.total_calories.toFixed(1)}</p>
                  </div>
                </div>

                <div className="mb-6">
                  <h3 className="font-medium mb-2">Weekly Schedule</h3>
                  {mealPlan.daily_meals.map((day, index) => (
                    <div key={index} className="mb-4 border-b pb-4">
                      <h4 className="font-semibold">{day.date ? new Date(day.date).toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' }) : `Day ${index + 1}`}</h4>
                      <div className="grid grid-cols-3 gap-2 mt-2">
                        {day.meals.map((meal, mealIndex) => (
                          <div key={mealIndex} className="border rounded p-2 bg-blue-50">
                            <p className="text-sm font-medium">{meal.meal_type}</p>
                            <p className="text-xs truncate">{meal.recipe?.name || 'No recipe'}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                <div>
                  <h3 className="font-medium mb-2">Grocery List</h3>
                  <div className="bg-gray-50 p-4 rounded-md max-h-60 overflow-y-auto">
                    {Object.entries(mealPlan.grocery_list.items_by_section || {}).map(([section, items]) => (
                      <div key={section} className="mb-3">
                        <h4 className="font-medium text-sm uppercase text-gray-600 border-b">{section}</h4>
                        <ul className="mt-1 text-sm">
                          {items.map((item, idx) => (
                            <li key={idx} className="flex justify-between">
                              <span>{item.name}</span>
                              <span>{item.quantity.toFixed(1)} {item.unit}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>Your meal plan will appear here after you submit your preferences.</p>
                <p className="mt-2 text-sm">Enter your dietary requirements and click "Generate Meal Plan"</p>
              </div>
            )}
          </div>
        </div>
      </main>

      <footer className="bg-gray-800 text-white p-4 mt-8">
        <div className="container mx-auto text-center">
          <p>© 2023 OptiMeal - AI-Powered Meal Planning</p>
        </div>
      </footer>
    </div>
  );
}
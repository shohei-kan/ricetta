import { apiRequest } from './api'

export type SimpleCategory = {
  id: number
  name: string
}

export type SimpleUnit = {
  id: number
  name: string
}

export type RecipeListItem = {
  id: number
  name: string
  category: SimpleCategory | null
  base_yield_quantity: string
  base_yield_unit: SimpleUnit
  main_image: string | null
  updated_at: string
}

export type RecipeDetailIngredient = {
  id: number
  ingredient: {
    id: number
    name: string
  }
  quantity: string
  unit: SimpleUnit
  sort_order: number
  memo: string
}

export type RecipeStep = {
  id: number
  step_number: number
  instruction: string
  image: string | null
  memo: string
}

export type RecipeCostSummary = {
  material_cost: string
  selling_price: string | null
  cost_rate: string | null
  gross_profit: string | null
}

export type RecipeDetail = {
  id: number
  name: string
  category: SimpleCategory | null
  description: string
  main_image: string | null
  base_yield_quantity: string
  base_yield_unit: SimpleUnit
  selling_price: string | null
  notes: string
  allergen_notes: string
  ingredients: RecipeDetailIngredient[]
  steps: RecipeStep[]
  cost_summary: RecipeCostSummary
}

export type RecipeIngredientFormPayload = {
  ingredient_id: number
  quantity: string
  unit_id: number
  sort_order?: number
  memo?: string
}

export type RecipeStepFormPayload = {
  step_number: number
  instruction: string
  image?: string | null
  memo?: string
}

export type RecipeFormPayload = {
  name: string
  category_id?: number | null
  description?: string
  main_image?: string | null
  base_yield_quantity: string
  base_yield_unit_id: number
  selling_price?: string | null
  notes?: string
  allergen_notes?: string
  ingredients: RecipeIngredientFormPayload[]
  steps: RecipeStepFormPayload[]
}

export function fetchRecipes(params: { q?: string; category?: string | number } = {}) {
  const query = new URLSearchParams()
  if (params.q) {
    query.set('q', params.q)
  }
  if (params.category !== undefined && params.category !== '') {
    query.set('category', String(params.category))
  }

  const queryString = query.toString()
  return apiRequest<RecipeListItem[]>(`/recipes/${queryString ? `?${queryString}` : ''}`)
}

export function fetchRecipeDetail(id: number) {
  return apiRequest<RecipeDetail>(`/recipes/${id}/`)
}

export function createRecipe(payload: RecipeFormPayload) {
  return apiRequest<RecipeDetail>('/recipes/', {
    method: 'POST',
    body: payload,
  })
}

export function updateRecipe(id: number, payload: RecipeFormPayload) {
  return apiRequest<RecipeDetail>(`/recipes/${id}/`, {
    method: 'PATCH',
    body: payload,
  })
}

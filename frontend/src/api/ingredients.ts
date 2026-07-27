import { apiRequest } from './api'

export type SimpleUnit = {
  id: number
  name: string
}

export type IngredientCostMode = 'none' | 'same_unit' | 'conversion'
export type IngredientType = 'raw' | 'prep_recipe'

export type SourceRecipeSummary = {
  id: number
  name: string
  recipe_type: 'prep' | 'menu'
  base_yield_quantity: string
  base_yield_unit: SimpleUnit
}

export type IngredientListItem = {
  id: number
  name: string
  supplier: string
  ingredient_type: IngredientType
  source_recipe: SourceRecipeSummary | null
  cost_mode: IngredientCostMode
  purchase_quantity: string | null
  purchase_unit: SimpleUnit | null
  purchase_price: string | null
  usage_unit: SimpleUnit | null
  conversion: {
    from_quantity: string
    from_unit: SimpleUnit
    to_quantity: string
    to_unit: SimpleUnit
  } | null
  unit_cost_label: string | null
}

export type IngredientDetail = IngredientListItem & {
  memo: string
}

export type IngredientFormPayload = {
  name: string
  supplier?: string
  memo?: string
  ingredient_type: IngredientType
  source_recipe_id?: number | null
  cost_mode: IngredientCostMode
  purchase_quantity?: string | null
  purchase_unit_id?: number | null
  purchase_price?: string | null
  usage_unit_id?: number | null
  conversion_from_quantity?: string | null
  conversion_from_unit_id?: number | null
  conversion_to_quantity?: string | null
  conversion_to_unit_id?: number | null
}

export function fetchIngredients(params: { q?: string } = {}) {
  const query = new URLSearchParams()
  if (params.q) {
    query.set('q', params.q)
  }

  const queryString = query.toString()
  return apiRequest<IngredientListItem[]>(`/ingredients/${queryString ? `?${queryString}` : ''}`)
}

export function fetchIngredientDetail(id: number) {
  return apiRequest<IngredientDetail>(`/ingredients/${id}/`)
}

export function createIngredient(payload: IngredientFormPayload) {
  return apiRequest<IngredientDetail>('/ingredients/', {
    method: 'POST',
    body: payload,
  })
}

export function updateIngredient(id: number, payload: IngredientFormPayload) {
  return apiRequest<IngredientDetail>(`/ingredients/${id}/`, {
    method: 'PATCH',
    body: payload,
  })
}

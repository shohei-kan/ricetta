import { apiRequest } from './api'

export type SimpleUnit = {
  id: number
  name: string
}

export type IngredientCostMode = 'none' | 'same_unit' | 'conversion'

export type IngredientListItem = {
  id: number
  name: string
  supplier: string
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

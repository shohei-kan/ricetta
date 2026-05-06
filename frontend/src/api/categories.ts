import { apiRequest } from './api'

export type Category = {
  id: number
  name: string
  sort_order: number
  is_active: boolean
}

export function fetchCategories() {
  return apiRequest<Category[]>('/categories/')
}

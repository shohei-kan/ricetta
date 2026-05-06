import { apiRequest } from './api'

export type Category = {
  id: number
  name: string
  sort_order: number
  is_active: boolean
}

export type CategoryPayload = {
  name: string
  sort_order?: number
  is_active?: boolean
}

export function fetchCategories() {
  return apiRequest<Category[]>('/categories/')
}

export function createCategory(payload: CategoryPayload) {
  return apiRequest<Category>('/categories/', {
    method: 'POST',
    body: payload,
  })
}

export function updateCategory(id: number, payload: CategoryPayload) {
  return apiRequest<Category>(`/categories/${id}/`, {
    method: 'PATCH',
    body: payload,
  })
}

export function deleteCategory(id: number) {
  return apiRequest<null>(`/categories/${id}/`, {
    method: 'DELETE',
  })
}

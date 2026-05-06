import { apiRequest } from './api'

export type UnitType = 'weight' | 'volume' | 'count' | 'custom'

export type Unit = {
  id: number
  name: string
  unit_type: UnitType
  is_default: boolean
  is_standard: boolean
  sort_order: number
  is_active: boolean
}

export type UnitPayload = {
  name: string
  unit_type: UnitType
  sort_order?: number
  is_active?: boolean
}

export function fetchUnits() {
  return apiRequest<Unit[]>('/units/')
}

export function createUnit(payload: UnitPayload) {
  return apiRequest<Unit>('/units/', {
    method: 'POST',
    body: payload,
  })
}

export function updateUnit(id: number, payload: UnitPayload) {
  return apiRequest<Unit>(`/units/${id}/`, {
    method: 'PATCH',
    body: payload,
  })
}

export function deleteUnit(id: number) {
  return apiRequest<null>(`/units/${id}/`, {
    method: 'DELETE',
  })
}

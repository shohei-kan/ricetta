import { apiRequest } from './api'

export type Unit = {
  id: number
  name: string
  unit_type: 'weight' | 'volume' | 'count' | 'custom'
  is_default: boolean
}

export function fetchUnits() {
  return apiRequest<Unit[]>('/units/')
}

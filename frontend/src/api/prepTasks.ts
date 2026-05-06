import { apiRequest } from './api'

export type PrepTaskStatus = 'todo' | 'doing' | 'done'

export type PrepTask = {
  id: number
  recipe: {
    id: number
    name: string
  }
  planned_quantity: string
  planned_unit: {
    id: number
    name: string
  }
  status: PrepTaskStatus
  memo: string
  sort_order: number
  completed_at: string | null
}

export type PrepTaskListResponse = {
  date: string
  summary: Record<PrepTaskStatus, number>
  tasks: PrepTask[]
}

export function fetchPrepTasks(date?: string): Promise<PrepTaskListResponse> {
  const query = date ? `?date=${encodeURIComponent(date)}` : ''
  return apiRequest(`/prep-tasks/${query}`)
}

export function updatePrepTaskStatus(
  id: number,
  status: PrepTaskStatus,
): Promise<{ id: number; status: PrepTaskStatus; completed_at: string | null }> {
  return apiRequest(`/prep-tasks/${id}/status/`, {
    method: 'PATCH',
    body: { status },
  })
}

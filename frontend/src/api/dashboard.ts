import { apiRequest } from './api'

export type StatusKey = 'todo' | 'doing' | 'done'

export type SummaryUnit = {
  id: number
  name: string
}

export type SummaryRecipe = {
  id: number
  name: string
}

export type DashboardTask = {
  id: number
  recipe: SummaryRecipe
  planned_quantity: string
  planned_unit: SummaryUnit
  status: StatusKey
  memo: string
  sort_order: number
}

export type DashboardRecipe = {
  id: number
  name: string
  category: null | {
    id: number
    name: string
  }
}

export type DashboardData = {
  date: string
  prep_summary: Record<StatusKey, number>
  next_tasks: DashboardTask[]
  frequent_recipes: DashboardRecipe[]
  stats: {
    recipe_count: number
    ingredient_count: number
    prep_task_count: number
  }
  alerts: unknown[]
}

export function fetchDashboard(date?: string): Promise<DashboardData> {
  const query = date ? `?date=${encodeURIComponent(date)}` : ''
  return apiRequest(`/dashboard/${query}`)
}

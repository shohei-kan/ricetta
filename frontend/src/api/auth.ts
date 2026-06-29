import { apiRequest } from './api'

export type AuthUser = {
  id: number
  email: string
  name: string
}

export type AuthShop = {
  id: number
  name: string
}

export type AuthMembership = {
  role: 'owner' | 'staff'
  display_name: string
}

export type AuthSession = {
  user: AuthUser
  shop: AuthShop
  membership: AuthMembership
}

export type LoginInput = {
  email: string
  password: string
}

export type DisplayNameInput = {
  display_name: string
}

export function fetchCsrf(): Promise<{ detail: string }> {
  return apiRequest('/auth/csrf/')
}

export function fetchMe(): Promise<AuthSession> {
  return apiRequest('/auth/me/')
}

export function updateDisplayName(input: DisplayNameInput): Promise<AuthSession> {
  return apiRequest('/auth/me/', {
    method: 'PATCH',
    body: input,
  })
}

export function login(input: LoginInput): Promise<AuthSession> {
  return apiRequest('/auth/login/', {
    method: 'POST',
    body: input,
  })
}

export function logout(): Promise<{ detail: string }> {
  return apiRequest('/auth/logout/', {
    method: 'POST',
  })
}

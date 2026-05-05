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

export function fetchCsrf(): Promise<{ detail: string }> {
  return apiRequest('/auth/csrf/')
}

export function fetchMe(): Promise<AuthSession> {
  return apiRequest('/auth/me/')
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

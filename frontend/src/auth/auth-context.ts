import { createContext } from 'react'
import type { AuthSession, LoginInput } from '../api/auth'

export type AuthContextValue = {
  session: AuthSession | null
  loading: boolean
  error: string | null
  login: (input: LoginInput) => Promise<void>
  logout: () => Promise<void>
  refreshMe: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)

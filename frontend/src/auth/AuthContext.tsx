import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import {
  fetchCsrf,
  fetchMe,
  login as loginRequest,
  logout as logoutRequest,
  type AuthSession,
  type LoginInput,
} from '../api/auth'
import { ApiError } from '../api/api'
import { AuthContext } from './auth-context'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<AuthSession | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refreshMe = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const nextSession = await fetchMe()
      setSession(nextSession)
    } catch (caught) {
      if (caught instanceof ApiError && caught.status === 401) {
        setSession(null)
      } else {
        setError('ログイン状態を確認できませんでした。')
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    let isActive = true

    async function loadSession() {
      try {
        const nextSession = await fetchMe()
        if (isActive) {
          setSession(nextSession)
        }
      } catch (caught) {
        if (isActive && caught instanceof ApiError && caught.status === 401) {
          setSession(null)
        } else if (isActive) {
          setError('ログイン状態を確認できませんでした。')
        }
      } finally {
        if (isActive) {
          setLoading(false)
        }
      }
    }

    void loadSession()

    return () => {
      isActive = false
    }
  }, [])

  const login = useCallback(async (input: LoginInput) => {
    setError(null)
    await fetchCsrf()
    const nextSession = await loginRequest(input)
    setSession(nextSession)
  }, [])

  const logout = useCallback(async () => {
    setError(null)
    try {
      await logoutRequest()
    } finally {
      setSession(null)
    }
  }, [])

  const value = useMemo(
    () => ({
      session,
      loading,
      error,
      login,
      logout,
      refreshMe,
    }),
    [error, loading, login, logout, refreshMe, session],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

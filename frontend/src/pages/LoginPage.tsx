import { useState, type FormEvent } from 'react'
import { ApiError } from '../api/api'
import { ricettaLogoFull } from '../assets'
import { useAuth } from '../auth/useAuth'

type LoginPageProps = {
  navigate: (path: string) => void
}

export function LoginPage({ navigate }: LoginPageProps) {
  const { login } = useAuth()
  const [email, setEmail] = useState('owner@example.com')
  const [password, setPassword] = useState('password')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)

    try {
      await login({ email, password })
      navigate('/dashboard')
    } catch (caught) {
      if (caught instanceof ApiError) {
        setError(caught.message)
      } else {
        setError('ログインに失敗しました。もう一度お試しください。')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="min-h-screen bg-[#f7f3ec] px-5 py-8 text-[#2a241f]">
      <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-md flex-col justify-center">
        <div className="mb-6 flex justify-center md:mb-8">
          <img
            alt="Ricetta"
            className="block h-auto w-full max-w-80 md:max-w-120"
            src={ricettaLogoFull}
          />
        </div>

        <form
          className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-[0_20px_60px_rgba(75,56,35,0.08)]"
          onSubmit={handleSubmit}
        >
          <label className="block text-left text-sm font-semibold text-[#4b4037]">
            メールアドレス
            <input
              autoComplete="email"
              className="mt-2 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 py-3 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
              onChange={(event) => setEmail(event.target.value)}
              type="email"
              value={email}
            />
          </label>

          <label className="mt-4 block text-left text-sm font-semibold text-[#4b4037]">
            パスワード
            <input
              autoComplete="current-password"
              className="mt-2 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 py-3 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
              onChange={(event) => setPassword(event.target.value)}
              type="password"
              value={password}
            />
          </label>

          {error && (
            <p className="mt-4 rounded-lg bg-[#fff0ed] px-4 py-3 text-left text-sm font-medium text-[#a23d2d]">
              {error}
            </p>
          )}

          <button
            className="mt-5 w-full rounded-lg bg-[#c76738] px-4 py-3 text-base font-bold text-white transition hover:bg-[#b65b31] disabled:cursor-not-allowed disabled:opacity-60"
            disabled={submitting}
            type="submit"
          >
            {submitting ? 'ログイン中...' : 'ログイン'}
          </button>
        </form>
      </div>
    </main>
  )
}

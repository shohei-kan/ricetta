import { useState, type FormEvent } from 'react'
import { ApiError } from '../api/api'
import { ricettaLogoFull } from '../assets'
import { useAuth } from '../auth/useAuth'
import { isDemoMode } from '../config/demo'

type LoginPageProps = {
  navigate: (path: string) => void
}

type DemoAccountType = 'owner' | 'staff'

const demoAccounts: Record<
  DemoAccountType,
  {
    description: string
    email: string
    label: string
    password: string
    restriction?: string
  }
> = {
  owner: {
    description:
      'レシピ・材料・カテゴリ・単位・店舗情報の編集、仕込み・メモ操作ができます。',
    email: 'owner@example.com',
    label: 'オーナー',
    password: 'password',
  },
  staff: {
    description: 'レシピ・材料・カテゴリ・単位の閲覧、仕込み・メモ操作ができます。',
    email: 'staff@example.com',
    label: 'スタッフ',
    password: 'password',
    restriction: 'レシピ・材料・カテゴリ・単位・店舗情報の編集はできません。',
  },
}

export function LoginPage({ navigate }: LoginPageProps) {
  const { login } = useAuth()
  const [selectedDemoAccount, setSelectedDemoAccount] =
    useState<DemoAccountType | null>(isDemoMode ? 'owner' : null)
  const [email, setEmail] = useState(isDemoMode ? demoAccounts.owner.email : '')
  const [password, setPassword] = useState(
    isDemoMode ? demoAccounts.owner.password : '',
  )
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function selectDemoAccount(accountType: DemoAccountType) {
    const account = demoAccounts[accountType]
    setSelectedDemoAccount(accountType)
    setEmail(account.email)
    setPassword(account.password)
    setError(null)
  }

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
      <div
        className={`mx-auto flex min-h-[calc(100vh-4rem)] flex-col justify-center ${
          isDemoMode ? 'max-w-3xl' : 'max-w-md'
        }`}
      >
        <div className="mb-6 flex justify-center md:mb-8">
          <img
            alt="Ricetta"
            className="block h-auto w-full max-w-80 md:max-w-120"
            src={ricettaLogoFull}
          />
        </div>

        <form
          className="mx-auto w-full max-w-md rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-[0_20px_60px_rgba(75,56,35,0.08)]"
          onSubmit={handleSubmit}
        >
          <label className="block text-left text-sm font-semibold text-[#4b4037]">
            メールアドレス
            <input
              autoComplete="email"
              className="mt-2 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 py-3 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
              onChange={(event) => {
                setEmail(event.target.value)
                setSelectedDemoAccount(null)
              }}
              type="email"
              value={email}
            />
          </label>

          <label className="mt-4 block text-left text-sm font-semibold text-[#4b4037]">
            パスワード
            <input
              autoComplete="current-password"
              className="mt-2 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 py-3 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
              onChange={(event) => {
                setPassword(event.target.value)
                setSelectedDemoAccount(null)
              }}
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

        {isDemoMode && (
          <DemoAccountInfo
            onSelect={selectDemoAccount}
            selectedAccount={selectedDemoAccount}
          />
        )}
      </div>
    </main>
  )
}

function DemoAccountInfo({
  onSelect,
  selectedAccount,
}: {
  onSelect: (accountType: DemoAccountType) => void
  selectedAccount: DemoAccountType | null
}) {
  return (
    <section className="mt-5 rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-4 text-left shadow-[0_16px_40px_rgba(75,56,35,0.06)] md:p-5">
      <p className="text-sm font-bold text-[#c76738]">公開デモ用アカウント</p>
      <p className="mt-2 text-sm leading-6 text-[#75685e]">
        この環境は公開デモです。入力内容は定期的に初期化され、実店舗データではありません。
      </p>
      <p className="mt-2 text-sm leading-6 text-[#8a7c70]">
        アカウントを選択すると、ログインフォームに入力されます。
      </p>

      <div className="mt-4 grid items-start gap-3 md:grid-cols-2">
        {Object.entries(demoAccounts).map(([accountType, account]) => (
          <DemoAccountCard
            accountType={accountType as DemoAccountType}
            description={account.description}
            email={account.email}
            isSelected={selectedAccount === accountType}
            key={accountType}
            label={account.label}
            onSelect={onSelect}
            password={account.password}
            restriction={account.restriction}
          />
        ))}
      </div>
    </section>
  )
}

function DemoAccountCard({
  accountType,
  description,
  email,
  isSelected,
  label,
  onSelect,
  password,
  restriction,
}: {
  accountType: DemoAccountType
  description: string
  email: string
  isSelected: boolean
  label: string
  onSelect: (accountType: DemoAccountType) => void
  password: string
  restriction?: string
}) {
  return (
    <button
      aria-pressed={isSelected}
      className={`flex h-full flex-col justify-start rounded-lg border p-3 text-left transition md:p-4 ${
        isSelected
          ? 'border-[#c76738] bg-[#fff5ed] shadow-[0_10px_24px_rgba(199,103,56,0.12)]'
          : 'border-[#eadfce] bg-[#fbf7f0] hover:border-[#dcb894] hover:bg-[#fffaf3]'
      }`}
      onClick={() => onSelect(accountType)}
      type="button"
    >
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-base font-bold text-[#2e2822]">{label}</h2>
        {isSelected && (
          <span className="rounded-full bg-[#c76738] px-2 py-0.5 text-xs font-bold text-white">
            選択中
          </span>
        )}
      </div>
      <p className="mt-2 rounded-md bg-white px-3 py-2 font-mono text-sm font-semibold text-[#5d5148]">
        {email} / {password}
      </p>
      <p className="mt-2 text-sm leading-6 text-[#75685e]">{description}</p>
      {restriction && (
        <p className="mt-2 rounded-md bg-[#fff0ed] px-3 py-2 text-sm font-semibold leading-6 text-[#8f4b3a]">
          {restriction}
        </p>
      )}
    </button>
  )
}

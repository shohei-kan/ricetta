import { useEffect, useState, type FormEvent } from 'react'
import { updateDisplayName } from '../api/auth'
import { ApiError } from '../api/api'
import {
  fetchShop,
  updateShop,
  type Shop,
  type ShopUpdateInput,
} from '../api/shop'
import { useAuth } from '../auth/useAuth'
import { AutoResizeTextarea } from '../components/ui/AutoResizeTextarea'

const emptyShopForm: ShopUpdateInput = {
  name: '',
  business_type: '',
  memo: '',
}

export function AccountPage() {
  const { logout, refreshMe, session } = useAuth()
  const [shop, setShop] = useState<Shop | null>(null)
  const [shopForm, setShopForm] = useState<ShopUpdateInput>(emptyShopForm)
  const [displayName, setDisplayName] = useState(session?.membership.display_name ?? '')
  const [loading, setLoading] = useState(true)
  const [editingShop, setEditingShop] = useState(false)
  const [savingShop, setSavingShop] = useState(false)
  const [savingName, setSavingName] = useState(false)
  const [shopError, setShopError] = useState<string | null>(null)
  const [nameError, setNameError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    async function loadShop() {
      setLoading(true)
      setShopError(null)
      try {
        const response = await fetchShop()
        if (active) {
          setShop(response)
          setShopForm(toShopForm(response))
        }
      } catch {
        if (active) {
          setShopError('店舗情報を読み込めませんでした。もう一度お試しください。')
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    void loadShop()
    return () => {
      active = false
    }
  }, [])

  if (!session) {
    return null
  }

  const isOwner = session.membership.role === 'owner'

  async function handleShopSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSavingShop(true)
    setShopError(null)
    try {
      const response = await updateShop(shopForm)
      setShop(response)
      setShopForm(toShopForm(response))
      setEditingShop(false)
      await refreshMe()
    } catch (caught) {
      setShopError(getRequestError(caught, '店舗情報の保存に失敗しました。'))
    } finally {
      setSavingShop(false)
    }
  }

  async function handleDisplayNameSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSavingName(true)
    setNameError(null)
    try {
      await updateDisplayName({ display_name: displayName })
      await refreshMe()
    } catch (caught) {
      setNameError(getRequestError(caught, '表示名の保存に失敗しました。'))
    } finally {
      setSavingName(false)
    }
  }

  function cancelShopEdit() {
    if (shop) {
      setShopForm(toShopForm(shop))
    }
    setShopError(null)
    setEditingShop(false)
  }

  return (
    <div className="mx-auto max-w-5xl px-5 py-6 md:px-8 md:py-8">
      <div className="mb-6 border-b border-[#ded2c2] pb-5">
        <p className="text-sm font-bold text-[#c76738]">Account</p>
        <h1 className="mt-2 text-3xl font-bold tracking-normal text-[#2e2822] md:text-4xl">
          アカウント
        </h1>
      </div>

      <div className="space-y-5">
        <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm md:p-6">
          <div className="flex items-center justify-between gap-4">
            <h2 className="text-2xl font-bold text-[#2e2822]">店舗情報</h2>
            {isOwner && shop && !editingShop && (
              <button
                className="whitespace-nowrap rounded-lg border border-[#dfd1bf] bg-white px-4 py-2 text-sm font-bold text-[#5d5148] transition hover:bg-[#fbf7f0]"
                onClick={() => setEditingShop(true)}
                type="button"
              >
                編集
              </button>
            )}
          </div>

          {loading && <p className="mt-5 text-[#75685e]">店舗情報を読み込んでいます...</p>}

          {!loading && shopError && !shop && (
            <p className="mt-5 rounded-lg bg-[#fff0ed] px-4 py-3 text-sm font-medium text-[#a23d2d]">
              {shopError}
            </p>
          )}

          {shop && editingShop ? (
            <form className="mt-5 space-y-4" onSubmit={handleShopSubmit}>
              <TextField
                label="店舗名"
                onChange={(value) => setShopForm((current) => ({ ...current, name: value }))}
                required
                value={shopForm.name}
              />
              <TextField
                label="業態"
                onChange={(value) => setShopForm((current) => ({ ...current, business_type: value }))}
                value={shopForm.business_type}
              />
              <label className="block">
                <span className="text-sm font-semibold text-[#4b4037]">メモ</span>
                <AutoResizeTextarea
                  className="mt-2 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 py-3 text-base leading-7 text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
                  onChange={(event) => setShopForm((current) => ({ ...current, memo: event.target.value }))}
                  value={shopForm.memo}
                />
              </label>
              {shopError && <ErrorBox message={shopError} />}
              <div className="flex flex-wrap gap-3">
                <button
                  className="rounded-lg bg-[#c76738] px-5 py-3 text-sm font-bold text-white transition hover:bg-[#b65b31] disabled:cursor-not-allowed disabled:opacity-60"
                  disabled={savingShop}
                  type="submit"
                >
                  {savingShop ? '保存中...' : '保存'}
                </button>
                <button
                  className="rounded-lg border border-[#dfd1bf] bg-white px-5 py-3 text-sm font-bold text-[#5d5148] transition hover:bg-[#fbf7f0]"
                  onClick={cancelShopEdit}
                  type="button"
                >
                  キャンセル
                </button>
              </div>
            </form>
          ) : shop ? (
            <dl className="mt-5 grid gap-4 sm:grid-cols-2">
              <InfoItem label="店舗名" value={shop.name} />
              <InfoItem label="業態" value={shop.business_type || '未設定'} />
              <InfoItem className="sm:col-span-2" label="メモ" value={shop.memo || '未設定'} />
            </dl>
          ) : null}

          {!isOwner && !loading && (
            <p className="mt-5 text-sm text-[#75685e]">店舗情報の編集はオーナーのみ行えます。</p>
          )}
        </section>

        <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm md:p-6">
          <h2 className="text-2xl font-bold text-[#2e2822]">あなたの情報</h2>
          <dl className="mt-5 grid gap-4 sm:grid-cols-2">
            <InfoItem label="メールアドレス" value={session.user.email} />
            <InfoItem label="権限" value={roleLabel(session.membership.role)} />
          </dl>

          <form className="mt-5 border-t border-[#eadfce] pt-5" onSubmit={handleDisplayNameSubmit}>
            <TextField
              label="表示名"
              onChange={setDisplayName}
              value={displayName}
            />
            {nameError && <ErrorBox message={nameError} />}
            <button
              className="mt-4 rounded-lg bg-[#c76738] px-5 py-3 text-sm font-bold text-white transition hover:bg-[#b65b31] disabled:cursor-not-allowed disabled:opacity-60"
              disabled={savingName}
              type="submit"
            >
              {savingName ? '保存中...' : '表示名を保存'}
            </button>
          </form>
        </section>

        <section className="border-t border-[#ded2c2] pt-5">
          <button
            className="rounded-lg border border-[#dfd1bf] bg-[#fffdf9] px-5 py-3 text-sm font-bold text-[#5d5148] transition hover:bg-[#f1e9dd]"
            onClick={() => void logout()}
            type="button"
          >
            ログアウト
          </button>
        </section>
      </div>
    </div>
  )
}

function TextField({
  label,
  onChange,
  required = false,
  value,
}: {
  label: string
  onChange: (value: string) => void
  required?: boolean
  value: string
}) {
  return (
    <label className="block">
      <span className="text-sm font-semibold text-[#4b4037]">
        {label}{required ? ' *' : ''}
      </span>
      <input
        className="mt-2 min-h-12 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
        onChange={(event) => onChange(event.target.value)}
        required={required}
        type="text"
        value={value}
      />
    </label>
  )
}

function InfoItem({
  className = '',
  label,
  value,
}: {
  className?: string
  label: string
  value: string
}) {
  return (
    <div className={`rounded-lg bg-[#f7f1e8] px-4 py-3 ${className}`}>
      <dt className="text-sm font-semibold text-[#75685e]">{label}</dt>
      <dd className="mt-1 whitespace-pre-wrap font-bold break-words text-[#34291f]">{value}</dd>
    </div>
  )
}

function ErrorBox({ message }: { message: string }) {
  return (
    <p className="mt-4 rounded-lg bg-[#fff0ed] px-4 py-3 text-sm font-medium text-[#a23d2d]">
      {message}
    </p>
  )
}

function toShopForm(shop: Shop): ShopUpdateInput {
  return {
    name: shop.name,
    business_type: shop.business_type,
    memo: shop.memo,
  }
}

function roleLabel(role: 'owner' | 'staff') {
  return role === 'owner' ? 'オーナー' : 'スタッフ'
}

function getRequestError(caught: unknown, fallback: string) {
  return caught instanceof ApiError ? caught.message : fallback
}

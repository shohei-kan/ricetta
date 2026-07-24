import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { leafSprigSimple } from '../assets'
import { ApiError } from '../api/api'
import {
  createCategory,
  deleteCategory,
  fetchCategories,
  updateCategory,
  type Category,
  type CategoryPayload,
} from '../api/categories'
import {
  createUnit,
  deleteUnit,
  fetchUnits,
  updateUnit,
  type Unit,
  type UnitPayload,
  type UnitType,
} from '../api/units'
import { useAuth } from '../auth/useAuth'

type CategoryFormState = {
  name: string
  sort_order: string
}

type UnitFormState = {
  name: string
  unit_type: UnitType
  sort_order: string
}

const emptyCategoryForm: CategoryFormState = {
  name: '',
  sort_order: '',
}

const emptyUnitForm: UnitFormState = {
  name: '',
  unit_type: 'custom',
  sort_order: '',
}

const unitTypeLabels: Record<UnitType, string> = {
  weight: '重量',
  volume: '容量',
  count: '個数',
  custom: 'その他',
}

const unitTypeOptions: UnitType[] = ['weight', 'volume', 'count', 'custom']

export function SettingsPage() {
  const { session } = useAuth()
  const [categories, setCategories] = useState<Category[]>([])
  const [units, setUnits] = useState<Unit[]>([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [categoryForm, setCategoryForm] = useState<CategoryFormState>(emptyCategoryForm)
  const [unitForm, setUnitForm] = useState<UnitFormState>(emptyUnitForm)
  const [editingCategoryId, setEditingCategoryId] = useState<number | null>(null)
  const [editingUnitId, setEditingUnitId] = useState<number | null>(null)
  const [categoryError, setCategoryError] = useState<string | null>(null)
  const [unitError, setUnitError] = useState<string | null>(null)
  const [categorySaving, setCategorySaving] = useState(false)
  const [unitSaving, setUnitSaving] = useState(false)
  const [deletingKey, setDeletingKey] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    async function loadSettings() {
      try {
        const [categoryResponse, unitResponse] = await Promise.all([
          fetchCategories(),
          fetchUnits(),
        ])
        if (active) {
          setCategories(categoryResponse)
          setUnits(unitResponse)
        }
      } catch {
        if (active) {
          setLoadError('設定を読み込めませんでした。もう一度お試しください。')
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    void loadSettings()
    return () => {
      active = false
    }
  }, [])

  const sortedCategories = useMemo(
    () => [...categories].sort((a, b) => a.sort_order - b.sort_order || a.id - b.id),
    [categories],
  )
  const sortedUnits = useMemo(
    () => [...units].sort((a, b) => a.sort_order - b.sort_order || a.id - b.id),
    [units],
  )
  const canManageSettings = session?.membership.role === 'owner'

  async function handleCategorySubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setCategoryError(null)
    const error = validateCategoryForm(categoryForm)
    if (error) {
      setCategoryError(error)
      return
    }

    setCategorySaving(true)
    try {
      const payload = toCategoryPayload(categoryForm)
      if (editingCategoryId === null) {
        await createCategory(payload)
      } else {
        await updateCategory(editingCategoryId, payload)
      }
      setCategoryForm(emptyCategoryForm)
      setEditingCategoryId(null)
      await reloadLists()
    } catch (caught) {
      setCategoryError(formatError(caught, '保存に失敗しました。入力内容を確認してください。'))
    } finally {
      setCategorySaving(false)
    }
  }

  async function handleUnitSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setUnitError(null)
    const error = validateUnitForm(unitForm)
    if (error) {
      setUnitError(error)
      return
    }

    setUnitSaving(true)
    try {
      const payload = toUnitPayload(unitForm)
      if (editingUnitId === null) {
        await createUnit(payload)
      } else {
        await updateUnit(editingUnitId, payload)
      }
      setUnitForm(emptyUnitForm)
      setEditingUnitId(null)
      await reloadLists()
    } catch (caught) {
      setUnitError(formatError(caught, '保存に失敗しました。入力内容を確認してください。'))
    } finally {
      setUnitSaving(false)
    }
  }

  async function reloadLists() {
    const [categoryResponse, unitResponse] = await Promise.all([
      fetchCategories(),
      fetchUnits(),
    ])
    setCategories(categoryResponse)
    setUnits(unitResponse)
  }

  function startCategoryEdit(category: Category) {
    setCategoryError(null)
    setEditingCategoryId(category.id)
    setCategoryForm({
      name: category.name,
      sort_order: String(category.sort_order),
    })
  }

  function startUnitEdit(unit: Unit) {
    if (unit.is_standard) {
      return
    }
    setUnitError(null)
    setEditingUnitId(unit.id)
    setUnitForm({
      name: unit.name,
      unit_type: unit.unit_type,
      sort_order: String(unit.sort_order),
    })
  }

  async function handleCategoryDelete(category: Category) {
    if (!window.confirm('このカテゴリを削除しますか？')) {
      return
    }
    setCategoryError(null)
    setDeletingKey(`category-${category.id}`)
    try {
      await deleteCategory(category.id)
      await reloadLists()
      if (editingCategoryId === category.id) {
        setEditingCategoryId(null)
        setCategoryForm(emptyCategoryForm)
      }
    } catch (caught) {
      setCategoryError(formatError(caught, '削除に失敗しました。使用中の可能性があります。'))
    } finally {
      setDeletingKey(null)
    }
  }

  async function handleUnitDelete(unit: Unit) {
    if (unit.is_standard || !window.confirm('この単位を削除しますか？')) {
      return
    }
    setUnitError(null)
    setDeletingKey(`unit-${unit.id}`)
    try {
      await deleteUnit(unit.id)
      await reloadLists()
      if (editingUnitId === unit.id) {
        setEditingUnitId(null)
        setUnitForm(emptyUnitForm)
      }
    } catch (caught) {
      setUnitError(formatError(caught, '削除に失敗しました。使用中の可能性があります。'))
    } finally {
      setDeletingKey(null)
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-5xl px-5 py-6 md:px-7 md:py-8">
        <div className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-6 text-[#75685e] shadow-sm">
          設定を読み込んでいます...
        </div>
      </div>
    )
  }

  if (loadError) {
    return (
      <div className="mx-auto max-w-5xl px-5 py-6 md:px-7 md:py-8">
        <div className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-6 text-[#a23d2d] shadow-sm">
          {loadError}
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-7xl px-5 py-6 md:px-8 md:py-8">
      <div className="mb-6 border-b border-[#ded2c2] pb-5">
        <p className="text-sm font-bold text-[#c76738]">Settings</p>
        <div className="mt-2 flex items-center gap-3">
          <h1 className="text-3xl font-bold tracking-normal text-[#2e2822] md:text-4xl">
            設定
          </h1>
          <img
            alt=""
            aria-hidden="true"
            className="pointer-events-none h-7 w-7 select-none object-contain opacity-65"
            src={leafSprigSimple}
          />
        </div>
        <p className="mt-2 text-base leading-7 text-[#75685e]">
          MVPではレシピ台帳の運用に必要なカテゴリと単位だけを管理します。
        </p>
        {!canManageSettings && (
          <p className="mt-3 rounded-lg border border-[#eadfce] bg-[#fffdf9] px-4 py-3 text-sm font-semibold text-[#75685e]">
            カテゴリと単位の管理はオーナーのみ行えます。スタッフは現在の設定を確認できます。
          </p>
        )}
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm md:p-6">
          <h2 className="text-2xl font-bold text-[#2e2822]">レシピカテゴリ</h2>
          <p className="mt-2 text-sm leading-6 text-[#75685e]">
            Recipe Formで選ぶ分類です。現在Shopのカテゴリだけを管理します。
          </p>

          {canManageSettings && (
            <form className="mt-5 rounded-lg border border-[#eadfce] bg-white p-4" onSubmit={handleCategorySubmit}>
              <p className="text-lg font-bold text-[#34291f]">
                {editingCategoryId === null ? 'カテゴリを追加' : 'カテゴリを編集'}
              </p>
              <div className="mt-4 grid gap-3 sm:grid-cols-[minmax(0,1fr)_120px]">
                <TextField
                  label="カテゴリ名"
                  onChange={(value) => setCategoryForm((current) => ({ ...current, name: value }))}
                  required
                  value={categoryForm.name}
                />
                <TextField
                  inputMode="numeric"
                  label="表示順"
                  onChange={(value) => setCategoryForm((current) => ({ ...current, sort_order: value }))}
                  value={categoryForm.sort_order}
                />
              </div>
              {categoryError && <ErrorBox message={categoryError} />}
              <FormActions
                cancelLabel="キャンセル"
                isEditing={editingCategoryId !== null}
                onCancel={() => {
                  setEditingCategoryId(null)
                  setCategoryForm(emptyCategoryForm)
                  setCategoryError(null)
                }}
                saving={categorySaving}
              />
            </form>
          )}

          <div className="mt-5 space-y-3">
            {sortedCategories.length === 0 ? (
              <p className="rounded-lg bg-[#f1e7dc] px-4 py-5 text-[#75685e]">
                カテゴリがまだありません。よく使う分類を追加しましょう。
              </p>
            ) : (
              sortedCategories.map((category) => (
                <div className="rounded-lg border border-[#eadfce] bg-white p-4" key={category.id}>
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <p className="text-lg font-bold text-[#332820]">{category.name}</p>
                      <p className="mt-1 text-sm text-[#75685e]">表示順: {category.sort_order}</p>
                    </div>
                    {canManageSettings && (
                      <div className="flex gap-2">
                        <button
                          className="rounded-lg border border-[#dfd1bf] bg-white px-4 py-2 text-sm font-bold text-[#5d5148] transition hover:bg-[#fbf7f0]"
                          onClick={() => startCategoryEdit(category)}
                          type="button"
                        >
                          編集
                        </button>
                        <button
                          className="rounded-lg bg-[#fff0ed] px-4 py-2 text-sm font-semibold text-[#a23d2d] transition hover:bg-[#f9dfd9] disabled:cursor-not-allowed disabled:opacity-60"
                          disabled={deletingKey === `category-${category.id}`}
                          onClick={() => void handleCategoryDelete(category)}
                          type="button"
                        >
                          削除
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </section>

        <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm md:p-6">
          <h2 className="text-2xl font-bold text-[#2e2822]">単位</h2>
          <p className="mt-2 text-sm leading-6 text-[#75685e]">
            標準Unitは表示のみです。店舗独自Unitだけ追加・編集・削除できます。
          </p>

          {canManageSettings && (
            <form className="mt-5 rounded-lg border border-[#eadfce] bg-white p-4" onSubmit={handleUnitSubmit}>
              <p className="text-lg font-bold text-[#34291f]">
                {editingUnitId === null ? '単位を追加' : '単位を編集'}
              </p>
              <div className="mt-4 grid gap-3 sm:grid-cols-[minmax(0,1fr)_140px_120px]">
                <TextField
                  label="単位名"
                  onChange={(value) => setUnitForm((current) => ({ ...current, name: value }))}
                  required
                  value={unitForm.name}
                />
                <label className="block">
                  <span className="text-sm font-semibold text-[#4b4037]">種別 *</span>
                  <select
                    className="mt-2 min-h-12 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
                    onChange={(event) => setUnitForm((current) => ({
                      ...current,
                      unit_type: event.target.value as UnitType,
                    }))}
                    value={unitForm.unit_type}
                  >
                    {unitTypeOptions.map((type) => (
                      <option key={type} value={type}>
                        {unitTypeLabels[type]}
                      </option>
                    ))}
                  </select>
                </label>
                <TextField
                  inputMode="numeric"
                  label="表示順"
                  onChange={(value) => setUnitForm((current) => ({ ...current, sort_order: value }))}
                  value={unitForm.sort_order}
                />
              </div>
              {unitError && <ErrorBox message={unitError} />}
              <FormActions
                cancelLabel="キャンセル"
                isEditing={editingUnitId !== null}
                onCancel={() => {
                  setEditingUnitId(null)
                  setUnitForm(emptyUnitForm)
                  setUnitError(null)
                }}
                saving={unitSaving}
              />
            </form>
          )}

          <div className="mt-5 space-y-3">
            {sortedUnits.length === 0 ? (
              <p className="rounded-lg bg-[#f1e7dc] px-4 py-5 text-[#75685e]">
                単位がまだありません。
              </p>
            ) : (
              sortedUnits.map((unit) => (
                <div className={`rounded-lg border p-4 ${unit.is_standard ? 'border-[#eadfce] bg-[#fbf7f0]' : 'border-[#eadfce] bg-white'}`} key={unit.id}>
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="text-lg font-bold text-[#332820]">{unit.name}</p>
                        <span className="rounded-full bg-[#f1e7dc] px-3 py-1 text-xs font-bold text-[#75685e]">
                          {unitTypeLabels[unit.unit_type]}
                        </span>
                        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
                          unit.is_standard
                            ? 'bg-[#efe8dc] text-[#75685e]'
                            : 'bg-[#e7f0e4] text-[#4d7a55]'
                        }`}
                        >
                          {unit.is_standard ? '標準' : '店舗独自'}
                        </span>
                      </div>
                      <p className="mt-1 text-sm text-[#75685e]">表示順: {unit.sort_order}</p>
                      {unit.is_standard && (
                        <p className="mt-2 text-xs text-[#8a7a6d]">
                          標準単位は編集できません。
                        </p>
                      )}
                    </div>
                    {canManageSettings && !unit.is_standard && (
                      <div className="flex gap-2">
                        <button
                          className="rounded-lg border border-[#dfd1bf] bg-white px-4 py-2 text-sm font-bold text-[#5d5148] transition hover:bg-[#fbf7f0]"
                          onClick={() => startUnitEdit(unit)}
                          type="button"
                        >
                          編集
                        </button>
                        <button
                          className="rounded-lg bg-[#fff0ed] px-4 py-2 text-sm font-semibold text-[#a23d2d] transition hover:bg-[#f9dfd9] disabled:cursor-not-allowed disabled:opacity-60"
                          disabled={deletingKey === `unit-${unit.id}`}
                          onClick={() => void handleUnitDelete(unit)}
                          type="button"
                        >
                          削除
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  )
}

function TextField({
  inputMode,
  label,
  onChange,
  required,
  value,
}: {
  inputMode?: 'numeric'
  label: string
  onChange: (value: string) => void
  required?: boolean
  value: string
}) {
  return (
    <label className="block">
      <span className="text-sm font-semibold text-[#4b4037]">
        {label}
        {required ? ' *' : ''}
      </span>
      <input
        className="mt-2 min-h-12 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
        inputMode={inputMode}
        onChange={(event) => onChange(event.target.value)}
        value={value}
      />
    </label>
  )
}

function FormActions({
  cancelLabel,
  isEditing,
  onCancel,
  saving,
}: {
  cancelLabel: string
  isEditing: boolean
  onCancel: () => void
  saving: boolean
}) {
  return (
    <div className="mt-4 flex flex-col gap-3 sm:flex-row">
      <button
        className="rounded-lg bg-[#c76738] px-4 py-3 text-base font-bold text-white transition hover:bg-[#b65b31] disabled:cursor-not-allowed disabled:opacity-60"
        disabled={saving}
        type="submit"
      >
        {saving ? '保存中...' : '保存'}
      </button>
      {isEditing && (
        <button
          className="rounded-lg border border-[#dfd1bf] bg-white px-4 py-3 text-base font-bold text-[#5d5148] transition hover:bg-[#fbf7f0]"
          onClick={onCancel}
          type="button"
        >
          {cancelLabel}
        </button>
      )}
    </div>
  )
}

function ErrorBox({ message }: { message: string }) {
  return (
    <div className="mt-4 rounded-lg border border-[#f1c8c0] bg-[#fff0ed] p-4 text-sm font-semibold leading-6 text-[#a23d2d]">
      {message}
    </div>
  )
}

function validateCategoryForm(form: CategoryFormState) {
  if (!form.name.trim()) {
    return 'カテゴリ名を入力してください。'
  }
  return validateSortOrder(form.sort_order)
}

function validateUnitForm(form: UnitFormState) {
  if (!form.name.trim()) {
    return '単位名を入力してください。'
  }
  if (!form.unit_type) {
    return '種別を選択してください。'
  }
  return validateSortOrder(form.sort_order)
}

function validateSortOrder(value: string) {
  if (!value.trim()) {
    return null
  }
  return Number.isNaN(Number(value)) ? '表示順は数値で入力してください。' : null
}

function toCategoryPayload(form: CategoryFormState): CategoryPayload {
  return {
    name: form.name.trim(),
    sort_order: toNumberOrZero(form.sort_order),
  }
}

function toUnitPayload(form: UnitFormState): UnitPayload {
  return {
    name: form.name.trim(),
    unit_type: form.unit_type,
    sort_order: toNumberOrZero(form.sort_order),
  }
}

function toNumberOrZero(value: string) {
  return value.trim() ? Number(value) : 0
}

function formatError(caught: unknown, fallback: string) {
  if (caught instanceof ApiError) {
    if (typeof caught.data === 'string') {
      return caught.data
    }
    return `${fallback} ${JSON.stringify(caught.data)}`
  }
  return fallback
}

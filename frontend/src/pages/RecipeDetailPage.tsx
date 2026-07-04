import { useEffect, useRef, useState, type FormEvent, type TouchEvent } from 'react'
import { ApiError } from '../api/api'
import { createPrepTask } from '../api/prepTasks'
import { fetchRecipeDetail, type RecipeDetail } from '../api/recipes'
import { fetchUnits, type Unit } from '../api/units'

type RecipeDetailPageProps = {
  id: number
  navigate: (path: string) => void
}

export function RecipeDetailPage({ id, navigate }: RecipeDetailPageProps) {
  const [recipe, setRecipe] = useState<RecipeDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    async function loadRecipe() {
      setLoading(true)
      setError(null)
      try {
        const response = await fetchRecipeDetail(id)
        if (active) {
          setRecipe(response)
        }
      } catch {
        if (active) {
          setError('レシピ詳細を読み込めませんでした。一覧に戻って再度お試しください。')
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    void loadRecipe()
    return () => {
      active = false
    }
  }, [id])

  return (
    <div className="mx-auto max-w-7xl px-5 py-6 md:px-8 md:py-8">
      {(loading || error || !recipe) && <BackButton navigate={navigate} />}

      {loading && (
        <div className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-6 text-[#75685e] shadow-sm">
          レシピを読み込んでいます...
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-6 text-[#a23d2d] shadow-sm">
          {error}
        </div>
      )}

      {!loading && !error && recipe && <RecipeDetailContent navigate={navigate} recipe={recipe} />}
    </div>
  )
}

function RecipeDetailContent({
  navigate,
  recipe,
}: {
  navigate: (path: string) => void
  recipe: RecipeDetail
}) {
  const [showPrepForm, setShowPrepForm] = useState(false)
  const [activeTab, setActiveTab] = useState<RecipeDetailTab>('overview')
  const touchStart = useRef<{ x: number; y: number } | null>(null)

  const tabs: Array<{ id: RecipeDetailTab; label: string }> = [
    { id: 'overview', label: '概要' },
    { id: 'ingredients', label: '材料' },
    { id: 'steps', label: '作り方' },
  ]

  function handleTouchStart(event: TouchEvent<HTMLElement>) {
    if (isDesktopRecipeLayout() || event.touches.length !== 1) {
      touchStart.current = null
      return
    }

    const touch = event.touches[0]
    touchStart.current = { x: touch.clientX, y: touch.clientY }
  }

  function handleTouchEnd(event: TouchEvent<HTMLElement>) {
    const start = touchStart.current
    touchStart.current = null

    if (!start || isDesktopRecipeLayout() || event.changedTouches.length !== 1) {
      return
    }

    const touch = event.changedTouches[0]
    const deltaX = touch.clientX - start.x
    const deltaY = touch.clientY - start.y

    if (Math.abs(deltaX) < 50 || Math.abs(deltaX) <= Math.abs(deltaY)) {
      return
    }

    const currentIndex = tabs.findIndex((tab) => tab.id === activeTab)
    const nextIndex = deltaX < 0 ? currentIndex + 1 : currentIndex - 1
    const nextTab = tabs[nextIndex]

    if (nextTab) {
      setActiveTab(nextTab.id)
    }
  }

  return (
    <>
      <div
        className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
      >
        <BackButton navigate={navigate} withBottomMargin={false} />
        <div
          className={`${activeTab === 'overview' ? 'grid' : 'hidden lg:grid'} grid-cols-2 gap-3`}
        >
          <button
            aria-expanded={showPrepForm}
            className="min-h-12 rounded-lg bg-[#c76738] px-5 py-3 text-base font-bold text-white shadow-[0_8px_18px_rgba(198,103,56,0.22)] transition hover:bg-[#b65b31]"
            onClick={() => setShowPrepForm((current) => !current)}
            type="button"
          >
            仕込みに追加
          </button>
          <button
            className="min-h-12 rounded-lg border border-[#dfd1bf] bg-white px-5 py-3 text-base font-bold text-[#5d5148] transition hover:bg-[#fbf7f0]"
            onClick={() => navigate(`/recipes/${recipe.id}/edit`)}
            type="button"
          >
            編集
          </button>
        </div>
      </div>

      {showPrepForm && (
        <div className={`${activeTab === 'overview' ? 'block' : 'hidden lg:block'} mb-3`}>
          <AddToPrepPanel
            navigate={navigate}
            onCancel={() => setShowPrepForm(false)}
            recipe={recipe}
          />
        </div>
      )}

      <header className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 pb-4 shadow-sm md:p-6 md:pb-5">
        <div className="min-w-0">
          <p className="text-sm font-bold text-[#78936f]">
            {recipe.category?.name ?? 'カテゴリなし'}
          </p>
          <h1 className="mt-2 text-3xl font-bold tracking-normal text-[#2e2822] md:text-4xl lg:text-5xl">
            {recipe.name}
          </h1>
          <p className="mt-3 text-lg font-bold text-[#c76738] md:text-xl">
            基準: {formatQuantity(recipe.base_yield_quantity)} {recipe.base_yield_unit.name}
          </p>
          <p
            className={`${activeTab === 'overview' ? 'block' : 'hidden lg:block'} mt-4 whitespace-pre-wrap text-base leading-8 text-[#75685e]`}
          >
            {recipe.description || '説明はまだ登録されていません。'}
          </p>
        </div>
      </header>

      <nav
        aria-label="レシピ詳細の表示切り替え"
        className="mx-4 mt-3 max-w-lg rounded-xl border border-[#ded2c2] bg-[#eee5d8] p-1 shadow-sm md:mx-auto lg:hidden"
      >
        <div className="grid grid-cols-3 gap-1">
          {tabs.map((tab) => (
            <button
              aria-pressed={activeTab === tab.id}
              className={`min-h-12 rounded-lg px-2 py-3 text-sm font-bold transition sm:text-base ${
                activeTab === tab.id
                  ? 'bg-[#fffdf9] text-[#b65b31] shadow-sm ring-1 ring-[#dcc8b5]'
                  : 'text-[#75685e] hover:bg-[#f7f1e8] hover:text-[#5d5148]'
              }`}
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              type="button"
            >
              {tab.label}
            </button>
          ))}
        </div>
      </nav>

      <main
        className="mt-5 touch-pan-y"
        onTouchCancel={() => {
          touchStart.current = null
        }}
        onTouchEnd={handleTouchEnd}
        onTouchStart={handleTouchStart}
      >
        <div className="lg:grid lg:grid-cols-2 lg:items-start lg:gap-6">
          <div className={responsiveSectionClass(activeTab, 'ingredients')}>
            <IngredientsPanel recipe={recipe} />
          </div>
          <div className={responsiveSectionClass(activeTab, 'steps')}>
            <StepsPanel recipe={recipe} />
          </div>
        </div>

        <div
          className={
            activeTab === 'overview'
              ? 'mt-5 grid gap-5 lg:grid-cols-[minmax(360px,1.2fr)_repeat(2,minmax(0,0.7fr))]'
              : 'mt-5 hidden lg:grid lg:grid-cols-[minmax(360px,1.2fr)_repeat(2,minmax(0,0.7fr))] lg:gap-5'
          }
        >
          <CostSummaryCard recipe={recipe} />
          <NoteCard label="注意点 / メモ" value={recipe.notes || '特になし'} />
          <NoteCard label="アレルゲン" value={recipe.allergen_notes || '未設定'} />
        </div>
      </main>
    </>
  )
}

type RecipeDetailTab = 'overview' | 'ingredients' | 'steps'

function responsiveSectionClass(activeTab: RecipeDetailTab, section: RecipeDetailTab) {
  return activeTab === section ? 'block' : 'hidden lg:block'
}

function isDesktopRecipeLayout() {
  return window.matchMedia('(min-width: 1024px)').matches
}

function BackButton({
  navigate,
  withBottomMargin = true,
}: {
  navigate: (path: string) => void
  withBottomMargin?: boolean
}) {
  return (
    <button
      className={`${withBottomMargin ? 'mb-5' : ''} min-h-12 self-start rounded-lg border border-[#dfd1bf] bg-[#fffdf9] px-4 py-3 text-base font-bold text-[#5d5148] transition hover:bg-[#fbf7f0]`}
      onClick={() => goBack(navigate)}
      type="button"
    >
      ← 戻る
    </button>
  )
}

function NoteCard({ label, value }: { label: string; value: string }) {
  return (
    <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm">
      <h2 className="text-lg font-bold text-[#2e2822]">{label}</h2>
      <p className="mt-3 whitespace-pre-wrap rounded-lg bg-[#f1e7dc] px-4 py-3 leading-7 text-[#75685e]">
        {value}
      </p>
    </section>
  )
}

function IngredientsPanel({ recipe }: { recipe: RecipeDetail }) {
  const [showMemos, setShowMemos] = useState(false)
  const hasMemos = recipe.ingredients.some((item) => item.memo.trim().length > 0)

  return (
    <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-4 shadow-sm md:p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-2xl font-bold text-[#2e2822]">材料</h2>
        {hasMemos && (
          <button
            aria-expanded={showMemos}
            className="min-h-10 rounded-lg border border-[#dfd1bf] bg-[#fbf7f0] px-3 py-2 text-sm font-bold text-[#6f6258] transition hover:bg-[#f1e7dc]"
            onClick={() => setShowMemos((current) => !current)}
            type="button"
          >
            {showMemos ? '下ごしらえメモを隠す' : '下ごしらえメモを表示'}
          </button>
        )}
      </div>
      {recipe.ingredients.length > 0 ? (
        <div className="mt-4 divide-y divide-[#eadfce] border-y border-[#eadfce]">
          {recipe.ingredients.map((item) => (
            <div className="px-1 py-3.5 md:px-2" key={item.id}>
              <div className="flex items-baseline justify-between gap-4">
                <p className="min-w-0 text-base font-bold text-[#2e2822] md:text-lg">
                  {item.ingredient.name}
                </p>
                <p className="shrink-0 text-base font-bold text-[#6f6258] md:text-lg">
                  {formatQuantity(item.quantity)} {item.unit.name}
                </p>
              </div>
              {showMemos && item.memo && (
                <p className="mt-1.5 text-sm leading-6 text-[#8a7a6d]">{item.memo}</p>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p className="mt-4 rounded-lg bg-[#f1e7dc] px-4 py-5 text-[#75685e]">
          材料はまだ登録されていません。
        </p>
      )}
    </section>
  )
}

function StepsPanel({ recipe }: { recipe: RecipeDetail }) {
  return (
    <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-4 shadow-sm md:p-6">
      <h2 className="text-2xl font-bold text-[#2e2822]">作り方</h2>
      {recipe.steps.length > 0 ? (
        <ol className="mt-5 space-y-4">
          {recipe.steps.map((step) => (
            <li className="flex gap-3 rounded-xl border border-[#eadfce] bg-white p-4 md:gap-4" key={step.id}>
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#78936f] text-base font-bold text-white">
                {step.step_number}
              </span>
              <div className="min-w-0 pt-0.5">
                <p className="whitespace-pre-wrap text-base leading-8 text-[#2e2822] md:text-lg">
                  {step.instruction}
                </p>
                {step.memo && <p className="mt-2 text-sm leading-6 text-[#8a7a6d]">{step.memo}</p>}
              </div>
            </li>
          ))}
        </ol>
      ) : (
        <p className="mt-4 rounded-lg bg-[#f1e7dc] px-4 py-5 text-[#75685e]">
          作り方はまだ登録されていません。
        </p>
      )}
    </section>
  )
}

function AddToPrepPanel({
  navigate,
  onCancel,
  recipe,
}: {
  navigate: (path: string) => void
  onCancel: () => void
  recipe: RecipeDetail
}) {
  const [units, setUnits] = useState<Unit[]>([])
  const [unitsLoading, setUnitsLoading] = useState(true)
  const [unitError, setUnitError] = useState<string | null>(null)
  const [date, setDate] = useState(getTodayDate)
  const [plannedQuantity, setPlannedQuantity] = useState(recipe.base_yield_quantity)
  const [plannedUnitId, setPlannedUnitId] = useState(String(recipe.base_yield_unit.id))
  const [memo, setMemo] = useState('')
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [validationErrors, setValidationErrors] = useState<string[]>([])

  useEffect(() => {
    let active = true

    async function loadUnits() {
      setUnitsLoading(true)
      setUnitError(null)
      try {
        const response = await fetchUnits()
        if (active) {
          setUnits(ensureBaseUnit(response, recipe.base_yield_unit))
        }
      } catch {
        if (active) {
          setUnitError('単位一覧を読み込めませんでした。')
          setUnits([{
            id: recipe.base_yield_unit.id,
            name: recipe.base_yield_unit.name,
            is_active: true,
            unit_type: 'custom',
            is_default: false,
            is_standard: false,
            sort_order: 0,
          }])
        }
      } finally {
        if (active) {
          setUnitsLoading(false)
        }
      }
    }

    void loadUnits()
    return () => {
      active = false
    }
  }, [recipe.base_yield_unit])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const errors = validatePrepForm({ date, plannedQuantity, plannedUnitId, recipeId: recipe.id })
    setValidationErrors(errors)
    setSaveError(null)

    if (errors.length > 0) {
      return
    }

    setSaving(true)
    try {
      await createPrepTask({
        date,
        recipe_id: recipe.id,
        planned_quantity: plannedQuantity,
        planned_unit_id: Number(plannedUnitId),
        memo: memo.trim(),
      })
      navigate('/prep')
    } catch (caught) {
      setSaveError(formatSaveError(caught))
    } finally {
      setSaving(false)
    }
  }

  return (
    <section className="rounded-xl border border-[#d8c3ad] bg-[#fff7eb] p-5 shadow-sm">
      <h2 className="text-xl font-bold text-[#34291f]">今日の仕込みに追加</h2>
      <p className="mt-2 text-sm leading-6 text-[#75685e]">
        基準量を初期値にして、今日の仕込みボードへ追加します。
      </p>

      {unitError && <p className="mt-3 text-sm font-semibold text-[#a23d2d]">{unitError}</p>}

      <form className="mt-4 space-y-4" onSubmit={handleSubmit}>
        <label className="block">
          <span className="text-sm font-semibold text-[#4b4037]">仕込み日 *</span>
          <input
            className="mt-2 min-h-12 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
            onChange={(event) => setDate(event.target.value)}
            type="date"
            value={date}
          />
        </label>

        <label className="block">
          <span className="text-sm font-semibold text-[#4b4037]">予定数量 *</span>
          <input
            className="mt-2 min-h-12 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
            inputMode="decimal"
            onChange={(event) => setPlannedQuantity(event.target.value)}
            value={plannedQuantity}
          />
        </label>

        <label className="block">
          <span className="text-sm font-semibold text-[#4b4037]">予定単位 *</span>
          <select
            className="mt-2 min-h-12 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2 disabled:bg-[#eee7db] disabled:text-[#8a7a6d]"
            disabled={unitsLoading}
            onChange={(event) => setPlannedUnitId(event.target.value)}
            value={plannedUnitId}
          >
            <option value="">選択してください</option>
            {units.map((unit) => (
              <option key={unit.id} value={unit.id}>
                {unit.name}
              </option>
            ))}
          </select>
          {unitsLoading && <span className="mt-2 block text-xs text-[#75685e]">単位を読み込んでいます...</span>}
        </label>

        <label className="block">
          <span className="text-sm font-semibold text-[#4b4037]">メモ</span>
          <textarea
            className="mt-2 min-h-20 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 py-3 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
            onChange={(event) => setMemo(event.target.value)}
            value={memo}
          />
        </label>

        {(validationErrors.length > 0 || saveError) && (
          <div className="rounded-lg border border-[#f1c8c0] bg-[#fff0ed] p-4 text-[#a23d2d]">
            <p className="font-bold">仕込みへの追加に失敗しました。入力内容を確認してください。</p>
            {saveError && <p className="mt-2 text-sm leading-6">{saveError}</p>}
            {validationErrors.length > 0 && (
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">
                {validationErrors.map((error) => (
                  <li key={error}>{error}</li>
                ))}
              </ul>
            )}
          </div>
        )}

        <div className="flex flex-col gap-3 sm:flex-row">
          <button
            className="rounded-lg bg-[#c76738] px-4 py-3 text-base font-bold text-white transition hover:bg-[#b65b31] disabled:cursor-not-allowed disabled:opacity-60"
            disabled={saving || unitsLoading}
            type="submit"
          >
            {saving ? '追加中...' : '仕込みに追加'}
          </button>
          <button
            className="rounded-lg border border-[#dfd1bf] bg-white px-4 py-3 text-base font-bold text-[#5d5148] transition hover:bg-[#fbf7f0]"
            onClick={onCancel}
            type="button"
          >
            キャンセル
          </button>
        </div>
      </form>
    </section>
  )
}

function CostSummaryCard({ recipe }: { recipe: RecipeDetail }) {
  const summary = recipe.cost_summary

  return (
    <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm md:p-6">
      <h2 className="text-2xl font-bold text-[#2e2822]">原価情報</h2>
      <p className="mt-2 text-sm leading-6 text-[#75685e]">基準量あたりの原価サマリーです。</p>
      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <SummaryRow label="材料原価" value={`${formatMoney(summary.material_cost)}円`} />
        <SummaryRow
          label="販売価格"
          value={summary.selling_price === null ? '未設定' : `${formatMoney(summary.selling_price)}円`}
        />
        <SummaryRow label="原価率" value={summary.cost_rate === null ? '-' : `${summary.cost_rate}%`} />
        <SummaryRow
          label="粗利"
          value={summary.gross_profit === null ? '-' : `${formatMoney(summary.gross_profit)}円`}
        />
      </div>
    </section>
  )
}

function SummaryRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-lg bg-[#f1e7dc] px-4 py-3">
      <span className="text-sm font-semibold text-[#75685e]">{label}</span>
      <span className="text-lg font-bold text-[#332820]">{value}</span>
    </div>
  )
}

function ensureBaseUnit(units: Unit[], baseUnit: RecipeDetail['base_yield_unit']) {
  if (units.some((unit) => unit.id === baseUnit.id)) {
    return units
  }
  return [
    {
      id: baseUnit.id,
      name: baseUnit.name,
      is_active: true,
      unit_type: 'custom' as const,
      is_default: false,
      is_standard: false,
      sort_order: 0,
    },
    ...units,
  ]
}

function validatePrepForm({
  date,
  plannedQuantity,
  plannedUnitId,
  recipeId,
}: {
  date: string
  plannedQuantity: string
  plannedUnitId: string
  recipeId: number
}) {
  const errors: string[] = []
  if (!date) {
    errors.push('仕込み日を入力してください。')
  }
  if (!recipeId) {
    errors.push('レシピを選択してください。')
  }
  const quantity = Number(plannedQuantity)
  if (!plannedQuantity || Number.isNaN(quantity)) {
    errors.push('予定数量を入力してください。')
  } else if (quantity <= 0) {
    errors.push('予定数量は0より大きい値を入力してください。')
  }
  if (!plannedUnitId) {
    errors.push('予定単位を選択してください。')
  }
  return errors
}

function getTodayDate() {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatSaveError(caught: unknown) {
  if (caught instanceof ApiError) {
    if (typeof caught.data === 'string') {
      return caught.data
    }
    return JSON.stringify(caught.data)
  }
  return '仕込みへの追加に失敗しました。入力内容を確認してください。'
}

function goBack(navigate: (path: string) => void) {
  if (window.history.length > 1) {
    window.history.back()
    return
  }
  navigate('/recipes')
}

function formatQuantity(value: string) {
  return Number(value).toLocaleString('ja-JP', {
    maximumFractionDigits: 2,
  })
}

function formatMoney(value: string) {
  return Number(value).toLocaleString('ja-JP', {
    maximumFractionDigits: 2,
  })
}

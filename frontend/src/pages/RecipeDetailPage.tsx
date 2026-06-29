import { useEffect, useState, type FormEvent } from 'react'
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
      <button
        className="mb-5 rounded-lg border border-[#dfd1bf] bg-[#fffdf9] px-4 py-3 text-base font-bold text-[#5d5148] transition hover:bg-[#fbf7f0]"
        onClick={() => goBack(navigate)}
        type="button"
      >
        ← 戻る
      </button>

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

  return (
    <>
      <header className="mb-6 rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm md:p-6">
        <p className="text-sm font-bold text-[#78936f]">
          {recipe.category?.name ?? 'カテゴリなし'}
        </p>
        <h1 className="mt-2 text-3xl font-bold tracking-normal text-[#2e2822] md:text-5xl">
          {recipe.name}
        </h1>
        <p className="mt-4 text-xl font-bold text-[#c76738]">
          基準: {formatQuantity(recipe.base_yield_quantity)} {recipe.base_yield_unit.name}
        </p>
        {recipe.description && (
          <p className="mt-4 max-w-3xl text-base leading-8 text-[#75685e]">
            {recipe.description}
          </p>
        )}
        <div className="mt-5 flex flex-col gap-3 sm:flex-row">
          <button
            className="rounded-lg bg-[#c76738] px-5 py-3 text-base font-bold text-white shadow-[0_8px_18px_rgba(198,103,56,0.22)] transition hover:bg-[#b65b31]"
            onClick={() => setShowPrepForm((current) => !current)}
            type="button"
          >
            今日の仕込みに追加
          </button>
          <button
            className="rounded-lg border border-[#dfd1bf] bg-white px-5 py-3 text-base font-bold text-[#5d5148] transition hover:bg-[#fbf7f0]"
            onClick={() => navigate(`/recipes/${recipe.id}/edit`)}
            type="button"
          >
            編集
          </button>
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.35fr)_minmax(320px,0.75fr)]">
        <main className="space-y-5">
          <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm md:p-6">
            <h2 className="text-2xl font-bold text-[#2e2822]">材料</h2>
            <div className="mt-4 space-y-3">
              {recipe.ingredients.length > 0 ? (
                recipe.ingredients.map((item) => (
                  <div
                    className="rounded-lg border border-[#eadfce] bg-white px-4 py-4"
                    key={item.id}
                  >
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-baseline sm:justify-between">
                      <p className="text-xl font-bold text-[#2e2822]">{item.ingredient.name}</p>
                      <p className="text-xl font-bold text-[#6f6258]">
                        {formatQuantity(item.quantity)} {item.unit.name}
                      </p>
                    </div>
                    {item.memo && <p className="mt-2 text-sm text-[#8a7a6d]">{item.memo}</p>}
                  </div>
                ))
              ) : (
                <p className="rounded-lg bg-[#f1e7dc] px-4 py-5 text-[#75685e]">
                  材料はまだ登録されていません。
                </p>
              )}
            </div>
          </section>

          <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm md:p-6">
            <h2 className="text-2xl font-bold text-[#2e2822]">作り方</h2>
            <div className="mt-4 space-y-3">
              {recipe.steps.length > 0 ? (
                recipe.steps.map((step) => (
                  <div className="rounded-lg border border-[#eadfce] bg-[#f1e7dc] p-4" key={step.id}>
                    <p className="text-sm font-bold text-[#75685e]">STEP {step.step_number}</p>
                    <p className="mt-2 rounded-lg bg-white px-4 py-3 text-lg leading-8 text-[#2e2822]">{step.instruction}</p>
                    {step.memo && <p className="mt-2 text-sm text-[#8a7a6d]">{step.memo}</p>}
                  </div>
                ))
              ) : (
                <p className="rounded-lg bg-[#f1e7dc] px-4 py-5 text-[#75685e]">
                  作り方はまだ登録されていません。
                </p>
              )}
            </div>
          </section>
        </main>

        <aside className="space-y-5">
          {showPrepForm && (
            <AddToPrepPanel
              navigate={navigate}
              onCancel={() => setShowPrepForm(false)}
              recipe={recipe}
            />
          )}

          <CostSummaryCard recipe={recipe} />

          <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm">
            <h2 className="text-xl font-bold text-[#2e2822]">注意点</h2>
            <p className="mt-3 rounded-lg bg-[#f1e7dc] px-4 py-4 leading-7 text-[#75685e]">
              {recipe.notes || '特になし'}
            </p>
          </section>

          <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm">
            <h2 className="text-xl font-bold text-[#2e2822]">アレルゲン</h2>
            <p className="mt-3 rounded-lg bg-[#f1e7dc] px-4 py-4 leading-7 text-[#75685e]">
              {recipe.allergen_notes || '未設定'}
            </p>
          </section>
        </aside>
      </div>
    </>
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
    <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm">
      <h2 className="text-xl font-bold text-[#2e2822]">原価情報</h2>
      <div className="mt-4 space-y-3">
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

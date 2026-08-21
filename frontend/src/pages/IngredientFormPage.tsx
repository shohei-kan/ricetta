import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { ApiError } from '../api/api'
import {
  createIngredient,
  fetchIngredientDetail,
  updateIngredient,
  type IngredientCostMode,
  type IngredientDetail,
  type IngredientFormPayload,
  type IngredientType,
} from '../api/ingredients'
import { fetchRecipes, type RecipeListItem } from '../api/recipes'
import { fetchUnits, type Unit } from '../api/units'
import { useAuth } from '../auth/useAuth'
import { AutoResizeTextarea } from '../components/ui/AutoResizeTextarea'
import {
  getFormBackPath,
  hierarchyBackOptions,
  type Navigate,
} from '../navigation'

type IngredientFormPageProps = {
  id?: number
  navigate: Navigate
}

type FormState = {
  name: string
  supplier: string
  memo: string
  ingredient_type: IngredientType
  source_recipe_id: string
  cost_mode: IngredientCostMode
  purchase_quantity: string
  purchase_unit_id: string
  purchase_price: string
  usage_unit_id: string
  conversion_from_quantity: string
  conversion_to_quantity: string
}

const initialFormState: FormState = {
  name: '',
  supplier: '',
  memo: '',
  ingredient_type: 'raw',
  source_recipe_id: '',
  cost_mode: 'none',
  purchase_quantity: '',
  purchase_unit_id: '',
  purchase_price: '',
  usage_unit_id: '',
  conversion_from_quantity: '',
  conversion_to_quantity: '',
}

const costModeOptions: Array<{
  description: string
  label: string
  value: IngredientCostMode
}> = [
  {
    description: '水・飾り・少量調味料など、原価に含めない材料。',
    label: '原価計算しない',
    value: 'none',
  },
  {
    description: '卵1個30円など、仕入単位と使用単位が同じ材料。',
    label: '仕入単位のまま計算',
    value: 'same_unit',
  },
  {
    description: '1缶180円、1缶400gなど、使用単位へ換算する材料。',
    label: '使用単位に換算して計算',
    value: 'conversion',
  },
]

const ingredientTypeOptions: Array<{
  description: string
  label: string
  value: IngredientType
}> = [
  {
    description: '野菜、肉、調味料など、仕入原価を直接入力する材料。',
    label: '通常材料',
    value: 'raw',
  },
  {
    description: 'トマトソースなど、仕込み用レシピを別レシピの材料として使う項目。',
    label: '仕込みレシピ',
    value: 'prep_recipe',
  },
]

export function IngredientFormPage({ id, navigate }: IngredientFormPageProps) {
  const { session } = useAuth()
  const isEdit = id !== undefined
  const [form, setForm] = useState<FormState>(initialFormState)
  const [units, setUnits] = useState<Unit[]>([])
  const [recipes, setRecipes] = useState<RecipeListItem[]>([])
  const [loading, setLoading] = useState(isEdit)
  const [unitsLoading, setUnitsLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [unitError, setUnitError] = useState<string | null>(null)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [validationErrors, setValidationErrors] = useState<string[]>([])

  useEffect(() => {
    let active = true

    async function loadUnits() {
      setUnitsLoading(true)
      setUnitError(null)
      try {
        const [unitResponse, recipeResponse] = await Promise.all([
          fetchUnits(),
          fetchRecipes(),
        ])
        if (active) {
          setUnits(unitResponse)
          setRecipes(recipeResponse)
        }
      } catch {
        if (active) {
          setUnitError('単位一覧を読み込めませんでした。')
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
  }, [])

  useEffect(() => {
    if (!isEdit || id === undefined) {
      return
    }

    let active = true
    const ingredientId = id

    async function loadIngredient() {
      setLoading(true)
      setLoadError(null)
      try {
        const ingredient = await fetchIngredientDetail(ingredientId)
        if (active) {
          setForm(toFormState(ingredient))
        }
      } catch {
        if (active) {
          setLoadError('材料情報を読み込めませんでした。')
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    void loadIngredient()
    return () => {
      active = false
    }
  }, [id, isEdit])

  const selectedPurchaseUnit = useMemo(
    () => units.find((unit) => String(unit.id) === form.purchase_unit_id),
    [form.purchase_unit_id, units],
  )
  const selectedUsageUnit = useMemo(
    () => units.find((unit) => String(unit.id) === form.usage_unit_id),
    [form.usage_unit_id, units],
  )
  const prepRecipes = useMemo(
    () => recipes.filter((recipe) => recipe.recipe_type === 'prep'),
    [recipes],
  )
  const canManageIngredients = session?.membership.role === 'owner'

  function updateForm(updates: Partial<FormState>) {
    setForm((current) => {
      const next = { ...current, ...updates }

      if (updates.ingredient_type === 'raw') {
        next.source_recipe_id = ''
      }

      if (updates.ingredient_type === 'prep_recipe') {
        next.cost_mode = 'none'
        next.purchase_quantity = ''
        next.purchase_unit_id = ''
        next.purchase_price = ''
        next.conversion_from_quantity = ''
        next.conversion_to_quantity = ''
      }

      if (updates.cost_mode === 'none') {
        next.purchase_quantity = ''
        next.purchase_unit_id = ''
        next.purchase_price = ''
        next.usage_unit_id = ''
        next.conversion_from_quantity = ''
        next.conversion_to_quantity = ''
      }

      if (next.cost_mode === 'same_unit') {
        next.usage_unit_id = next.purchase_unit_id
        next.conversion_from_quantity = ''
        next.conversion_to_quantity = ''
      }

      return next
    })
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const errors = validateForm(form)
    setValidationErrors(errors)
    setSaveError(null)

    if (errors.length > 0) {
      return
    }

    setSaving(true)
    try {
      const payload = toPayload(form)
      const saved = isEdit && id !== undefined
        ? await updateIngredient(id, payload)
        : await createIngredient(payload)
      navigate(`/ingredients/${saved.id}`)
    } catch (caught) {
      setSaveError(formatSaveError(caught))
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl px-5 py-6 md:px-7 md:py-8">
        <button
          className="mb-5 rounded-lg border border-[#dfd1bf] bg-[#fffdf9] px-4 py-3 text-base font-bold text-[#5d5148] transition hover:bg-[#fbf7f0]"
          onClick={() => goBack(isEdit, id, navigate)}
          type="button"
        >
          ← 戻る
        </button>
        <div className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-6 text-[#75685e] shadow-sm">
          材料情報を読み込んでいます...
        </div>
      </div>
    )
  }

  if (loadError) {
    return (
      <div className="mx-auto max-w-4xl px-5 py-6 md:px-7 md:py-8">
        <button
          className="mb-5 rounded-lg border border-[#dfd1bf] bg-[#fffdf9] px-4 py-3 text-base font-bold text-[#5d5148]"
          onClick={() => goBack(isEdit, id, navigate)}
          type="button"
        >
          ← 戻る
        </button>
        <div className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-6 text-[#a23d2d] shadow-sm">
          {loadError}
        </div>
      </div>
    )
  }

  if (!canManageIngredients) {
    return (
      <ForbiddenFormPage
        backLabel="← 戻る"
        message="材料の作成・編集はオーナーのみ利用できます。"
        navigate={() => goBack(isEdit, id, navigate)}
      />
    )
  }

  return (
    <div className="mx-auto max-w-260 px-5 py-6 md:px-8 md:py-8">
      <button
        className="mb-5 rounded-lg border border-[#dfd1bf] bg-[#fffdf9] px-4 py-3 text-base font-bold text-[#5d5148] transition hover:bg-[#fbf7f0]"
        onClick={() => goBack(isEdit, id, navigate)}
        type="button"
      >
        ← 戻る
      </button>

      <div className="mb-6 border-b border-[#ded2c2] pb-5">
        <p className="text-sm font-bold text-[#c76738]">
          Ingredient Form
        </p>
        <h1 className="mt-2 text-3xl font-bold tracking-normal text-[#2e2822] md:text-4xl">
          {isEdit ? '材料を編集' : '材料を追加'}
        </h1>
        <p className="mt-2 text-base leading-7 text-[#75685e]">
          原価計算モードに合わせて、必要な仕入・換算情報だけ入力します。
        </p>
      </div>

      <form className="space-y-5" onSubmit={handleSubmit}>
        <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm md:p-6">
          <h2 className="text-2xl font-bold text-[#2e2822]">基本情報</h2>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <TextField
              label="材料名"
              onChange={(value) => updateForm({ name: value })}
              required
              value={form.name}
            />
            <TextField
              label="仕入先"
              onChange={(value) => updateForm({ supplier: value })}
              value={form.supplier}
            />
            <label className="block md:col-span-2">
              <span className="text-sm font-semibold text-[#4b4037]">メモ</span>
              <AutoResizeTextarea
                className="mt-2 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 py-3 text-base leading-7 text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
                onChange={(event) => updateForm({ memo: event.target.value })}
                value={form.memo}
              />
            </label>
          </div>
        </section>

        <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm md:p-6">
          <h2 className="text-2xl font-bold text-[#2e2822]">材料種別</h2>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {ingredientTypeOptions.map((option) => (
              <label
                className={`block rounded-xl border p-4 ${
                  form.ingredient_type === option.value
                    ? 'border-[#c76738] bg-[#f1e7dc]'
                    : 'border-[#eadfce] bg-white'
                }`}
                key={option.value}
              >
                <input
                  checked={form.ingredient_type === option.value}
                  className="sr-only"
                  name="ingredient_type"
                  onChange={() => updateForm({ ingredient_type: option.value })}
                  type="radio"
                />
                <span className="text-base font-bold text-[#332820]">{option.label}</span>
                <span className="mt-2 block text-sm leading-6 text-[#75685e]">
                  {option.description}
                </span>
              </label>
            ))}
          </div>
        </section>

        {form.ingredient_type === 'prep_recipe' && (
          <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm md:p-6">
            <h2 className="text-2xl font-bold text-[#2e2822]">仕込みレシピ</h2>
            {unitError && <p className="mt-3 text-sm font-semibold text-[#a23d2d]">{unitError}</p>}
            <p className="mt-2 text-sm leading-6 text-[#75685e]">
              仕込みレシピの出来上がり量と原価から、使用量に応じた材料原価を計算します。
            </p>
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <RecipeSelectField
                disabled={unitsLoading}
                label="元になる仕込みレシピ"
                onChange={(value) => updateForm({ source_recipe_id: value })}
                recipes={prepRecipes}
                required
                value={form.source_recipe_id}
              />
              <SelectField
                disabled={unitsLoading}
                label="使用単位"
                onChange={(value) => updateForm({ usage_unit_id: value })}
                required
                units={units}
                value={form.usage_unit_id}
              />
            </div>
          </section>
        )}

        {form.ingredient_type === 'raw' && (
          <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm md:p-6">
          <h2 className="text-2xl font-bold text-[#2e2822]">原価計算モード</h2>
          <div className="mt-4 grid gap-3 lg:grid-cols-3">
            {costModeOptions.map((option) => (
              <label
                className={`block rounded-xl border p-4 ${
                  form.cost_mode === option.value
                    ? 'border-[#c76738] bg-[#f1e7dc]'
                    : 'border-[#eadfce] bg-white'
                }`}
                key={option.value}
              >
                <input
                  checked={form.cost_mode === option.value}
                  className="sr-only"
                  name="cost_mode"
                  onChange={() => updateForm({ cost_mode: option.value })}
                  type="radio"
                />
                <span className="text-base font-bold text-[#332820]">{option.label}</span>
                <span className="mt-2 block text-sm leading-6 text-[#75685e]">
                  {option.description}
                </span>
              </label>
            ))}
          </div>
        </section>
        )}

        {form.ingredient_type === 'raw' && form.cost_mode !== 'none' && (
          <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm md:p-6">
            <h2 className="text-2xl font-bold text-[#2e2822]">仕入・使用情報</h2>
            {unitError && <p className="mt-3 text-sm font-semibold text-[#a23d2d]">{unitError}</p>}
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <TextField
                inputMode="decimal"
                label="仕入数量"
                onChange={(value) => updateForm({ purchase_quantity: value })}
                required
                value={form.purchase_quantity}
              />
              <SelectField
                disabled={unitsLoading}
                label="仕入単位"
                onChange={(value) => updateForm({ purchase_unit_id: value })}
                required
                units={units}
                value={form.purchase_unit_id}
              />
              <TextField
                inputMode="decimal"
                label="仕入価格"
                onChange={(value) => updateForm({ purchase_price: value })}
                required
                value={form.purchase_price}
              />
              <SelectField
                disabled={form.cost_mode === 'same_unit' || unitsLoading}
                helpText={
                  form.cost_mode === 'same_unit'
                    ? 'MVPでは仕入単位と同じ単位で固定します。'
                    : undefined
                }
                label="使用単位"
                onChange={(value) => updateForm({ usage_unit_id: value })}
                required
                units={units}
                value={form.usage_unit_id}
              />
            </div>

            {form.cost_mode === 'same_unit' && selectedPurchaseUnit && (
              <p className="mt-4 rounded-lg bg-[#f1e7dc] px-4 py-3 text-sm font-semibold text-[#75685e]">
                使用単位: {selectedPurchaseUnit.name}
              </p>
            )}
          </section>
        )}

        {form.ingredient_type === 'raw' && form.cost_mode === 'conversion' && (
          <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm md:p-6">
            <h2 className="text-2xl font-bold text-[#2e2822]">換算情報</h2>
            <p className="mt-2 text-sm leading-6 text-[#75685e]">
              換算元単位は仕入単位、換算先単位は使用単位に自動で合わせます。
            </p>
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <TextField
                inputMode="decimal"
                label="換算元数量"
                onChange={(value) => updateForm({ conversion_from_quantity: value })}
                required
                value={form.conversion_from_quantity}
              />
              <ReadOnlyField label="換算元単位" value={selectedPurchaseUnit?.name ?? '未選択'} />
              <TextField
                inputMode="decimal"
                label="換算先数量"
                onChange={(value) => updateForm({ conversion_to_quantity: value })}
                required
                value={form.conversion_to_quantity}
              />
              <ReadOnlyField label="換算先単位" value={selectedUsageUnit?.name ?? '未選択'} />
            </div>
          </section>
        )}

        {(validationErrors.length > 0 || saveError) && (
          <div className="rounded-xl border border-[#f1c8c0] bg-[#fff0ed] p-4 text-[#a23d2d]">
            <p className="font-bold">保存に失敗しました。入力内容を確認してください。</p>
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
            className="rounded-lg bg-[#c76738] px-5 py-3 text-base font-bold text-white transition hover:bg-[#b65b31] disabled:cursor-not-allowed disabled:opacity-60"
            disabled={saving || unitsLoading}
            type="submit"
          >
            {saving ? '保存中...' : '保存'}
          </button>
          <button
            className="rounded-lg border border-[#dfd1bf] bg-white px-5 py-3 text-base font-bold text-[#5d5148] transition hover:bg-[#fbf7f0]"
            onClick={() => goBack(isEdit, id, navigate)}
            type="button"
          >
            キャンセル
          </button>
        </div>
      </form>
    </div>
  )
}

function ForbiddenFormPage({
  backLabel,
  message,
  navigate,
}: {
  backLabel: string
  message: string
  navigate: () => void
}) {
  return (
    <div className="mx-auto max-w-4xl px-5 py-6 md:px-7 md:py-8">
      <button
        className="mb-5 rounded-lg border border-[#dfd1bf] bg-[#fffdf9] px-4 py-3 text-base font-bold text-[#5d5148] transition hover:bg-[#fbf7f0]"
        onClick={navigate}
        type="button"
      >
        {backLabel}
      </button>
      <div className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-6 text-[#75685e] shadow-sm">
        {message}
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
  inputMode?: 'decimal'
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

function SelectField({
  disabled,
  helpText,
  label,
  onChange,
  required,
  units,
  value,
}: {
  disabled?: boolean
  helpText?: string
  label: string
  onChange: (value: string) => void
  required?: boolean
  units: Unit[]
  value: string
}) {
  return (
    <label className="block">
      <span className="text-sm font-semibold text-[#4b4037]">
        {label}
        {required ? ' *' : ''}
      </span>
      <select
        className="mt-2 min-h-12 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2 disabled:bg-[#eee7db] disabled:text-[#8a7a6d]"
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        value={value}
      >
        <option value="">選択してください</option>
        {units.map((unit) => (
          <option key={unit.id} value={unit.id}>
            {unit.name}
          </option>
        ))}
      </select>
      {helpText && <span className="mt-2 block text-xs text-[#75685e]">{helpText}</span>}
    </label>
  )
}

function RecipeSelectField({
  disabled,
  label,
  onChange,
  recipes,
  required,
  value,
}: {
  disabled?: boolean
  label: string
  onChange: (value: string) => void
  recipes: RecipeListItem[]
  required?: boolean
  value: string
}) {
  return (
    <label className="block">
      <span className="text-sm font-semibold text-[#4b4037]">
        {label}
        {required ? ' *' : ''}
      </span>
      <select
        className="mt-2 min-h-12 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2 disabled:bg-[#eee7db] disabled:text-[#8a7a6d]"
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        value={value}
      >
        <option value="">選択してください</option>
        {recipes.map((recipe) => (
          <option key={recipe.id} value={recipe.id}>
            {recipe.name}（出来上がり量 {formatQuantity(recipe.base_yield_quantity)} {recipe.base_yield_unit.name}）
          </option>
        ))}
      </select>
    </label>
  )
}

function ReadOnlyField({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-sm font-semibold text-[#4b4037]">{label}</p>
      <p className="mt-2 rounded-lg bg-[#f1e7dc] px-4 py-3 text-base font-bold text-[#332820]">
        {value}
      </p>
    </div>
  )
}

function toFormState(ingredient: IngredientDetail): FormState {
  return {
    name: ingredient.name,
    supplier: ingredient.supplier,
    memo: ingredient.memo,
    ingredient_type: ingredient.ingredient_type,
    source_recipe_id: ingredient.source_recipe ? String(ingredient.source_recipe.id) : '',
    cost_mode: ingredient.cost_mode,
    purchase_quantity: ingredient.purchase_quantity ?? '',
    purchase_unit_id: ingredient.purchase_unit ? String(ingredient.purchase_unit.id) : '',
    purchase_price: ingredient.purchase_price ?? '',
    usage_unit_id: ingredient.usage_unit ? String(ingredient.usage_unit.id) : '',
    conversion_from_quantity: ingredient.conversion?.from_quantity ?? '',
    conversion_to_quantity: ingredient.conversion?.to_quantity ?? '',
  }
}

function toPayload(form: FormState): IngredientFormPayload {
  const base = {
    name: form.name.trim(),
    supplier: form.supplier.trim(),
    memo: form.memo.trim(),
    ingredient_type: form.ingredient_type,
    source_recipe_id: form.ingredient_type === 'prep_recipe'
      ? toNumberOrNull(form.source_recipe_id)
      : null,
    cost_mode: form.cost_mode,
  }

  if (form.ingredient_type === 'prep_recipe') {
    return {
      ...base,
      cost_mode: 'none',
      purchase_quantity: null,
      purchase_unit_id: null,
      purchase_price: null,
      usage_unit_id: toNumberOrNull(form.usage_unit_id),
      conversion_from_quantity: null,
      conversion_from_unit_id: null,
      conversion_to_quantity: null,
      conversion_to_unit_id: null,
    }
  }

  if (form.cost_mode === 'none') {
    return {
      ...base,
      purchase_quantity: null,
      purchase_unit_id: null,
      purchase_price: null,
      usage_unit_id: null,
      conversion_from_quantity: null,
      conversion_from_unit_id: null,
      conversion_to_quantity: null,
      conversion_to_unit_id: null,
    }
  }

  const purchaseUnitId = toNumberOrNull(form.purchase_unit_id)
  const usageUnitId = form.cost_mode === 'same_unit'
    ? purchaseUnitId
    : toNumberOrNull(form.usage_unit_id)

  if (form.cost_mode === 'same_unit') {
    return {
      ...base,
      purchase_quantity: form.purchase_quantity,
      purchase_unit_id: purchaseUnitId,
      purchase_price: form.purchase_price,
      usage_unit_id: usageUnitId,
      conversion_from_quantity: null,
      conversion_from_unit_id: null,
      conversion_to_quantity: null,
      conversion_to_unit_id: null,
    }
  }

  return {
    ...base,
    purchase_quantity: form.purchase_quantity,
    purchase_unit_id: purchaseUnitId,
    purchase_price: form.purchase_price,
    usage_unit_id: usageUnitId,
    conversion_from_quantity: form.conversion_from_quantity,
    conversion_from_unit_id: purchaseUnitId,
    conversion_to_quantity: form.conversion_to_quantity,
    conversion_to_unit_id: usageUnitId,
  }
}

function validateForm(form: FormState) {
  const errors: string[] = []
  if (!form.name.trim()) {
    errors.push('材料名を入力してください。')
  }

  if (form.ingredient_type === 'prep_recipe') {
    if (!form.source_recipe_id) {
      errors.push('元になる仕込みレシピを選択してください。')
    }
    if (!form.usage_unit_id) {
      errors.push('使用単位を選択してください。')
    }
    return errors
  }

  if (form.cost_mode === 'same_unit' || form.cost_mode === 'conversion') {
    validatePositive(form.purchase_quantity, '仕入数量', errors)
    if (!form.purchase_unit_id) {
      errors.push('仕入単位を選択してください。')
    }
    validateNonNegative(form.purchase_price, '仕入価格', errors)
    if (!form.usage_unit_id) {
      errors.push('使用単位を選択してください。')
    }
  }

  if (form.cost_mode === 'conversion') {
    validatePositive(form.conversion_from_quantity, '換算元数量', errors)
    if (!form.purchase_unit_id) {
      errors.push('換算元単位を選択してください。')
    }
    validatePositive(form.conversion_to_quantity, '換算先数量', errors)
    if (!form.usage_unit_id) {
      errors.push('換算先単位を選択してください。')
    }
  }

  return errors
}

function validatePositive(value: string, label: string, errors: string[]) {
  const number = Number(value)
  if (!value || Number.isNaN(number)) {
    errors.push(`${label}を入力してください。`)
  } else if (number <= 0) {
    errors.push(`${label}は0より大きい値を入力してください。`)
  }
}

function validateNonNegative(value: string, label: string, errors: string[]) {
  const number = Number(value)
  if (!value || Number.isNaN(number)) {
    errors.push(`${label}を入力してください。`)
  } else if (number < 0) {
    errors.push(`${label}は0以上の値を入力してください。`)
  }
}

function formatQuantity(value: string) {
  return Number(value).toLocaleString('ja-JP', {
    maximumFractionDigits: 2,
  })
}

function toNumberOrNull(value: string) {
  return value ? Number(value) : null
}

function formatSaveError(caught: unknown) {
  if (caught instanceof ApiError) {
    if (typeof caught.data === 'string') {
      return caught.data
    }
    return JSON.stringify(caught.data)
  }
  return '保存に失敗しました。入力内容を確認してください。'
}

function goBack(isEdit: boolean, id: number | undefined, navigate: Navigate) {
  navigate(
    getFormBackPath('/ingredients', isEdit ? id : undefined),
    hierarchyBackOptions,
  )
}

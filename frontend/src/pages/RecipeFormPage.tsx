import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { ApiError } from '../api/api'
import { fetchCategories, type Category } from '../api/categories'
import { fetchIngredients, type IngredientListItem } from '../api/ingredients'
import {
  createRecipe,
  fetchRecipeDetail,
  updateRecipe,
  type RecipeDetail,
  type RecipeFormPayload,
} from '../api/recipes'
import { fetchUnits, type Unit } from '../api/units'

type RecipeFormPageProps = {
  id?: number
  navigate: (path: string) => void
}

type IngredientRow = {
  ingredient_id: string
  quantity: string
  unit_id: string
  memo: string
}

type StepRow = {
  instruction: string
  memo: string
}

type FormState = {
  name: string
  category_id: string
  description: string
  base_yield_quantity: string
  base_yield_unit_id: string
  selling_price: string
  notes: string
  allergen_notes: string
  ingredients: IngredientRow[]
  steps: StepRow[]
}

const initialFormState: FormState = {
  name: '',
  category_id: '',
  description: '',
  base_yield_quantity: '1',
  base_yield_unit_id: '',
  selling_price: '',
  notes: '',
  allergen_notes: '',
  ingredients: [],
  steps: [],
}

const emptyIngredientRow: IngredientRow = {
  ingredient_id: '',
  quantity: '',
  unit_id: '',
  memo: '',
}

const emptyStepRow: StepRow = {
  instruction: '',
  memo: '',
}

export function RecipeFormPage({ id, navigate }: RecipeFormPageProps) {
  const isEdit = id !== undefined
  const [form, setForm] = useState<FormState>(initialFormState)
  const [categories, setCategories] = useState<Category[]>([])
  const [units, setUnits] = useState<Unit[]>([])
  const [ingredients, setIngredients] = useState<IngredientListItem[]>([])
  const [loading, setLoading] = useState(isEdit)
  const [optionsLoading, setOptionsLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [optionsError, setOptionsError] = useState<string | null>(null)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [validationErrors, setValidationErrors] = useState<string[]>([])

  useEffect(() => {
    let active = true

    async function loadOptions() {
      setOptionsLoading(true)
      setOptionsError(null)
      try {
        const [categoryResponse, unitResponse, ingredientResponse] = await Promise.all([
          fetchCategories(),
          fetchUnits(),
          fetchIngredients(),
        ])
        if (active) {
          setCategories(categoryResponse)
          setUnits(unitResponse)
          setIngredients(ingredientResponse)
        }
      } catch {
        if (active) {
          setOptionsError('選択肢を読み込めませんでした。')
        }
      } finally {
        if (active) {
          setOptionsLoading(false)
        }
      }
    }

    void loadOptions()
    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    if (!isEdit || id === undefined) {
      return
    }

    let active = true
    const recipeId = id

    async function loadRecipe() {
      setLoading(true)
      setLoadError(null)
      try {
        const recipe = await fetchRecipeDetail(recipeId)
        if (active) {
          setForm(toFormState(recipe))
        }
      } catch {
        if (active) {
          setLoadError('レシピを読み込めませんでした。')
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
  }, [id, isEdit])

  const activeIngredients = useMemo(
    () => ingredients.filter((ingredient) => ingredient.name),
    [ingredients],
  )

  function updateForm(updates: Partial<FormState>) {
    setForm((current) => ({ ...current, ...updates }))
  }

  function addIngredientRow() {
    updateForm({ ingredients: [...form.ingredients, { ...emptyIngredientRow }] })
  }

  function updateIngredientRow(index: number, updates: Partial<IngredientRow>) {
    const nextRows = form.ingredients.map((row, rowIndex) => {
      if (rowIndex !== index) {
        return row
      }

      const next = { ...row, ...updates }
      if (updates.ingredient_id !== undefined) {
        const selectedIngredient = ingredients.find(
          (ingredient) => String(ingredient.id) === updates.ingredient_id,
        )
        next.unit_id = selectedIngredient?.usage_unit
          ? String(selectedIngredient.usage_unit.id)
          : next.unit_id
      }
      return next
    })
    updateForm({ ingredients: nextRows })
  }

  function removeIngredientRow(index: number) {
    updateForm({ ingredients: form.ingredients.filter((_, rowIndex) => rowIndex !== index) })
  }

  function addStepRow() {
    updateForm({ steps: [...form.steps, { ...emptyStepRow }] })
  }

  function updateStepRow(index: number, updates: Partial<StepRow>) {
    updateForm({
      steps: form.steps.map((row, rowIndex) => (
        rowIndex === index ? { ...row, ...updates } : row
      )),
    })
  }

  function removeStepRow(index: number) {
    updateForm({ steps: form.steps.filter((_, rowIndex) => rowIndex !== index) })
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
        ? await updateRecipe(id, payload)
        : await createRecipe(payload)
      navigate(`/recipes/${saved.id}`)
    } catch (caught) {
      setSaveError(formatSaveError(caught))
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl px-5 py-6 md:px-7 md:py-8">
        <div className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-6 text-[#75685e] shadow-sm">
          レシピを読み込んでいます...
        </div>
      </div>
    )
  }

  if (loadError) {
    return (
      <div className="mx-auto max-w-4xl px-5 py-6 md:px-7 md:py-8">
        <button
          className="mb-5 rounded-lg bg-[#ebe1d2] px-4 py-3 text-base font-semibold text-[#5d5148]"
          onClick={() => navigate('/recipes')}
          type="button"
        >
          ← レシピ一覧へ
        </button>
        <div className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-6 text-[#a23d2d] shadow-sm">
          {loadError}
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-6xl px-5 py-6 md:px-7 md:py-8">
      <button
        className="mb-5 rounded-lg bg-[#ebe1d2] px-4 py-3 text-base font-semibold text-[#5d5148] transition hover:bg-[#e0d4c4]"
        onClick={() => goBack(isEdit, id, navigate)}
        type="button"
      >
        ← 戻る
      </button>

      <div className="mb-6">
        <p className="text-sm font-semibold tracking-[0.14em] text-[#9b6b43]">RECIPE FORM</p>
        <h1 className="mt-2 text-3xl font-bold tracking-normal text-[#332820] md:text-4xl">
          {isEdit ? 'レシピを編集' : 'レシピを追加'}
        </h1>
        <p className="mt-2 text-base leading-7 text-[#75685e]">
          基本情報、材料、作り方を分けて入力します。材料欄には原価情報を混ぜません。
        </p>
      </div>

      <form className="space-y-5" onSubmit={handleSubmit}>
        <section className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
          <h2 className="text-xl font-bold text-[#34291f]">基本情報</h2>
          {optionsError && (
            <p className="mt-3 text-sm font-semibold text-[#a23d2d]">{optionsError}</p>
          )}
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <TextField
              label="レシピ名"
              onChange={(value) => updateForm({ name: value })}
              required
              value={form.name}
            />
            <SelectField
              disabled={optionsLoading}
              label="カテゴリ"
              onChange={(value) => updateForm({ category_id: value })}
              options={categories.map((category) => ({
                label: category.name,
                value: String(category.id),
              }))}
              placeholder="カテゴリなし"
              value={form.category_id}
            />
            <TextField
              inputMode="decimal"
              label="基準量"
              onChange={(value) => updateForm({ base_yield_quantity: value })}
              required
              value={form.base_yield_quantity}
            />
            <SelectField
              disabled={optionsLoading}
              label="基準単位"
              onChange={(value) => updateForm({ base_yield_unit_id: value })}
              options={units.map((unit) => ({ label: unit.name, value: String(unit.id) }))}
              required
              value={form.base_yield_unit_id}
            />
            <label className="block md:col-span-2">
              <span className="text-sm font-semibold text-[#4b4037]">説明</span>
              <textarea
                className="mt-2 min-h-24 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 py-3 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
                onChange={(event) => updateForm({ description: event.target.value })}
                value={form.description}
              />
            </label>
          </div>
        </section>

        <section className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-xl font-bold text-[#34291f]">材料</h2>
              <p className="mt-1 text-sm leading-6 text-[#75685e]">
                使用する材料、使用量、単位だけを入力します。原価情報は表示しません。
              </p>
            </div>
            <button
              className="rounded-lg bg-[#7b4f2f] px-4 py-3 text-base font-semibold text-white transition hover:bg-[#694225]"
              onClick={addIngredientRow}
              type="button"
            >
              材料行を追加
            </button>
          </div>

          <div className="mt-4 space-y-4">
            {form.ingredients.length === 0 && (
              <p className="rounded-lg bg-[#f4ecdf] px-4 py-5 text-[#75685e]">
                材料行はまだありません。あとから追加して保存できます。
              </p>
            )}
            {form.ingredients.map((row, index) => (
              <div className="rounded-lg border border-[#eadfce] bg-white p-4" key={index}>
                <div className="grid gap-4 lg:grid-cols-[minmax(0,1.3fr)_160px_160px_minmax(0,1fr)]">
                  <SelectField
                    disabled={optionsLoading}
                    label="材料"
                    onChange={(value) => updateIngredientRow(index, { ingredient_id: value })}
                    options={activeIngredients.map((ingredient) => ({
                      label: ingredient.name,
                      value: String(ingredient.id),
                    }))}
                    required
                    value={row.ingredient_id}
                  />
                  <TextField
                    inputMode="decimal"
                    label="使用量"
                    onChange={(value) => updateIngredientRow(index, { quantity: value })}
                    required
                    value={row.quantity}
                  />
                  <SelectField
                    disabled={optionsLoading}
                    label="単位"
                    onChange={(value) => updateIngredientRow(index, { unit_id: value })}
                    options={units.map((unit) => ({ label: unit.name, value: String(unit.id) }))}
                    required
                    value={row.unit_id}
                  />
                  <TextField
                    label="メモ"
                    onChange={(value) => updateIngredientRow(index, { memo: value })}
                    value={row.memo}
                  />
                </div>
                <div className="mt-3 flex justify-end">
                  <button
                    className="rounded-lg bg-[#f1e7dc] px-4 py-2 text-sm font-semibold text-[#7a5a42] transition hover:bg-[#e5d7c8]"
                    onClick={() => removeIngredientRow(index)}
                    type="button"
                  >
                    この材料行を削除
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-xl font-bold text-[#34291f]">作り方</h2>
              <p className="mt-1 text-sm leading-6 text-[#75685e]">
                保存時に表示順で工程番号を振り直します。
              </p>
            </div>
            <button
              className="rounded-lg bg-[#7b4f2f] px-4 py-3 text-base font-semibold text-white transition hover:bg-[#694225]"
              onClick={addStepRow}
              type="button"
            >
              工程を追加
            </button>
          </div>

          <div className="mt-4 space-y-4">
            {form.steps.length === 0 && (
              <p className="rounded-lg bg-[#f4ecdf] px-4 py-5 text-[#75685e]">
                作り方はまだありません。あとから追加して保存できます。
              </p>
            )}
            {form.steps.map((row, index) => (
              <div className="rounded-lg border border-[#eadfce] bg-white p-4" key={index}>
                <p className="text-sm font-semibold text-[#9b6b43]">STEP {index + 1}</p>
                <div className="mt-3 grid gap-4 md:grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)]">
                  <label className="block">
                    <span className="text-sm font-semibold text-[#4b4037]">作り方</span>
                    <textarea
                      className="mt-2 min-h-28 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 py-3 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
                      onChange={(event) => updateStepRow(index, { instruction: event.target.value })}
                      value={row.instruction}
                    />
                  </label>
                  <TextField
                    label="メモ"
                    onChange={(value) => updateStepRow(index, { memo: value })}
                    value={row.memo}
                  />
                </div>
                <div className="mt-3 flex justify-end">
                  <button
                    className="rounded-lg bg-[#f1e7dc] px-4 py-2 text-sm font-semibold text-[#7a5a42] transition hover:bg-[#e5d7c8]"
                    onClick={() => removeStepRow(index)}
                    type="button"
                  >
                    この工程を削除
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
          <h2 className="text-xl font-bold text-[#34291f]">管理情報</h2>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <TextField
              inputMode="decimal"
              label="販売価格"
              onChange={(value) => updateForm({ selling_price: value })}
              value={form.selling_price}
            />
            <TextField
              label="アレルゲンメモ"
              onChange={(value) => updateForm({ allergen_notes: value })}
              value={form.allergen_notes}
            />
            <label className="block md:col-span-2">
              <span className="text-sm font-semibold text-[#4b4037]">注意点</span>
              <textarea
                className="mt-2 min-h-24 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 py-3 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
                onChange={(event) => updateForm({ notes: event.target.value })}
                value={form.notes}
              />
            </label>
          </div>
        </section>

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
            className="rounded-lg bg-[#7b4f2f] px-5 py-3 text-base font-semibold text-white transition hover:bg-[#694225] disabled:cursor-not-allowed disabled:opacity-60"
            disabled={saving || optionsLoading}
            type="submit"
          >
            {saving ? '保存中...' : '保存'}
          </button>
          <button
            className="rounded-lg bg-[#ebe1d2] px-5 py-3 text-base font-semibold text-[#5d5148] transition hover:bg-[#e0d4c4]"
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
  label,
  onChange,
  options,
  placeholder = '選択してください',
  required,
  value,
}: {
  disabled?: boolean
  label: string
  onChange: (value: string) => void
  options: Array<{ label: string; value: string }>
  placeholder?: string
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
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  )
}

function toFormState(recipe: RecipeDetail): FormState {
  return {
    name: recipe.name,
    category_id: recipe.category ? String(recipe.category.id) : '',
    description: recipe.description,
    base_yield_quantity: recipe.base_yield_quantity,
    base_yield_unit_id: String(recipe.base_yield_unit.id),
    selling_price: recipe.selling_price ?? '',
    notes: recipe.notes,
    allergen_notes: recipe.allergen_notes,
    ingredients: recipe.ingredients.map((item) => ({
      ingredient_id: String(item.ingredient.id),
      quantity: item.quantity,
      unit_id: String(item.unit.id),
      memo: item.memo,
    })),
    steps: recipe.steps.map((step) => ({
      instruction: step.instruction,
      memo: step.memo,
    })),
  }
}

function toPayload(form: FormState): RecipeFormPayload {
  const ingredientRows = form.ingredients.filter((row) => !isIngredientRowEmpty(row))
  const stepRows = form.steps.filter((row) => !isStepRowEmpty(row))

  return {
    name: form.name.trim(),
    category_id: toNumberOrNull(form.category_id),
    description: form.description.trim(),
    main_image: null,
    base_yield_quantity: form.base_yield_quantity,
    base_yield_unit_id: Number(form.base_yield_unit_id),
    selling_price: form.selling_price.trim() ? form.selling_price : null,
    notes: form.notes.trim(),
    allergen_notes: form.allergen_notes.trim(),
    ingredients: ingredientRows.map((row, index) => ({
      ingredient_id: Number(row.ingredient_id),
      quantity: row.quantity,
      unit_id: Number(row.unit_id),
      sort_order: index + 1,
      memo: row.memo.trim(),
    })),
    steps: stepRows.map((row, index) => ({
      step_number: index + 1,
      instruction: row.instruction.trim(),
      image: null,
      memo: row.memo.trim(),
    })),
  }
}

function validateForm(form: FormState) {
  const errors: string[] = []
  if (!form.name.trim()) {
    errors.push('レシピ名を入力してください。')
  }
  validatePositive(form.base_yield_quantity, '基準量', errors)
  if (!form.base_yield_unit_id) {
    errors.push('基準単位を選択してください。')
  }
  if (form.selling_price.trim()) {
    validateNonNegative(form.selling_price, '販売価格', errors)
  }

  form.ingredients.forEach((row, index) => {
    if (isIngredientRowEmpty(row)) {
      return
    }
    const label = `材料${index + 1}行目`
    if (!row.ingredient_id) {
      errors.push(`${label}の材料を選択してください。`)
    }
    validatePositive(row.quantity, `${label}の使用量`, errors)
    if (!row.unit_id) {
      errors.push(`${label}の単位を選択してください。`)
    }
  })

  form.steps.forEach((row, index) => {
    if (isStepRowEmpty(row)) {
      return
    }
    if (!row.instruction.trim()) {
      errors.push(`工程${index + 1}の作り方を入力してください。`)
    }
  })

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

function isIngredientRowEmpty(row: IngredientRow) {
  return !row.ingredient_id && !row.quantity.trim() && !row.unit_id && !row.memo.trim()
}

function isStepRowEmpty(row: StepRow) {
  return !row.instruction.trim() && !row.memo.trim()
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

function goBack(isEdit: boolean, id: number | undefined, navigate: (path: string) => void) {
  if (isEdit && id !== undefined) {
    navigate(`/recipes/${id}`)
    return
  }
  navigate('/recipes')
}

import { useEffect, useState } from 'react'
import {
  fetchIngredientDetail,
  type IngredientCostMode,
  type IngredientDetail,
  type IngredientType,
} from '../api/ingredients'
import { useAuth } from '../auth/useAuth'

type IngredientDetailPageProps = {
  id: number
  navigate: (path: string) => void
}

const costModeText: Record<IngredientCostMode, { label: string; description: string }> = {
  none: {
    label: '原価計算しない',
    description: '水・飾り・少量調味料など、原価に含めない材料です。',
  },
  same_unit: {
    label: '仕入単位のまま計算',
    description: '卵1個30円など、仕入単位と使用単位が同じ材料です。',
  },
  conversion: {
    label: '使用単位に換算して計算',
    description: '1缶180円、1缶400gなど、仕入単位から使用単位へ換算する材料です。',
  },
}

const ingredientTypeText: Record<IngredientType, string> = {
  raw: '通常材料',
  prep_recipe: '仕込みレシピ',
}

export function IngredientDetailPage({ id, navigate }: IngredientDetailPageProps) {
  const [ingredient, setIngredient] = useState<IngredientDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    async function loadIngredient() {
      setLoading(true)
      setError(null)
      try {
        const response = await fetchIngredientDetail(id)
        if (active) {
          setIngredient(response)
        }
      } catch {
        if (active) {
          setError('材料情報を読み込めませんでした。一覧に戻って再度お試しください。')
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
          材料情報を読み込んでいます...
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-6 text-[#a23d2d] shadow-sm">
          {error}
        </div>
      )}

      {!loading && !error && ingredient && (
        <IngredientDetailContent ingredient={ingredient} navigate={navigate} />
      )}
    </div>
  )
}

function IngredientDetailContent({
  ingredient,
  navigate,
}: {
  ingredient: IngredientDetail
  navigate: (path: string) => void
}) {
  const { session } = useAuth()
  const mode = costModeText[ingredient.cost_mode]
  const isPrepRecipeIngredient = ingredient.ingredient_type === 'prep_recipe'
  const canManageIngredients = session?.membership.role === 'owner'

  return (
    <>
      <header className="mb-6 rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm md:p-6">
        <p className="text-sm font-bold text-[#c76738]">Ingredient</p>
        <h1 className="mt-2 text-3xl font-bold tracking-normal text-[#2e2822] md:text-4xl">
          {ingredient.name}
        </h1>
        <p className="mt-4 text-xl font-bold text-[#c76738]">
          {isPrepRecipeIngredient
            ? `${ingredient.source_recipe?.name ?? '仕込みレシピ'}由来`
            : ingredient.unit_cost_label ?? '計算なし'}
        </p>
        {canManageIngredients && (
          <button
            className="mt-5 rounded-lg bg-[#c76738] px-5 py-3 text-base font-bold text-white transition hover:bg-[#b65b31]"
            onClick={() => navigate(`/ingredients/${ingredient.id}/edit`)}
            type="button"
          >
            編集
          </button>
        )}
      </header>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(340px,0.9fr)]">
        <main className="space-y-5">
          <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm">
            <h2 className="text-xl font-bold text-[#2e2822]">基本情報</h2>
            <div className="mt-4 space-y-3">
              <InfoRow label="仕入先" value={ingredient.supplier || '未設定'} />
              <InfoRow label="材料種別" value={ingredientTypeText[ingredient.ingredient_type]} />
              {isPrepRecipeIngredient && (
                <InfoRow
                  label="元になる仕込みレシピ"
                  value={ingredient.source_recipe?.name ?? '未設定'}
                />
              )}
              <InfoRow label="メモ" value={ingredient.memo || '未設定'} />
            </div>
          </section>

          <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm">
            <h2 className="text-xl font-bold text-[#2e2822]">原価計算モード</h2>
            <div className="mt-4 rounded-lg bg-[#f1e7dc] px-4 py-4">
              <p className="text-lg font-bold text-[#332820]">
                {isPrepRecipeIngredient ? '仕込みレシピから計算' : mode.label}
              </p>
              <p className="mt-2 leading-7 text-[#75685e]">
                {isPrepRecipeIngredient
                  ? '仕込みレシピの出来上がり量と原価から、使用量に応じた材料原価を計算します。'
                  : mode.description}
              </p>
            </div>
          </section>
        </main>

        <aside className="space-y-5">
          <CostInfo ingredient={ingredient} />
          {ingredient.cost_mode === 'conversion' && <ConversionInfo ingredient={ingredient} />}
        </aside>
      </div>
    </>
  )
}

function CostInfo({ ingredient }: { ingredient: IngredientDetail }) {
  if (ingredient.ingredient_type === 'prep_recipe') {
    return (
      <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm">
        <h2 className="text-xl font-bold text-[#34291f]">原価情報</h2>
        <div className="mt-4 space-y-3">
          <InfoRow label="使用単位" value={ingredient.usage_unit?.name ?? '未設定'} />
          <InfoRow
            label="計算方法"
            value="仕込みレシピの1単位あたり原価から計算"
          />
        </div>
      </section>
    )
  }

  if (ingredient.cost_mode === 'none') {
    return (
      <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm">
        <h2 className="text-xl font-bold text-[#34291f]">原価情報</h2>
        <div className="mt-4 space-y-3">
          <InfoRow label="単価表示" value="計算なし" />
        </div>
      </section>
    )
  }

  return (
    <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm">
      <h2 className="text-xl font-bold text-[#2e2822]">仕入・使用情報</h2>
      <div className="mt-4 space-y-3">
        <InfoRow
          label="仕入数量"
          value={formatQuantityWithUnit(ingredient.purchase_quantity, ingredient.purchase_unit)}
        />
        <InfoRow label="仕入価格" value={formatPrice(ingredient.purchase_price)} />
        <InfoRow label="使用単位" value={ingredient.usage_unit?.name ?? '未設定'} />
        <InfoRow label="単価表示" value={ingredient.unit_cost_label ?? '計算なし'} />
      </div>
    </section>
  )
}

function ConversionInfo({ ingredient }: { ingredient: IngredientDetail }) {
  const conversion = ingredient.conversion

  return (
    <section className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-sm">
      <h2 className="text-xl font-bold text-[#2e2822]">換算情報</h2>
      <div className="mt-4 space-y-3">
        {conversion ? (
          <>
            <InfoRow
              label="換算元"
              value={`${formatQuantity(conversion.from_quantity)} ${conversion.from_unit.name}`}
            />
            <InfoRow
              label="換算先"
              value={`${formatQuantity(conversion.to_quantity)} ${conversion.to_unit.name}`}
            />
          </>
        ) : (
          <InfoRow label="換算情報" value="未設定" />
        )}
      </div>
    </section>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-[#f1e7dc] px-4 py-3">
      <p className="text-sm font-semibold text-[#75685e]">{label}</p>
      <p className="mt-1 text-lg font-bold leading-7 text-[#332820]">{value}</p>
    </div>
  )
}

function goBack(navigate: (path: string) => void) {
  if (window.history.length > 1) {
    window.history.back()
    return
  }
  navigate('/ingredients')
}

function formatQuantityWithUnit(
  quantity: string | null,
  unit: { name: string } | null,
) {
  if (quantity === null || unit === null) {
    return '未設定'
  }
  return `${formatQuantity(quantity)} ${unit.name}`
}

function formatQuantity(value: string) {
  return Number(value).toLocaleString('ja-JP', {
    maximumFractionDigits: 2,
  })
}

function formatPrice(value: string | null) {
  if (value === null) {
    return '未設定'
  }
  return `${Number(value).toLocaleString('ja-JP', {
    maximumFractionDigits: 2,
  })}円`
}

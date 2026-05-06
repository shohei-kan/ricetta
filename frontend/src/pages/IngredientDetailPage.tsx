import { useEffect, useState } from 'react'
import {
  fetchIngredientDetail,
  type IngredientCostMode,
  type IngredientDetail,
} from '../api/ingredients'

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
    <div className="mx-auto max-w-7xl px-5 py-6 md:px-7 md:py-8">
      <button
        className="mb-5 rounded-lg bg-[#ebe1d2] px-4 py-3 text-base font-semibold text-[#5d5148] transition hover:bg-[#e0d4c4]"
        onClick={() => goBack(navigate)}
        type="button"
      >
        ← 戻る
      </button>

      {loading && (
        <div className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-6 text-[#75685e] shadow-sm">
          材料情報を読み込んでいます...
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-6 text-[#a23d2d] shadow-sm">
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
  const mode = costModeText[ingredient.cost_mode]

  return (
    <>
      <header className="mb-6 rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
        <p className="text-sm font-semibold text-[#9b6b43]">INGREDIENT</p>
        <h1 className="mt-2 text-3xl font-bold tracking-normal text-[#332820] md:text-4xl">
          {ingredient.name}
        </h1>
        <p className="mt-4 text-xl font-bold text-[#6f4f36]">
          {ingredient.unit_cost_label ?? '計算なし'}
        </p>
        <button
          className="mt-5 rounded-lg bg-[#7b4f2f] px-5 py-3 text-base font-semibold text-white transition hover:bg-[#694225]"
          onClick={() => navigate(`/ingredients/${ingredient.id}/edit`)}
          type="button"
        >
          編集
        </button>
      </header>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(340px,0.9fr)]">
        <main className="space-y-5">
          <section className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
            <h2 className="text-xl font-bold text-[#34291f]">基本情報</h2>
            <div className="mt-4 space-y-3">
              <InfoRow label="仕入先" value={ingredient.supplier || '未設定'} />
              <InfoRow label="メモ" value={ingredient.memo || '未設定'} />
            </div>
          </section>

          <section className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
            <h2 className="text-xl font-bold text-[#34291f]">原価計算モード</h2>
            <div className="mt-4 rounded-lg bg-[#f4ecdf] px-4 py-4">
              <p className="text-lg font-bold text-[#332820]">{mode.label}</p>
              <p className="mt-2 leading-7 text-[#75685e]">{mode.description}</p>
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
  if (ingredient.cost_mode === 'none') {
    return (
      <section className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
        <h2 className="text-xl font-bold text-[#34291f]">原価情報</h2>
        <div className="mt-4 space-y-3">
          <InfoRow label="単価表示" value="計算なし" />
        </div>
      </section>
    )
  }

  return (
    <section className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
      <h2 className="text-xl font-bold text-[#34291f]">仕入・使用情報</h2>
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
    <section className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
      <h2 className="text-xl font-bold text-[#34291f]">換算情報</h2>
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
    <div className="rounded-lg bg-[#f4ecdf] px-4 py-3">
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

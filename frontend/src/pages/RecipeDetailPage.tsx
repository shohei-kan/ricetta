import { useEffect, useState } from 'react'
import { fetchRecipeDetail, type RecipeDetail } from '../api/recipes'

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
          レシピを読み込んでいます...
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-6 text-[#a23d2d] shadow-sm">
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
  return (
    <>
      <header className="mb-6 rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
        <p className="text-sm font-semibold text-[#9b6b43]">
          {recipe.category?.name ?? 'カテゴリなし'}
        </p>
        <h1 className="mt-2 text-3xl font-bold tracking-normal text-[#332820] md:text-4xl">
          {recipe.name}
        </h1>
        <p className="mt-4 text-xl font-bold text-[#6f4f36]">
          基準: {formatQuantity(recipe.base_yield_quantity)} {recipe.base_yield_unit.name}
        </p>
        {recipe.description && (
          <p className="mt-4 max-w-3xl text-base leading-8 text-[#75685e]">
            {recipe.description}
          </p>
        )}
        <button
          className="mt-5 rounded-lg bg-[#7b4f2f] px-5 py-3 text-base font-semibold text-white transition hover:bg-[#694225]"
          onClick={() => navigate(`/recipes/${recipe.id}/edit`)}
          type="button"
        >
          編集
        </button>
      </header>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1.35fr)_minmax(320px,0.75fr)]">
        <main className="space-y-5">
          <section className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
            <h2 className="text-2xl font-bold text-[#34291f]">材料</h2>
            <div className="mt-4 space-y-3">
              {recipe.ingredients.length > 0 ? (
                recipe.ingredients.map((item) => (
                  <div
                    className="rounded-lg border border-[#eadfce] bg-white px-4 py-4"
                    key={item.id}
                  >
                    <div className="flex flex-col gap-2 sm:flex-row sm:items-baseline sm:justify-between">
                      <p className="text-lg font-bold text-[#332820]">{item.ingredient.name}</p>
                      <p className="text-lg font-semibold text-[#6f6258]">
                        {formatQuantity(item.quantity)} {item.unit.name}
                      </p>
                    </div>
                    {item.memo && <p className="mt-2 text-sm text-[#8a7a6d]">{item.memo}</p>}
                  </div>
                ))
              ) : (
                <p className="rounded-lg bg-[#f4ecdf] px-4 py-5 text-[#75685e]">
                  材料はまだ登録されていません。
                </p>
              )}
            </div>
          </section>

          <section className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
            <h2 className="text-2xl font-bold text-[#34291f]">作り方</h2>
            <div className="mt-4 space-y-3">
              {recipe.steps.length > 0 ? (
                recipe.steps.map((step) => (
                  <div className="rounded-lg border border-[#eadfce] bg-white p-4" key={step.id}>
                    <p className="text-sm font-semibold text-[#9b6b43]">STEP {step.step_number}</p>
                    <p className="mt-2 text-lg leading-8 text-[#332820]">{step.instruction}</p>
                    {step.memo && <p className="mt-2 text-sm text-[#8a7a6d]">{step.memo}</p>}
                  </div>
                ))
              ) : (
                <p className="rounded-lg bg-[#f4ecdf] px-4 py-5 text-[#75685e]">
                  作り方はまだ登録されていません。
                </p>
              )}
            </div>
          </section>
        </main>

        <aside className="space-y-5">
          <CostSummaryCard recipe={recipe} />

          <section className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
            <h2 className="text-xl font-bold text-[#34291f]">注意点</h2>
            <p className="mt-3 rounded-lg bg-[#f4ecdf] px-4 py-4 leading-7 text-[#75685e]">
              {recipe.notes || '特になし'}
            </p>
          </section>

          <section className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
            <h2 className="text-xl font-bold text-[#34291f]">アレルゲン</h2>
            <p className="mt-3 rounded-lg bg-[#f4ecdf] px-4 py-4 leading-7 text-[#75685e]">
              {recipe.allergen_notes || '未設定'}
            </p>
          </section>
        </aside>
      </div>
    </>
  )
}

function CostSummaryCard({ recipe }: { recipe: RecipeDetail }) {
  const summary = recipe.cost_summary

  return (
    <section className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
      <h2 className="text-xl font-bold text-[#34291f]">原価情報</h2>
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
    <div className="flex items-center justify-between rounded-lg bg-[#f4ecdf] px-4 py-3">
      <span className="text-sm font-semibold text-[#75685e]">{label}</span>
      <span className="text-lg font-bold text-[#332820]">{value}</span>
    </div>
  )
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

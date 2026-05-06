import { useEffect, useState, type FormEvent } from 'react'
import {
  fetchIngredients,
  type IngredientCostMode,
  type IngredientListItem,
} from '../api/ingredients'

type IngredientListPageProps = {
  navigate: (path: string) => void
}

const costModeLabels: Record<IngredientCostMode, string> = {
  none: '原価計算しない',
  same_unit: '仕入単位のまま計算',
  conversion: '使用単位に換算して計算',
}

export function IngredientListPage({ navigate }: IngredientListPageProps) {
  const [ingredients, setIngredients] = useState<IngredientListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchInput, setSearchInput] = useState('')
  const [query, setQuery] = useState('')

  useEffect(() => {
    let active = true

    async function loadIngredients() {
      setLoading(true)
      setError(null)
      try {
        const response = await fetchIngredients({ q: query })
        if (active) {
          setIngredients(response)
        }
      } catch {
        if (active) {
          setError('材料一覧を読み込めませんでした。もう一度お試しください。')
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    void loadIngredients()
    return () => {
      active = false
    }
  }, [query])

  function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setQuery(searchInput.trim())
  }

  return (
    <div className="mx-auto max-w-6xl px-5 py-6 md:px-7 md:py-8">
      <div className="mb-6 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm font-semibold tracking-[0.14em] text-[#9b6b43]">INGREDIENTS</p>
          <h1 className="mt-2 text-3xl font-bold tracking-normal text-[#332820] md:text-4xl">
            材料
          </h1>
          <p className="mt-2 text-base leading-7 text-[#75685e]">
            仕入先、原価計算モード、単価を確認する材料マスターです。
          </p>
        </div>
        <button
          className="rounded-lg bg-[#7b4f2f] px-5 py-3 text-base font-semibold text-white transition hover:bg-[#694225]"
          onClick={() => navigate('/ingredients/new')}
          type="button"
        >
          材料を追加
        </button>
      </div>

      <form
        className="mb-5 flex flex-col gap-3 rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-4 shadow-sm sm:flex-row"
        onSubmit={handleSearch}
      >
        <input
          className="min-h-12 flex-1 rounded-lg border border-[#d7cbbb] bg-white px-4 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
          onChange={(event) => setSearchInput(event.target.value)}
          placeholder="ホールトマト、卵、塩..."
          type="search"
          value={searchInput}
        />
        <button
          className="rounded-lg bg-[#7b4f2f] px-5 py-3 text-base font-semibold text-white transition hover:bg-[#694225]"
          type="submit"
        >
          検索
        </button>
      </form>

      {loading && (
        <div className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-6 text-[#75685e] shadow-sm">
          材料を読み込んでいます...
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-6 text-[#a23d2d] shadow-sm">
          {error}
        </div>
      )}

      {!loading && !error && ingredients.length === 0 && (
        <div className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-6 text-[#75685e] shadow-sm">
          <p className="text-lg font-bold text-[#34291f]">材料がまだありません。</p>
          <p className="mt-2">最初の材料を登録しましょう。</p>
        </div>
      )}

      {!loading && !error && ingredients.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {ingredients.map((ingredient) => (
            <IngredientCard
              ingredient={ingredient}
              key={ingredient.id}
              navigate={navigate}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function IngredientCard({
  ingredient,
  navigate,
}: {
  ingredient: IngredientListItem
  navigate: (path: string) => void
}) {
  return (
    <article className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
      <p className="text-sm font-semibold text-[#9b6b43]">
        {costModeLabels[ingredient.cost_mode]}
      </p>
      <h2 className="mt-2 text-2xl font-bold leading-8 text-[#332820]">{ingredient.name}</h2>
      {ingredient.supplier && (
        <p className="mt-2 text-sm font-semibold text-[#75685e]">{ingredient.supplier}</p>
      )}
      <p className="mt-4 rounded-lg bg-[#f4ecdf] px-4 py-3 text-base font-bold text-[#6f4f36]">
        {ingredient.unit_cost_label ?? '計算なし'}
      </p>
      <button
        className="mt-4 w-full rounded-lg bg-[#7b4f2f] px-4 py-3 text-base font-semibold text-white transition hover:bg-[#694225]"
        onClick={() => navigate(`/ingredients/${ingredient.id}`)}
        type="button"
      >
        詳細を見る
      </button>
    </article>
  )
}

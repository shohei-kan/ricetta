import { useEffect, useState, type FormEvent } from 'react'
import { emptyIngredients, emptyRecipeSearch } from '../assets'
import {
  fetchIngredients,
  type IngredientCostMode,
  type IngredientListItem,
} from '../api/ingredients'
import { useAuth } from '../auth/useAuth'
import { EmptyState } from '../components/EmptyState'

type IngredientListPageProps = {
  navigate: (path: string) => void
}

const costModeLabels: Record<IngredientCostMode, string> = {
  none: '原価計算しない',
  same_unit: '仕入単位のまま計算',
  conversion: '使用単位に換算して計算',
}

export function IngredientListPage({ navigate }: IngredientListPageProps) {
  const { session } = useAuth()
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

  const canManageIngredients = session?.membership.role === 'owner'

  return (
    <div className="mx-auto max-w-7xl px-5 py-6 md:px-8 md:py-8">
      <div className="mb-6 flex flex-col gap-4 border-b border-[#ded2c2] pb-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm font-bold text-[#c76738]">Ingredients</p>
          <h1 className="mt-2 text-3xl font-bold tracking-normal text-[#2e2822] md:text-4xl">
            材料一覧
          </h1>
          <p className="mt-2 text-base leading-7 text-[#75685e]">
            仕入先、原価計算モード、単価を確認する材料マスターです。
          </p>
        </div>
        {canManageIngredients && (
          <button
            className="rounded-lg bg-[#c76738] px-5 py-3 text-base font-bold text-white shadow-[0_8px_18px_rgba(198,103,56,0.22)] transition hover:bg-[#b65b31]"
            onClick={() => navigate('/ingredients/new')}
            type="button"
          >
            材料を追加
          </button>
        )}
      </div>

      <form
        className="mb-6 flex flex-col gap-4 rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-4 shadow-sm sm:flex-row"
        onSubmit={handleSearch}
      >
        <input
          className="min-h-14 flex-1 rounded-lg border border-[#d7cbbb] bg-white px-4 text-lg text-[#2b2621] outline-none ring-[#c76738]/30 transition focus:ring-2"
          onChange={(event) => setSearchInput(event.target.value)}
          placeholder="ホールトマト、卵、塩..."
          type="search"
          value={searchInput}
        />
        <button
          className="rounded-lg bg-[#c76738] px-6 py-3 text-base font-bold text-white transition hover:bg-[#b65b31]"
          type="submit"
        >
          検索
        </button>
      </form>

      {loading && (
        <div className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-6 text-[#75685e] shadow-sm">
          材料を読み込んでいます...
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-6 text-[#a23d2d] shadow-sm">
          {error}
        </div>
      )}

      {!loading && !error && ingredients.length === 0 && (
        <div className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-6 text-[#75685e] shadow-sm">
          <EmptyState
            description={query ? '検索条件を変えて、もう一度お試しください。' : '最初の材料を登録しましょう。'}
            imageSrc={query ? emptyRecipeSearch : emptyIngredients}
            title={query ? '該当する材料が見つかりません。' : '材料がまだありません。'}
          />
        </div>
      )}

      {!loading && !error && ingredients.length > 0 && (
        <div className="overflow-hidden rounded-xl border border-[#ded2c2] bg-[#fffdf9] shadow-sm">
          <div className="hidden grid-cols-[1.2fr_1.4fr_1fr_1fr] gap-4 border-b border-[#ded2c2] bg-[#f1e7dc] px-5 py-4 text-base font-bold text-[#2e2822] md:grid">
            <span>材料名</span>
            <span>計算方法</span>
            <span>目安単価</span>
            <span>仕入先</span>
          </div>
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
    <article className="border-b border-[#ded2c2] bg-[#fffdf9] p-5 last:border-b-0 md:grid md:grid-cols-[1.2fr_1.4fr_1fr_1fr] md:items-center md:gap-4">
      <div>
        <h2 className="text-2xl font-bold leading-8 text-[#2e2822]">{ingredient.name}</h2>
        <p className="mt-1 text-sm font-semibold text-[#75685e] md:hidden">
          {ingredient.supplier || '仕入先未設定'}
        </p>
      </div>
      <p className="mt-3 text-base font-bold text-[#6f6258] md:mt-0">
        {costModeLabels[ingredient.cost_mode]}
      </p>
      <p className="mt-3 text-lg font-bold text-[#c76738] md:mt-0">
        {ingredient.unit_cost_label ?? '計算なし'}
      </p>
      <p className="mt-2 hidden text-base font-semibold text-[#75685e] md:block">
        {ingredient.supplier || '未設定'}
      </p>
      <button
        className="mt-4 rounded-lg border border-[#dfd1bf] bg-white px-4 py-3 text-base font-bold text-[#5d5148] transition hover:bg-[#fbf7f0] md:col-span-4 md:w-fit"
        onClick={() => navigate(`/ingredients/${ingredient.id}`)}
        type="button"
      >
        詳細を見る
      </button>
    </article>
  )
}

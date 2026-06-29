import { useEffect, useState, type FormEvent } from 'react'
import { fetchRecipes, type RecipeListItem } from '../api/recipes'
import { emptyRecipeAdd, emptyRecipeSearch, leafSprigSimple } from '../assets'
import { EmptyState } from '../components/EmptyState'

type RecipeListPageProps = {
  navigate: (path: string) => void
}

export function RecipeListPage({ navigate }: RecipeListPageProps) {
  const [recipes, setRecipes] = useState<RecipeListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchInput, setSearchInput] = useState('')
  const [query, setQuery] = useState('')

  useEffect(() => {
    let active = true

    async function loadRecipes() {
      setLoading(true)
      setError(null)
      try {
        const response = await fetchRecipes({ q: query })
        if (active) {
          setRecipes(response)
        }
      } catch {
        if (active) {
          setError('レシピ一覧を読み込めませんでした。もう一度お試しください。')
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    void loadRecipes()
    return () => {
      active = false
    }
  }, [query])

  function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setQuery(searchInput.trim())
  }

  return (
    <div className="mx-auto max-w-7xl px-5 py-6 md:px-8 md:py-8">
      <div className="mb-6 flex flex-col gap-4 border-b border-[#ded2c2] pb-5 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-bold text-[#c76738]">Recipes</p>
          <div className="mt-2 flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-normal text-[#2e2822] md:text-4xl">
              レシピ一覧
            </h1>
            <img
              alt=""
              aria-hidden="true"
              className="pointer-events-none h-10 w-10 select-none object-contain opacity-85 md:h-12 md:w-12"
              src={leafSprigSimple}
            />
          </div>
          <p className="mt-2 text-base leading-7 text-[#75685e]">
            仕込み場で確認するレシピ台帳です。材料と作り方をすぐ開けるようにします。
          </p>
        </div>
        <button
          className="rounded-lg bg-[#c76738] px-5 py-3 text-base font-bold text-white shadow-[0_8px_18px_rgba(198,103,56,0.22)] transition hover:bg-[#b65b31]"
          onClick={() => navigate('/recipes/new')}
          type="button"
        >
          レシピを追加
        </button>
      </div>

      <form
        className="mb-6 flex flex-col gap-4 rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-4 shadow-sm sm:flex-row"
        onSubmit={handleSearch}
      >
        <input
          className="min-h-14 flex-1 rounded-lg border border-[#d7cbbb] bg-white px-4 text-lg text-[#2b2621] outline-none ring-[#c76738]/30 transition focus:ring-2"
          onChange={(event) => setSearchInput(event.target.value)}
          placeholder="トマトソース、プリン..."
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
          レシピを読み込んでいます...
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-6 text-[#a23d2d] shadow-sm">
          {error}
        </div>
      )}

      {!loading && !error && recipes.length === 0 && (
        <div className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-6 text-[#75685e] shadow-sm">
          <EmptyState
            description={query ? '検索条件を変えて、もう一度お試しください。' : '最初のレシピを登録しましょう。'}
            imageSrc={query ? emptyRecipeSearch : emptyRecipeAdd}
            title={query ? '該当するレシピが見つかりません。' : 'レシピがまだありません。'}
          />
        </div>
      )}

      {!loading && !error && recipes.length > 0 && (
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {recipes.map((recipe) => (
            <RecipeCard key={recipe.id} navigate={navigate} recipe={recipe} />
          ))}
        </div>
      )}
    </div>
  )
}

function RecipeCard({
  navigate,
  recipe,
}: {
  navigate: (path: string) => void
  recipe: RecipeListItem
}) {
  return (
    <button
      className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-4 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
      onClick={() => navigate(`/recipes/${recipe.id}`)}
      type="button"
    >
      <div className="mb-4 flex aspect-16/7 items-center justify-center rounded-lg bg-[#eee5d8] text-base font-bold text-[#8a7a6d]">
        写真
      </div>
      <p className="text-sm font-bold text-[#78936f]">
        {recipe.category?.name ?? 'カテゴリなし'}
      </p>
      <h2 className="mt-2 text-2xl font-bold leading-8 text-[#2e2822]">{recipe.name}</h2>
      <p className="mt-3 text-base font-bold text-[#6f6258]">
        基準: {formatQuantity(recipe.base_yield_quantity)} {recipe.base_yield_unit.name}
      </p>
      <p className="mt-2 text-sm text-[#8a7a6d]">更新: {formatDate(recipe.updated_at)}</p>
    </button>
  )
}

function formatQuantity(value: string) {
  return Number(value).toLocaleString('ja-JP', {
    maximumFractionDigits: 2,
  })
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('ja-JP', {
    dateStyle: 'medium',
  }).format(new Date(value))
}

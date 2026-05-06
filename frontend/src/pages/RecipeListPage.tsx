import { useEffect, useState, type FormEvent } from 'react'
import { fetchRecipes, type RecipeListItem } from '../api/recipes'

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
    <div className="mx-auto max-w-6xl px-5 py-6 md:px-7 md:py-8">
      <div className="mb-6">
        <p className="text-sm font-semibold tracking-[0.14em] text-[#9b6b43]">RECIPES</p>
        <h1 className="mt-2 text-3xl font-bold tracking-normal text-[#332820] md:text-4xl">
          レシピ
        </h1>
        <p className="mt-2 text-base leading-7 text-[#75685e]">
          仕込み場で確認するレシピ台帳です。材料と作り方をすぐ開けるようにします。
        </p>
      </div>

      <form
        className="mb-5 flex flex-col gap-3 rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-4 shadow-sm sm:flex-row"
        onSubmit={handleSearch}
      >
        <input
          className="min-h-12 flex-1 rounded-lg border border-[#d7cbbb] bg-white px-4 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
          onChange={(event) => setSearchInput(event.target.value)}
          placeholder="トマトソース、プリン..."
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
          レシピを読み込んでいます...
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-6 text-[#a23d2d] shadow-sm">
          {error}
        </div>
      )}

      {!loading && !error && recipes.length === 0 && (
        <div className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-6 text-[#75685e] shadow-sm">
          <p className="text-lg font-bold text-[#34291f]">レシピがまだありません。</p>
          <p className="mt-2">最初のレシピを登録しましょう。</p>
        </div>
      )}

      {!loading && !error && recipes.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
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
      className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
      onClick={() => navigate(`/recipes/${recipe.id}`)}
      type="button"
    >
      <p className="text-sm font-semibold text-[#9b6b43]">
        {recipe.category?.name ?? 'カテゴリなし'}
      </p>
      <h2 className="mt-2 text-2xl font-bold leading-8 text-[#332820]">{recipe.name}</h2>
      <p className="mt-4 text-base font-semibold text-[#6f6258]">
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

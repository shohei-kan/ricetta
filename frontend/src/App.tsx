import { useEffect, useState } from 'react'
import { AuthProvider } from './auth/AuthContext'
import { useAuth } from './auth/useAuth'
import { AppLayout, type RoutePath } from './components/AppLayout'
import { DashboardPage } from './pages/DashboardPage'
import { LoginPage } from './pages/LoginPage'
import { PlaceholderPage } from './pages/PlaceholderPage'
import { PrepTodayPage } from './pages/PrepTodayPage'
import { RecipeDetailPage } from './pages/RecipeDetailPage'
import { RecipeListPage } from './pages/RecipeListPage'

const protectedPaths: RoutePath[] = [
  '/dashboard',
  '/prep',
  '/recipes',
  '/ingredients',
  '/settings',
]

const placeholderContent: Record<
  Exclude<RoutePath, '/dashboard' | '/prep'>,
  { title: string; description: string }
> = {
  '/recipes': {
    title: 'レシピ',
    description: 'レシピ一覧・詳細・編集画面は次フェーズ以降で実装します。',
  },
  '/ingredients': {
    title: '材料',
    description: '材料一覧・フォーム画面は次フェーズ以降で実装します。',
  },
  '/settings': {
    title: '設定',
    description: '店舗情報、カテゴリ、単位設定は後続フェーズで整えます。',
  },
}

function App() {
  return (
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  )
}

function AppRouter() {
  const [path, setPath] = useState(getCurrentPath)
  const { loading, session } = useAuth()

  useEffect(() => {
    function handlePopState() {
      setPath(getCurrentPath())
    }

    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  function navigate(nextPath: string) {
    if (window.location.pathname !== nextPath) {
      window.history.pushState(null, '', nextPath)
      setPath(getCurrentPath())
    }
  }

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#f7f4ee] text-[#6f6258]">
        読み込み中...
      </main>
    )
  }

  if (path === '/login') {
    if (session) {
      return <RedirectTo navigate={navigate} path="/dashboard" />
    }
    return <LoginPage navigate={navigate} />
  }

  const routePath = toRoutePath(path)
  if (!routePath) {
    return <RedirectTo navigate={navigate} path={session ? '/dashboard' : '/login'} />
  }

  if (!session) {
    return <RedirectTo navigate={navigate} path="/login" />
  }

  return (
    <AppLayout currentPath={routePath} navigate={navigateToRoute(navigate)}>
      {renderRoute(path, routePath, navigate)}
    </AppLayout>
  )
}

function renderRoute(path: string, routePath: RoutePath, navigate: (path: string) => void) {
  if (routePath === '/dashboard') {
    return <DashboardPage navigate={navigate} />
  }

  if (routePath === '/prep') {
    return <PrepTodayPage navigate={navigate} />
  }

  const recipeId = getRecipeId(path)
  if (recipeId !== null) {
    return <RecipeDetailPage id={recipeId} navigate={navigate} />
  }

  if (routePath === '/recipes') {
    return <RecipeListPage navigate={navigate} />
  }

  return (
    <PlaceholderPage
      description={placeholderContent[routePath].description}
      title={placeholderContent[routePath].title}
    />
  )
}

function RedirectTo({
  navigate,
  path,
}: {
  navigate: (path: string) => void
  path: string
}) {
  useEffect(() => {
    navigate(path)
  }, [navigate, path])

  return null
}

function getCurrentPath() {
  return window.location.pathname === '/' ? '/dashboard' : window.location.pathname
}

function toRoutePath(path: string): RoutePath | null {
  if (getRecipeId(path) !== null) {
    return '/recipes'
  }
  return protectedPaths.includes(path as RoutePath) ? (path as RoutePath) : null
}

function getRecipeId(path: string): number | null {
  const match = path.match(/^\/recipes\/(\d+)$/)
  if (!match) {
    return null
  }
  return Number(match[1])
}

function navigateToRoute(navigate: (path: string) => void) {
  return (path: RoutePath) => navigate(path)
}

export default App

import { useEffect, useState } from 'react'
import { AuthProvider } from './auth/AuthContext'
import { useAuth } from './auth/useAuth'
import { AppLayout, type RoutePath } from './components/AppLayout'
import { AccountPage } from './pages/AccountPage'
import { DashboardPage } from './pages/DashboardPage'
import { IngredientDetailPage } from './pages/IngredientDetailPage'
import { IngredientFormPage } from './pages/IngredientFormPage'
import { IngredientListPage } from './pages/IngredientListPage'
import { LoginPage } from './pages/LoginPage'
import { PrepTodayPage } from './pages/PrepTodayPage'
import { RecipeDetailPage } from './pages/RecipeDetailPage'
import { RecipeFormPage } from './pages/RecipeFormPage'
import { RecipeListPage } from './pages/RecipeListPage'
import { SettingsPage } from './pages/SettingsPage'

const protectedPaths: RoutePath[] = [
  '/dashboard',
  '/prep',
  '/recipes',
  '/ingredients',
  '/settings',
  '/account',
]

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
      <main className="flex min-h-screen items-center justify-center bg-[#f7f3ec] text-[#6f6258]">
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
  if (routePath === '/account') {
    return <AccountPage />
  }

  if (routePath === '/dashboard') {
    return <DashboardPage navigate={navigate} />
  }

  if (routePath === '/prep') {
    return <PrepTodayPage navigate={navigate} />
  }

  if (path === '/recipes/new') {
    return <RecipeFormPage key="recipe-new" navigate={navigate} />
  }

  const recipeEditId = getRecipeEditId(path)
  if (recipeEditId !== null) {
    return <RecipeFormPage id={recipeEditId} key={`recipe-edit-${recipeEditId}`} navigate={navigate} />
  }

  const recipeId = getRecipeId(path)
  if (recipeId !== null) {
    return <RecipeDetailPage id={recipeId} navigate={navigate} />
  }

  if (routePath === '/recipes') {
    return <RecipeListPage navigate={navigate} />
  }

  if (path === '/ingredients/new') {
    return <IngredientFormPage navigate={navigate} />
  }

  const ingredientEditId = getIngredientEditId(path)
  if (ingredientEditId !== null) {
    return <IngredientFormPage id={ingredientEditId} navigate={navigate} />
  }

  const ingredientId = getIngredientId(path)
  if (ingredientId !== null) {
    return <IngredientDetailPage id={ingredientId} navigate={navigate} />
  }

  if (routePath === '/ingredients') {
    return <IngredientListPage navigate={navigate} />
  }

  return <SettingsPage />
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
  if (path === '/recipes/new' || getRecipeEditId(path) !== null) {
    return '/recipes'
  }
  if (getRecipeId(path) !== null) {
    return '/recipes'
  }
  if (getIngredientId(path) !== null) {
    return '/ingredients'
  }
  if (path === '/ingredients/new' || getIngredientEditId(path) !== null) {
    return '/ingredients'
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

function getRecipeEditId(path: string): number | null {
  const match = path.match(/^\/recipes\/(\d+)\/edit$/)
  if (!match) {
    return null
  }
  return Number(match[1])
}

function getIngredientId(path: string): number | null {
  const match = path.match(/^\/ingredients\/(\d+)$/)
  if (!match) {
    return null
  }
  return Number(match[1])
}

function getIngredientEditId(path: string): number | null {
  const match = path.match(/^\/ingredients\/(\d+)\/edit$/)
  if (!match) {
    return null
  }
  return Number(match[1])
}

function navigateToRoute(navigate: (path: string) => void) {
  return (path: RoutePath) => navigate(path)
}

export default App

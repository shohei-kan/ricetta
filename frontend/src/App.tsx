import { useEffect, useState } from 'react'
import { AuthProvider } from './auth/AuthContext'
import { useAuth } from './auth/useAuth'
import { AppLayout, type RoutePath } from './components/AppLayout'
import { DashboardPage } from './pages/DashboardPage'
import { LoginPage } from './pages/LoginPage'
import { PlaceholderPage } from './pages/PlaceholderPage'

const protectedPaths: RoutePath[] = [
  '/dashboard',
  '/prep',
  '/recipes',
  '/ingredients',
  '/settings',
]

const placeholderContent: Record<RoutePath, { title: string; description: string }> = {
  '/dashboard': {
    title: '今日の現場',
    description: '',
  },
  '/prep': {
    title: '今日の仕込み',
    description: 'PrepTask APIと接続する画面は次フェーズで実装します。',
  },
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
      {routePath === '/dashboard' ? (
        <DashboardPage navigate={navigate} />
      ) : (
        <PlaceholderPage
          description={placeholderContent[routePath].description}
          title={placeholderContent[routePath].title}
        />
      )}
    </AppLayout>
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
  return protectedPaths.includes(path as RoutePath) ? (path as RoutePath) : null
}

function navigateToRoute(navigate: (path: string) => void) {
  return (path: RoutePath) => navigate(path)
}

export default App

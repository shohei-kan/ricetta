import type { ReactNode } from 'react'
import { useAuth } from '../auth/useAuth'

export type RoutePath = '/dashboard' | '/prep' | '/recipes' | '/ingredients' | '/settings'

const navItems: Array<{ path: RoutePath; label: string }> = [
  { path: '/dashboard', label: 'ホーム' },
  { path: '/prep', label: '仕込み' },
  { path: '/recipes', label: 'レシピ' },
  { path: '/ingredients', label: '材料' },
  { path: '/settings', label: '設定' },
]

type AppLayoutProps = {
  children: ReactNode
  currentPath: RoutePath
  navigate: (path: RoutePath) => void
}

export function AppLayout({ children, currentPath, navigate }: AppLayoutProps) {
  const { logout, session } = useAuth()

  return (
    <div className="min-h-screen bg-[#f7f4ee] text-[#2b2621]">
      <aside className="fixed left-0 top-0 hidden h-screen w-[120px] border-r border-[#e5ddcf] bg-[#fffaf2] px-3 py-4 md:flex md:flex-col">
        <button
          className="mb-5 rounded-lg px-2 py-3 text-left text-xl font-semibold text-[#382c22]"
          onClick={() => navigate('/dashboard')}
          type="button"
        >
          Ricetta
        </button>
        <nav className="flex flex-1 flex-col gap-2">
          {navItems.map((item) => (
            <button
              className={`rounded-lg px-3 py-3 text-left text-base font-medium transition ${
                currentPath === item.path
                  ? 'bg-[#eadfce] text-[#2f241c] shadow-sm'
                  : 'text-[#70665c] hover:bg-[#f1e9dd]'
              }`}
              key={item.path}
              onClick={() => navigate(item.path)}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </nav>
        <div className="rounded-lg bg-[#f3eadc] px-3 py-3 text-left">
          <p className="text-sm font-semibold text-[#3d3228]">{session?.shop.name}</p>
          <p className="mt-1 text-xs text-[#817569]">{session?.membership.role}</p>
        </div>
        <button
          className="mt-3 rounded-lg px-3 py-2 text-left text-sm text-[#817569] hover:bg-[#f1e9dd]"
          onClick={() => void logout()}
          type="button"
        >
          ログアウト
        </button>
      </aside>

      <main className="min-h-screen pb-24 md:ml-[120px] md:pb-0">
        <header className="sticky top-0 z-10 border-b border-[#e6ded3] bg-[#f7f4ee]/95 px-5 py-4 backdrop-blur md:hidden">
          <div className="flex items-center justify-between">
            <button
              className="text-xl font-semibold text-[#382c22]"
              onClick={() => navigate('/dashboard')}
              type="button"
            >
              Ricetta
            </button>
            <button
              className="rounded-lg bg-[#ebe1d2] px-3 py-2 text-sm font-medium text-[#5d5148]"
              onClick={() => navigate('/settings')}
              type="button"
            >
              設定
            </button>
          </div>
        </header>
        {children}
      </main>

      <nav className="fixed bottom-0 left-0 right-0 z-20 grid grid-cols-4 gap-2 border-t border-[#e2d8ca] bg-[#fffaf2] px-3 py-3 md:hidden">
        {navItems.slice(0, 4).map((item) => (
          <button
            className={`rounded-lg px-2 py-3 text-sm font-semibold ${
              currentPath === item.path
                ? 'bg-[#eadfce] text-[#2f241c]'
                : 'text-[#70665c]'
            }`}
            key={item.path}
            onClick={() => navigate(item.path)}
            type="button"
          >
            {item.label}
          </button>
        ))}
      </nav>
    </div>
  )
}

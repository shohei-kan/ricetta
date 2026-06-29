import type { ReactNode } from 'react'
import { ricettaLogoSimple } from '../assets'
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
    <div className="min-h-screen bg-[#f7f3ec] text-[#2a241f] md:flex">
      <aside className="sticky top-0 hidden h-screen w-30 shrink-0 border-r border-[#ded2c2] bg-[#fffdf9] md:flex md:flex-col">
        <button
          className="flex min-h-24 items-center justify-center border-b border-[#ded2c2] py-5"
          onClick={() => navigate('/dashboard')}
          type="button"
        >
          <span className="flex w-29.5 justify-center overflow-hidden">
            <img alt="Ricetta" className="h-auto w-37 max-w-none" src={ricettaLogoSimple} />
          </span>
        </button>
        <nav className="flex flex-1 flex-col gap-5 px-3 py-7">
          {navItems.map((item) => (
            <button
              className={`rounded-xl border px-3 py-4 text-center text-lg font-bold transition ${
                currentPath === item.path
                  ? 'border-[#d9a98e] bg-[#f1e7dc] text-[#c76738] shadow-[0_8px_20px_rgba(84,58,35,0.06)]'
                  : 'border-transparent text-[#2d2823] hover:border-[#eadfce] hover:bg-[#fbf7f0]'
              }`}
              key={item.path}
              onClick={() => navigate(item.path)}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </nav>
        <div className="border-t border-[#ded2c2] px-4 py-5 text-left">
          <p className="truncate text-base font-bold text-[#2e2822]">{session?.shop.name}</p>
          <p className="mt-3 inline-flex rounded-md bg-[#78936f] px-3 py-1 text-sm font-bold text-white">
            {session?.membership.role}
          </p>
        </div>
        <button
          className="mx-3 mb-4 whitespace-nowrap rounded-lg px-1.5 py-2 text-center text-[13px] font-semibold break-keep text-[#776b60] hover:bg-[#f1e9dd]"
          onClick={() => void logout()}
          type="button"
        >
          ログアウト
        </button>
      </aside>

      <main className="min-h-screen min-w-0 flex-1 bg-[#f7f3ec] pb-24 md:pb-0">
        <header className="sticky top-0 z-10 border-b border-[#ded2c2] bg-[#fffdf9]/95 px-5 py-4 backdrop-blur md:hidden">
          <div className="flex items-center justify-between">
            <button
              className="flex min-h-10 items-center"
              onClick={() => navigate('/dashboard')}
              type="button"
            >
              <img alt="Ricetta" className="h-auto w-28" src={ricettaLogoSimple} />
            </button>
            <button
              className="rounded-lg border border-[#dfd1bf] bg-[#fbf7f0] px-4 py-2 text-sm font-bold text-[#5d5148]"
              onClick={() => navigate('/settings')}
              type="button"
            >
              設定
            </button>
          </div>
        </header>
        {children}
      </main>

      <nav className="fixed bottom-0 left-0 right-0 z-20 grid grid-cols-4 gap-2 border-t border-[#ded2c2] bg-[#fffdf9] px-3 pb-[calc(0.75rem+env(safe-area-inset-bottom))] pt-3 shadow-[0_-10px_30px_rgba(84,58,35,0.08)] md:hidden">
        {navItems.slice(0, 4).map((item) => (
          <button
            className={`min-h-14 rounded-xl border px-2 py-3 text-sm font-bold ${
              currentPath === item.path
                ? 'border-[#d9a98e] bg-[#f1e7dc] text-[#c76738]'
                : 'border-transparent text-[#5f554b]'
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

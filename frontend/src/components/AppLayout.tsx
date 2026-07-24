import type { ReactNode } from 'react'
import {
  BookOpen,
  CircleUserRound,
  ClipboardList,
  Home,
  Package,
  Settings,
  type LucideIcon,
} from 'lucide-react'
import { ricettaLogoSimple } from '../assets'
import { DemoBanner } from './demo/DemoBanner'

export type RoutePath = '/dashboard' | '/prep' | '/recipes' | '/ingredients' | '/settings' | '/account'

const navItems: Array<{ path: RoutePath; label: string; icon: LucideIcon }> = [
  { path: '/dashboard', label: 'ホーム', icon: Home },
  { path: '/prep', label: '仕込み', icon: ClipboardList },
  { path: '/recipes', label: 'レシピ', icon: BookOpen },
  { path: '/ingredients', label: '材料', icon: Package },
  { path: '/settings', label: '設定', icon: Settings },
]

type AppLayoutProps = {
  children: ReactNode
  currentPath: RoutePath
  pathname: string
  navigate: (path: RoutePath) => void
}

const mobileBottomNavPaths = new Set([
  '/dashboard',
  '/prep',
  '/recipes',
  '/ingredients',
  '/settings',
  '/account',
])

export function AppLayout({ children, currentPath, pathname, navigate }: AppLayoutProps) {
  const showMobileBottomNav = mobileBottomNavPaths.has(pathname)

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
          {navItems.map(({ icon: Icon, label, path }) => (
            <button
              className={`flex min-h-17 flex-col items-center justify-center gap-1.5 rounded-xl border px-2 py-3 text-center text-base font-bold transition ${
                currentPath === path
                  ? 'border-[#d9a98e] bg-[#f1e7dc] text-[#c76738] shadow-[0_8px_20px_rgba(84,58,35,0.06)]'
                  : 'border-transparent text-[#2d2823] hover:border-[#eadfce] hover:bg-[#fbf7f0]'
              }`}
              key={path}
              onClick={() => navigate(path)}
              type="button"
            >
              <Icon aria-hidden="true" size={21} strokeWidth={1.7} />
              <span>{label}</span>
            </button>
          ))}
        </nav>
        <button
          className={`flex min-h-20 w-full flex-col items-center justify-center gap-2 border-t border-[#ded2c2] px-3 py-4 text-center text-[#5d5148] transition hover:bg-[#f7f1e8] hover:text-[#c76738] ${
            currentPath === '/account' ? 'bg-[#f1e7dc]' : ''
          }`}
          onClick={() => navigate('/account')}
          type="button"
        >
          <CircleUserRound aria-hidden="true" size={22} strokeWidth={1.7} />
          <span className="text-sm font-bold">アカウント</span>
        </button>
      </aside>

      <main className={`min-h-screen min-w-0 flex-1 bg-[#f7f3ec] md:pb-0 ${showMobileBottomNav ? 'pb-20' : ''}`}>
        <DemoBanner />
        <header className="border-b border-[#ded2c2] bg-[#fffdf9] px-5 py-4 md:hidden">
          <div className="flex items-center justify-between">
            <button
              className="flex min-h-10 items-center"
              onClick={() => navigate('/dashboard')}
              type="button"
            >
              <img alt="Ricetta" className="h-auto w-28" src={ricettaLogoSimple} />
            </button>
            <button
              aria-label="アカウント"
              className="flex min-h-11 min-w-11 items-center justify-center rounded-full text-[#5d5148] transition hover:text-[#c76738]"
              onClick={() => navigate('/account')}
              type="button"
            >
              <CircleUserRound aria-hidden="true" size={23} strokeWidth={1.8} />
            </button>
          </div>
        </header>
        {children}
      </main>

      {showMobileBottomNav && (
        <nav className="fixed bottom-0 left-0 right-0 z-20 grid grid-cols-5 gap-1 border-t border-[#ded2c2] bg-[#fffdf9] px-2 pb-[calc(0.5rem+env(safe-area-inset-bottom))] pt-2 shadow-[0_-10px_30px_rgba(84,58,35,0.08)] md:hidden">
          {navItems.map(({ icon: Icon, label, path }) => (
            <button
              aria-label={label}
              className={`flex min-h-14 flex-col items-center justify-center gap-1 rounded-xl border px-1 py-2 font-bold transition ${
                currentPath === path
                  ? 'border-[#d9a98e] bg-[#f1e7dc] text-[#c76738]'
                  : 'border-transparent text-[#5f554b]'
              }`}
              key={path}
              onClick={() => navigate(path)}
              type="button"
            >
              <Icon aria-hidden="true" size={22} strokeWidth={1.8} />
              <span className="text-[11px] leading-none">{label}</span>
            </button>
          ))}
        </nav>
      )}
    </div>
  )
}

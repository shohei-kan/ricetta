import { useEffect, useState, type ReactNode } from 'react'
import {
  fetchDashboard,
  type DashboardData,
  type DashboardTask,
  type StatusKey,
} from '../api/dashboard'

type DashboardPageProps = {
  navigate: (path: string) => void
}

const statusLabels: Record<StatusKey, string> = {
  todo: '未着手',
  doing: '作業中',
  done: '完了',
}

export function DashboardPage({ navigate }: DashboardPageProps) {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    async function loadDashboard() {
      setLoading(true)
      setError(null)
      try {
        const data = await fetchDashboard()
        if (active) {
          setDashboard(data)
        }
      } catch {
        if (active) {
          setError('Dashboardを読み込めませんでした。')
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    void loadDashboard()
    return () => {
      active = false
    }
  }, [])

  if (loading) {
    return <PageShell title="今日の現場">読み込み中...</PageShell>
  }

  if (error || !dashboard) {
    return <PageShell title="今日の現場">{error ?? 'データがありません。'}</PageShell>
  }

  return (
    <PageShell title="今日の現場" subtitle={formatDate(dashboard.date)}>
      <div className="grid gap-5 lg:grid-cols-[minmax(0,1.45fr)_minmax(320px,0.9fr)]">
        <section className="space-y-5">
          <div className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-xl font-bold text-[#34291f]">今日の仕込み</h2>
                <p className="mt-1 text-sm text-[#75685e]">ホワイトボード代わりの進捗確認</p>
              </div>
              <button
                className="rounded-lg bg-[#7b4f2f] px-4 py-3 text-base font-semibold text-white"
                onClick={() => navigate('/prep')}
                type="button"
              >
                今日の仕込みを見る
              </button>
            </div>

            <div className="mt-5 grid grid-cols-3 gap-3">
              {(['todo', 'doing', 'done'] as StatusKey[]).map((status) => (
                <div className="rounded-lg bg-[#f4ecdf] p-4 text-center" key={status}>
                  <p className="text-sm font-semibold text-[#75685e]">{statusLabels[status]}</p>
                  <p className="mt-2 text-3xl font-bold text-[#332820]">
                    {dashboard.prep_summary[status]}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
            <h2 className="text-xl font-bold text-[#34291f]">次にやること</h2>
            <div className="mt-4 space-y-3">
              {dashboard.next_tasks.length > 0 ? (
                dashboard.next_tasks.map((task) => <TaskCard key={task.id} task={task} />)
              ) : (
                <p className="rounded-lg bg-[#f4ecdf] px-4 py-5 text-[#75685e]">
                  今日の未完了の仕込みはありません。
                </p>
              )}
            </div>
          </div>
        </section>

        <aside className="space-y-5">
          <div className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
            <h2 className="text-xl font-bold text-[#34291f]">よく使うレシピ</h2>
            <div className="mt-4 space-y-2">
              {dashboard.frequent_recipes.length > 0 ? (
                dashboard.frequent_recipes.map((recipe) => (
                  <div
                    className="rounded-lg bg-[#f4ecdf] px-4 py-3"
                    key={recipe.id}
                  >
                    <p className="font-semibold text-[#3c3027]">{recipe.name}</p>
                    <p className="mt-1 text-sm text-[#7b6f64]">
                      {recipe.category?.name ?? 'カテゴリなし'}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-[#75685e]">まだ表示できるレシピがありません。</p>
              )}
            </div>
          </div>

          <div className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
            <h2 className="text-xl font-bold text-[#34291f]">ミニサマリー</h2>
            <div className="mt-4 grid grid-cols-3 gap-2">
              <Stat label="レシピ" value={dashboard.stats.recipe_count} />
              <Stat label="材料" value={dashboard.stats.ingredient_count} />
              <Stat label="仕込み" value={dashboard.stats.prep_task_count} />
            </div>
          </div>

          <div className="rounded-xl border border-[#e3d8c9] bg-[#fffaf2] p-5 shadow-sm">
            <h2 className="text-xl font-bold text-[#34291f]">期限注意</h2>
            <p className="mt-4 rounded-lg bg-[#f4ecdf] px-4 py-4 text-[#75685e]">
              {dashboard.alerts.length === 0
                ? '現在注意はありません。'
                : `${dashboard.alerts.length}件の注意があります。`}
            </p>
          </div>
        </aside>
      </div>
    </PageShell>
  )
}

function PageShell({
  children,
  subtitle,
  title,
}: {
  children: ReactNode
  subtitle?: string
  title: string
}) {
  return (
    <div className="mx-auto max-w-6xl px-5 py-6 md:px-7 md:py-8">
      <div className="mb-6">
        <p className="text-sm font-semibold tracking-[0.14em] text-[#9b6b43]">RICETTA</p>
        <h1 className="mt-2 text-3xl font-bold tracking-normal text-[#332820] md:text-4xl">
          {title}
        </h1>
        {subtitle && <p className="mt-2 text-base text-[#75685e]">{subtitle}</p>}
      </div>
      {children}
    </div>
  )
}

function TaskCard({ task }: { task: DashboardTask }) {
  return (
    <div className="rounded-lg border border-[#eadfce] bg-white px-4 py-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-lg font-bold text-[#332820]">{task.recipe.name}</p>
          <p className="mt-1 text-[#75685e]">
            {formatQuantity(task.planned_quantity)}
            {task.planned_unit.name}
          </p>
          {task.memo && <p className="mt-2 text-sm text-[#8a7a6d]">{task.memo}</p>}
        </div>
        <span className="rounded-full bg-[#f0e5d5] px-3 py-1 text-sm font-semibold text-[#6d5038]">
          {statusLabels[task.status]}
        </span>
      </div>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg bg-[#f4ecdf] px-3 py-4 text-center">
      <p className="text-2xl font-bold text-[#332820]">{value}</p>
      <p className="mt-1 text-sm font-semibold text-[#75685e]">{label}</p>
    </div>
  )
}

function formatQuantity(value: string) {
  return Number(value).toLocaleString('ja-JP', {
    maximumFractionDigits: 2,
  })
}

function formatDate(date: string) {
  return new Intl.DateTimeFormat('ja-JP', {
    dateStyle: 'full',
  }).format(new Date(`${date}T00:00:00`))
}

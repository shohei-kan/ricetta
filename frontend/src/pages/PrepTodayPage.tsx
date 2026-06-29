import { useCallback, useEffect, useMemo, useState } from 'react'
import { emptyPrepBoard } from '../assets'
import {
  fetchPrepTasks,
  updatePrepTaskStatus,
  type PrepTask,
  type PrepTaskListResponse,
  type PrepTaskStatus,
} from '../api/prepTasks'
import { EmptyState as EmptyStateContent } from '../components/EmptyState'

const statusLabels: Record<PrepTaskStatus, string> = {
  todo: '未着手',
  doing: '作業中',
  done: '完了',
}

const statusOrder: PrepTaskStatus[] = ['todo', 'doing', 'done']

type PrepTodayPageProps = {
  navigate: (path: string) => void
}

export function PrepTodayPage({ navigate }: PrepTodayPageProps) {
  const [data, setData] = useState<PrepTaskListResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [statusError, setStatusError] = useState<string | null>(null)
  const [updatingTaskId, setUpdatingTaskId] = useState<number | null>(null)
  const today = useMemo(() => getToday(), [])

  const loadPrepTasks = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetchPrepTasks(today)
      setData(response)
    } catch {
      setError('仕込み一覧を読み込めませんでした。もう一度お試しください。')
    } finally {
      setLoading(false)
    }
  }, [today])

  useEffect(() => {
    let active = true

    async function load() {
      setLoading(true)
      setError(null)
      try {
        const response = await fetchPrepTasks(today)
        if (active) {
          setData(response)
        }
      } catch {
        if (active) {
          setError('仕込み一覧を読み込めませんでした。もう一度お試しください。')
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    void load()
    return () => {
      active = false
    }
  }, [today])

  async function handleStatusChange(taskId: number, status: PrepTaskStatus) {
    setUpdatingTaskId(taskId)
    setStatusError(null)
    try {
      await updatePrepTaskStatus(taskId, status)
      await loadPrepTasks()
    } catch {
      setStatusError('ステータスを更新できませんでした。もう一度お試しください。')
    } finally {
      setUpdatingTaskId(null)
    }
  }

  const tasksByStatus = groupTasksByStatus(data?.tasks ?? [])
  const isEmpty = !loading && !error && (data?.tasks.length ?? 0) === 0

  return (
    <div className="mx-auto max-w-7xl px-5 py-6 md:px-8 md:py-8">
      <div className="mb-6 flex flex-col gap-4 border-b border-[#ded2c2] pb-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm font-bold text-[#c76738]">Prep Today</p>
          <h1 className="mt-2 text-3xl font-bold tracking-normal text-[#2e2822] md:text-4xl">
            今日の仕込み
          </h1>
          <p className="mt-2 text-base text-[#75685e]">{formatDate(data?.date ?? today)}</p>
        </div>

        {data && (
          <div className="grid grid-cols-3 gap-2 rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-3 shadow-sm">
            {statusOrder.map((status) => (
              <div className={`min-w-22 rounded-lg border px-3 py-3 text-center ${columnTone(status)}`} key={status}>
                <p className="text-sm font-bold">{statusLabels[status]}</p>
                <p className="mt-1 text-2xl font-bold">{data.summary[status]}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {statusError && (
        <p className="mb-4 rounded-lg bg-[#fff0ed] px-4 py-3 text-sm font-semibold text-[#a23d2d]">
          {statusError}
        </p>
      )}

      {loading && <LoadingState />}

      {error && (
        <div className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-6 text-[#75685e] shadow-sm">
          {error}
        </div>
      )}

      {isEmpty && <EmptyState />}

      {data && data.tasks.length > 0 && (
        <div className="grid gap-6 lg:grid-cols-3">
          {statusOrder.map((status) => (
            <StatusColumn
              key={status}
              label={statusLabels[status]}
              onStatusChange={handleStatusChange}
              onViewRecipe={(recipeId) => navigate(`/recipes/${recipeId}`)}
              status={status}
              tasks={tasksByStatus[status]}
              updatingTaskId={updatingTaskId}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function StatusColumn({
  label,
  onStatusChange,
  onViewRecipe,
  status,
  tasks,
  updatingTaskId,
}: {
  label: string
  onStatusChange: (taskId: number, status: PrepTaskStatus) => Promise<void>
  onViewRecipe: (recipeId: number) => void
  status: PrepTaskStatus
  tasks: PrepTask[]
  updatingTaskId: number | null
}) {
  return (
    <section className={`min-h-130 rounded-xl border p-5 ${columnSurface(status)}`}>
      <div className="mb-5 border-b border-current/10 pb-4">
        <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">{label}</h2>
        <span className="rounded-full bg-white/70 px-3 py-1 text-sm font-bold">
          {tasks.length}
        </span>
        </div>
      </div>

      <div className="space-y-3">
        {tasks.length > 0 ? (
          tasks.map((task) => (
            <PrepTaskCard
              key={task.id}
              onStatusChange={onStatusChange}
              onViewRecipe={onViewRecipe}
              status={status}
              task={task}
              updating={updatingTaskId === task.id}
            />
          ))
        ) : (
          <p className="rounded-lg border border-white/70 bg-white/55 px-4 py-5 text-sm font-semibold text-[#75685e]">
            この状態の仕込みはありません。
          </p>
        )}
      </div>
    </section>
  )
}

function PrepTaskCard({
  onStatusChange,
  onViewRecipe,
  status,
  task,
  updating,
}: {
  onStatusChange: (taskId: number, status: PrepTaskStatus) => Promise<void>
  onViewRecipe: (recipeId: number) => void
  status: PrepTaskStatus
  task: PrepTask
  updating: boolean
}) {
  const actions = getStatusActions(status)

  return (
    <article className="rounded-xl border border-[#e2d6c7] bg-[#fffdf9] p-4 shadow-[0_10px_24px_rgba(84,58,35,0.06)]">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-xl font-bold leading-7 text-[#2e2822]">{task.recipe.name}</h3>
          <p className="mt-2 text-lg font-bold text-[#6f6258]">
            {formatQuantity(task.planned_quantity)} {task.planned_unit.name}
          </p>
        </div>
        <span className="shrink-0 rounded-md bg-[#78936f] px-3 py-1 text-sm font-bold text-white">
          {statusLabels[task.status]}
        </span>
      </div>

      {task.memo && (
        <p className="mt-3 rounded-lg bg-[#f7f1e8] px-3 py-2 text-sm leading-6 text-[#75685e]">
          {task.memo}
        </p>
      )}

      {task.completed_at && (
        <p className="mt-3 text-sm font-medium text-[#7b6f64]">
          完了: {formatTime(task.completed_at)}
        </p>
      )}

      <button
        className="mt-4 w-full rounded-lg border border-[#dfd1bf] bg-white px-3 py-3 text-sm font-bold text-[#5d5148] transition hover:bg-[#fbf7f0]"
        onClick={() => onViewRecipe(task.recipe.id)}
        type="button"
      >
        レシピを見る
      </button>

      <div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
        {actions.map((action) => (
          <button
            className="rounded-lg bg-[#c76738] px-3 py-3 text-sm font-bold text-white transition hover:bg-[#b65b31] disabled:cursor-not-allowed disabled:opacity-60"
            disabled={updating}
            key={action.status}
            onClick={() => void onStatusChange(task.id, action.status)}
            type="button"
          >
            {updating ? '更新中...' : action.label}
          </button>
        ))}
      </div>
    </article>
  )
}

function LoadingState() {
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      {statusOrder.map((status) => (
        <section className={`rounded-xl border p-5 ${columnSurface(status)}`} key={status}>
          <div className="mb-4 h-6 w-24 rounded bg-[#eadfce]" />
          <div className="space-y-3">
            <div className="h-36 rounded-xl bg-white/55" />
            <div className="h-28 rounded-xl bg-white/55" />
          </div>
        </section>
      ))}
    </div>
  )
}

function EmptyState() {
  return (
    <div className="rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-6 text-[#75685e] shadow-sm">
      <EmptyStateContent
        description="レシピから仕込みを追加しましょう。"
        imageSrc={emptyPrepBoard}
        title="今日の仕込みはまだありません。"
      />
    </div>
  )
}

function groupTasksByStatus(tasks: PrepTask[]): Record<PrepTaskStatus, PrepTask[]> {
  return {
    todo: tasks.filter((task) => task.status === 'todo'),
    doing: tasks.filter((task) => task.status === 'doing'),
    done: tasks.filter((task) => task.status === 'done'),
  }
}

function getStatusActions(status: PrepTaskStatus): Array<{ label: string; status: PrepTaskStatus }> {
  if (status === 'todo') {
    return [
      { label: '作業中にする', status: 'doing' },
      { label: '完了', status: 'done' },
    ]
  }

  if (status === 'doing') {
    return [
      { label: '未着手に戻す', status: 'todo' },
      { label: '完了', status: 'done' },
    ]
  }

  return [
    { label: '未着手に戻す', status: 'todo' },
    { label: '作業中に戻す', status: 'doing' },
  ]
}

function columnSurface(status: PrepTaskStatus) {
  if (status === 'doing') {
    return 'border-[#f0dc9f] bg-[#fff1c8] text-[#9a6410]'
  }
  if (status === 'done') {
    return 'border-[#cfe1cd] bg-[#e7f0e4] text-[#4d7a55]'
  }
  return 'border-[#e3d7c8] bg-[#f1e7dc] text-[#75685e]'
}

function columnTone(status: PrepTaskStatus) {
  if (status === 'doing') {
    return 'border-[#ead8a5] bg-[#fff1c8] text-[#9a6410]'
  }
  if (status === 'done') {
    return 'border-[#cfe1cd] bg-[#e8f1e5] text-[#4d7a55]'
  }
  return 'border-[#e0d3c2] bg-[#f1e7dc] text-[#75685e]'
}

function getToday() {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatDate(date: string) {
  return new Intl.DateTimeFormat('ja-JP', {
    dateStyle: 'full',
  }).format(new Date(`${date}T00:00:00`))
}

function formatQuantity(value: string) {
  return Number(value).toLocaleString('ja-JP', {
    maximumFractionDigits: 2,
  })
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat('ja-JP', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

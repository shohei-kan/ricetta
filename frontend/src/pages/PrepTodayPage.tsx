import { useCallback, useEffect, useMemo, useState, type FormEvent } from 'react'
import {
  archiveBoardMemo,
  createBoardMemo,
  fetchBoardMemos,
  type BoardMemo,
} from '../api/boardMemos'
import {
  createPrepTask,
  fetchPrepTasks,
  updatePrepTaskStatus,
  type PrepTask,
  type PrepTaskListResponse,
  type PrepTaskStatus,
} from '../api/prepTasks'
import { fetchRecipes, type RecipeListItem } from '../api/recipes'
import { fetchUnits } from '../api/units'
import { AutoResizeTextarea } from '../components/ui/AutoResizeTextarea'

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
  const [showAddForm, setShowAddForm] = useState(false)
  const [boardMemos, setBoardMemos] = useState<BoardMemo[]>([])
  const [memoHistory, setMemoHistory] = useState<BoardMemo[]>([])
  const [boardMemoText, setBoardMemoText] = useState('')
  const [boardMemoError, setBoardMemoError] = useState<string | null>(null)
  const [savingBoardMemo, setSavingBoardMemo] = useState(false)
  const [archivingBoardMemoId, setArchivingBoardMemoId] = useState<number | null>(null)
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

  const loadBoardMemos = useCallback(async () => {
    setBoardMemoError(null)
    try {
      const [activeMemos, historyMemos] = await Promise.all([
        fetchBoardMemos(),
        fetchBoardMemos({ includeArchived: true }),
      ])
      setBoardMemos(activeMemos)
      setMemoHistory(historyMemos)
    } catch {
      setBoardMemoError('メモを読み込めませんでした。もう一度お試しください。')
    }
  }, [])

  useEffect(() => {
    let active = true

    async function load() {
      setLoading(true)
      setError(null)
      setBoardMemoError(null)
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

      try {
        const [activeMemos, historyMemos] = await Promise.all([
          fetchBoardMemos(),
          fetchBoardMemos({ includeArchived: true }),
        ])
        if (active) {
          setBoardMemos(activeMemos)
          setMemoHistory(historyMemos)
        }
      } catch {
        if (active) {
          setBoardMemoError('メモを読み込めませんでした。もう一度お試しください。')
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

  async function handleAddBoardMemo(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const text = boardMemoText.trim()
    if (!text) {
      setBoardMemoError('メモを入力してください。')
      return
    }

    setSavingBoardMemo(true)
    setBoardMemoError(null)
    try {
      await createBoardMemo(text)
      setBoardMemoText('')
      await loadBoardMemos()
    } catch {
      setBoardMemoError('メモを追加できませんでした。もう一度お試しください。')
    } finally {
      setSavingBoardMemo(false)
    }
  }

  async function handleArchiveBoardMemo(id: number) {
    setArchivingBoardMemoId(id)
    setBoardMemoError(null)
    try {
      await archiveBoardMemo(id)
      await loadBoardMemos()
    } catch {
      setBoardMemoError('メモを完了できませんでした。もう一度お試しください。')
    } finally {
      setArchivingBoardMemoId(null)
    }
  }

  async function handleTaskCreated() {
    await loadPrepTasks()
    setShowAddForm(false)
  }

  const tasksByStatus = groupTasksByStatus(data?.tasks ?? [])
  return (
    <div className="mx-auto max-w-7xl px-5 py-6 md:px-8 md:py-8">
      <div className="mb-6 flex flex-col gap-4 border-b border-[#ded2c2] pb-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm font-bold text-[#c76738]">Prep Today</p>
          <h1 className="mt-2 text-3xl font-bold tracking-normal text-[#2e2822] md:text-4xl">
            今日の仕込み
          </h1>
          <p className="mt-2 text-base text-[#75685e]">{formatDate(data?.date ?? today)}</p>
          <p className="mt-2 text-sm leading-6 text-[#8a7a6d]">
            未完了の仕込みと、今日完了した仕込みを表示します。
          </p>
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

      {showAddForm && (
        <AddPrepTaskModal
          date={today}
          onCancel={() => setShowAddForm(false)}
          onCreated={handleTaskCreated}
        />
      )}

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

      {data && (
        <>
          <div className="grid gap-6 lg:grid-cols-3">
            {statusOrder.map((status) => (
              <StatusColumn
                key={status}
                label={statusLabels[status]}
                onAdd={status === 'todo' ? () => setShowAddForm(true) : undefined}
                onStatusChange={handleStatusChange}
                onViewRecipe={(recipeId) => navigate(`/recipes/${recipeId}`)}
                status={status}
                tasks={tasksByStatus[status]}
                updatingTaskId={updatingTaskId}
              />
            ))}
          </div>
          <BoardMemoSection
            archivingMemoId={archivingBoardMemoId}
            error={boardMemoError}
            history={memoHistory}
            memoText={boardMemoText}
            memos={boardMemos}
            onArchive={(id) => void handleArchiveBoardMemo(id)}
            onMemoTextChange={setBoardMemoText}
            onSubmit={(event) => void handleAddBoardMemo(event)}
            saving={savingBoardMemo}
          />
        </>
      )}
    </div>
  )
}

function StatusColumn({
  label,
  onAdd,
  onStatusChange,
  onViewRecipe,
  status,
  tasks,
  updatingTaskId,
}: {
  label: string
  onAdd?: () => void
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
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold">{label}</h2>
            <span className="rounded-full bg-white/70 px-3 py-1 text-sm font-bold">
              {tasks.length}
            </span>
          </div>
          {onAdd && (
            <button
              aria-label="仕込みを追加"
              className="hidden h-10 w-10 items-center justify-center rounded-lg bg-[#c76738] text-xl font-bold leading-none text-white transition hover:bg-[#b65b31] lg:flex"
              onClick={onAdd}
              type="button"
            >
              ＋
            </button>
          )}
        </div>
        {onAdd && (
          <button
            className="mt-3 flex min-h-12 w-full items-center justify-center rounded-lg bg-[#c76738] px-4 py-3 text-base font-bold text-white transition hover:bg-[#b65b31] lg:hidden"
            onClick={onAdd}
            type="button"
          >
            ＋ 仕込みを追加
          </button>
        )}
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
    <article className="rounded-xl border border-[#e2d6c7] bg-[#fffdf9] p-3 shadow-[0_8px_18px_rgba(84,58,35,0.05)]">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="text-lg font-bold leading-6 text-[#2e2822]">{task.recipe.name}</h3>
          <p className="mt-1 text-base font-bold text-[#6f6258]">
            {formatQuantity(task.planned_quantity)} {task.planned_unit.name}
          </p>
        </div>
        <span className="shrink-0 rounded-md bg-[#78936f] px-2.5 py-1 text-xs font-bold text-white">
          {statusLabels[task.status]}
        </span>
      </div>

      {task.memo && (
        <p className="mt-2 overflow-hidden text-ellipsis whitespace-nowrap rounded-lg bg-[#f7f1e8] px-3 py-1.5 text-sm text-[#75685e]">
          {task.memo}
        </p>
      )}

      {task.completed_at && (
        <p className="mt-2 text-xs font-medium text-[#7b6f64]">
          完了: {formatTime(task.completed_at)}
        </p>
      )}

      <div className="mt-3 grid grid-cols-3 gap-2">
        <button
          className="min-h-10 rounded-lg border border-[#dfd1bf] bg-white px-2 py-2 text-sm font-bold text-[#5d5148] transition hover:bg-[#fbf7f0]"
          onClick={() => onViewRecipe(task.recipe.id)}
          type="button"
        >
          詳細
        </button>
        {actions.map((action) => (
          <button
            className={`min-h-10 rounded-lg px-2 py-2 text-sm font-bold transition disabled:cursor-not-allowed disabled:opacity-60 ${actionButtonTone(action.status)}`}
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

function BoardMemoSection({
  archivingMemoId,
  error,
  history,
  memoText,
  memos,
  onArchive,
  onMemoTextChange,
  onSubmit,
  saving,
}: {
  archivingMemoId: number | null
  error: string | null
  history: BoardMemo[]
  memoText: string
  memos: BoardMemo[]
  onArchive: (id: number) => void
  onMemoTextChange: (value: string) => void
  onSubmit: (event: FormEvent<HTMLFormElement>) => void
  saving: boolean
}) {
  const suggestions = uniqueMemoTexts(history)

  return (
    <section className="mt-6 rounded-xl border border-[#ded2c2] bg-[#fffdf9] p-4 shadow-sm md:p-5">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-bold text-[#2e2822]">メモ</h2>
          <p className="mt-1 text-sm leading-6 text-[#75685e]">
            仕込み以外の、今日のホワイトボードメモです。
          </p>
        </div>
        <form className="flex flex-col gap-2 sm:flex-row md:min-w-[360px]" onSubmit={onSubmit}>
          <label className="sr-only" htmlFor="board-memo-text">
            メモを追加
          </label>
          <input
            className="min-h-11 flex-1 rounded-lg border border-[#d7cbbb] bg-white px-4 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
            id="board-memo-text"
            list="board-memo-history"
            onChange={(event) => onMemoTextChange(event.target.value)}
            placeholder="玉ねぎ、ラップ、フライヤー油交換など"
            value={memoText}
          />
          <datalist id="board-memo-history">
            {suggestions.map((text) => (
              <option key={text} value={text} />
            ))}
          </datalist>
          <button
            className="min-h-11 rounded-lg bg-[#c76738] px-4 py-2 text-sm font-bold text-white transition hover:bg-[#b65b31] disabled:cursor-not-allowed disabled:opacity-60"
            disabled={saving}
            type="submit"
          >
            {saving ? '追加中...' : '＋ 追加'}
          </button>
        </form>
      </div>

      {error && (
        <p className="mt-3 rounded-lg bg-[#fff0ed] px-4 py-3 text-sm font-semibold text-[#a23d2d]">
          {error}
        </p>
      )}

      <div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {memos.length > 0 ? (
          memos.map((memo) => (
            <label
              className="flex min-h-11 items-center gap-3 rounded-lg border border-[#eadfce] bg-white px-3 py-2 text-[#3d342d] transition hover:bg-[#fbf7f0]"
              key={memo.id}
            >
              <input
                checked={false}
                className="h-4 w-4 accent-[#c76738]"
                disabled={archivingMemoId === memo.id}
                onChange={() => onArchive(memo.id)}
                type="checkbox"
              />
              <span className="text-sm font-semibold leading-6">{memo.text}</span>
            </label>
          ))
        ) : (
          <p className="rounded-lg border border-[#eadfce] bg-white px-4 py-3 text-sm font-semibold text-[#75685e] sm:col-span-2 lg:col-span-3">
            メモはありません。
          </p>
        )}
      </div>
    </section>
  )
}

function AddPrepTaskModal({
  date,
  onCancel,
  onCreated,
}: {
  date: string
  onCancel: () => void
  onCreated: () => Promise<void>
}) {
  const [recipes, setRecipes] = useState<RecipeListItem[]>([])
  const [unitOptions, setUnitOptions] = useState<Array<{ id: number; name: string }>>([])
  const [referencesLoading, setReferencesLoading] = useState(true)
  const [referenceError, setReferenceError] = useState<string | null>(null)
  const [recipeId, setRecipeId] = useState('')
  const [plannedQuantity, setPlannedQuantity] = useState('')
  const [plannedUnitId, setPlannedUnitId] = useState('')
  const [memo, setMemo] = useState('')
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [validationErrors, setValidationErrors] = useState<string[]>([])

  useEffect(() => {
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        onCancel()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => {
      document.body.style.overflow = previousOverflow
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [onCancel])

  useEffect(() => {
    let active = true

    async function loadReferences() {
      setReferencesLoading(true)
      setReferenceError(null)
      try {
        const [recipeResponse, unitResponse] = await Promise.all([fetchRecipes(), fetchUnits()])
        if (active) {
          setRecipes(recipeResponse)
          setUnitOptions(unitResponse.map((unit) => ({ id: unit.id, name: unit.name })))
        }
      } catch {
        if (active) {
          setReferenceError('レシピまたは単位を読み込めませんでした。もう一度お試しください。')
        }
      } finally {
        if (active) {
          setReferencesLoading(false)
        }
      }
    }

    void loadReferences()
    return () => {
      active = false
    }
  }, [])

  function handleRecipeChange(value: string) {
    setRecipeId(value)
    const recipe = recipes.find((item) => item.id === Number(value))
    if (!recipe) {
      setPlannedQuantity('')
      setPlannedUnitId('')
      return
    }

    setPlannedQuantity(recipe.base_yield_quantity)
    setPlannedUnitId(String(recipe.base_yield_unit.id))
    setUnitOptions((current) =>
      current.some((unit) => unit.id === recipe.base_yield_unit.id)
        ? current
        : [...current, recipe.base_yield_unit],
    )
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const errors = validateAddPrepTask({ plannedQuantity, plannedUnitId, recipeId })
    setValidationErrors(errors)
    setSaveError(null)
    if (errors.length > 0) {
      return
    }

    setSaving(true)
    try {
      await createPrepTask({
        date,
        recipe_id: Number(recipeId),
        planned_quantity: plannedQuantity,
        planned_unit_id: Number(plannedUnitId),
        memo: memo.trim(),
      })
      await onCreated()
    } catch {
      setSaveError('保存に失敗しました。入力内容を確認して、もう一度お試しください。')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#2a241f]/35 p-4 md:p-8"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          onCancel()
        }
      }}
    >
      <section
        aria-labelledby="add-prep-task-title"
        aria-modal="true"
        className="max-h-[calc(100dvh-2rem)] w-full max-w-2xl overflow-y-auto rounded-2xl border border-[#ded2c2] bg-[#fffdf9] p-5 shadow-[0_24px_70px_rgba(42,36,31,0.24)] md:p-6"
        role="dialog"
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-[#34291f]" id="add-prep-task-title">
              仕込みを追加
            </h2>
          <p className="mt-2 text-sm leading-6 text-[#75685e]">
            レシピを選ぶと、基準量と基準単位を自動入力します。
          </p>
          </div>
          <button
            aria-label="閉じる"
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-2xl text-[#75685e] transition hover:bg-[#f1e7dc] hover:text-[#2e2822]"
            onClick={onCancel}
            type="button"
          >
            ×
          </button>
        </div>

        {referenceError && (
          <p className="mt-4 rounded-lg bg-[#fff0ed] px-4 py-3 text-sm font-semibold text-[#a23d2d]">
            {referenceError}
          </p>
        )}

        <form className="mt-5 grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
        <label className="block md:col-span-2">
          <span className="text-sm font-semibold text-[#4b4037]">レシピ *</span>
          <select
            className="mt-2 min-h-12 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2 disabled:bg-[#eee7db]"
            disabled={referencesLoading || Boolean(referenceError)}
            onChange={(event) => handleRecipeChange(event.target.value)}
            value={recipeId}
          >
            <option value="">選択してください</option>
            {recipes.map((recipe) => (
              <option key={recipe.id} value={recipe.id}>
                {recipe.name}
              </option>
            ))}
          </select>
          {referencesLoading && (
            <span className="mt-2 block text-xs text-[#75685e]">レシピを読み込んでいます...</span>
          )}
        </label>

        <label className="block">
          <span className="text-sm font-semibold text-[#4b4037]">予定数量 *</span>
          <input
            className="mt-2 min-h-12 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
            inputMode="decimal"
            onChange={(event) => setPlannedQuantity(event.target.value)}
            value={plannedQuantity}
          />
        </label>

        <label className="block">
          <span className="text-sm font-semibold text-[#4b4037]">予定単位 *</span>
          <select
            className="mt-2 min-h-12 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 text-base text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2 disabled:bg-[#eee7db]"
            disabled={referencesLoading}
            onChange={(event) => setPlannedUnitId(event.target.value)}
            value={plannedUnitId}
          >
            <option value="">選択してください</option>
            {unitOptions.map((unit) => (
              <option key={unit.id} value={unit.id}>
                {unit.name}
              </option>
            ))}
          </select>
        </label>

        <label className="block md:col-span-2">
          <span className="text-sm font-semibold text-[#4b4037]">メモ</span>
          <AutoResizeTextarea
            className="mt-2 w-full rounded-lg border border-[#d7cbbb] bg-white px-4 py-3 text-base leading-7 text-[#2b2621] outline-none ring-[#b88458] transition focus:ring-2"
            onChange={(event) => setMemo(event.target.value)}
            value={memo}
          />
        </label>

        {(validationErrors.length > 0 || saveError) && (
          <div className="rounded-lg border border-[#f1c8c0] bg-[#fff0ed] p-4 text-[#a23d2d] md:col-span-2">
            <p className="font-bold">仕込みを追加できませんでした。</p>
            {saveError && <p className="mt-2 text-sm leading-6">{saveError}</p>}
            {validationErrors.length > 0 && (
              <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">
                {validationErrors.map((error) => (
                  <li key={error}>{error}</li>
                ))}
              </ul>
            )}
          </div>
        )}

        <div className="flex flex-col gap-3 sm:flex-row md:col-span-2">
          <button
            className="min-h-12 rounded-lg bg-[#c76738] px-5 py-3 text-base font-bold text-white transition hover:bg-[#b65b31] disabled:cursor-not-allowed disabled:opacity-60"
            disabled={saving || referencesLoading || Boolean(referenceError)}
            type="submit"
          >
            {saving ? '追加中...' : '仕込みに追加'}
          </button>
          <button
            className="min-h-12 rounded-lg border border-[#dfd1bf] bg-white px-5 py-3 text-base font-bold text-[#5d5148] transition hover:bg-[#fbf7f0]"
            onClick={onCancel}
            type="button"
          >
            キャンセル
          </button>
        </div>
        </form>
      </section>
    </div>
  )
}

function validateAddPrepTask({
  plannedQuantity,
  plannedUnitId,
  recipeId,
}: {
  plannedQuantity: string
  plannedUnitId: string
  recipeId: string
}) {
  const errors: string[] = []
  if (!recipeId) {
    errors.push('レシピを選択してください。')
  }
  const quantity = Number(plannedQuantity)
  if (!plannedQuantity || Number.isNaN(quantity)) {
    errors.push('予定数量を入力してください。')
  } else if (quantity <= 0) {
    errors.push('予定数量は0より大きい値を入力してください。')
  }
  if (!plannedUnitId) {
    errors.push('予定単位を選択してください。')
  }
  return errors
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
      { label: '開始', status: 'doing' },
      { label: '完了', status: 'done' },
    ]
  }

  if (status === 'doing') {
    return [
      { label: '未着手', status: 'todo' },
      { label: '完了', status: 'done' },
    ]
  }

  return [
    { label: '未着手', status: 'todo' },
    { label: '作業中', status: 'doing' },
  ]
}

function actionButtonTone(status: PrepTaskStatus) {
  if (status === 'todo') {
    return 'border border-[#dfd1bf] bg-white text-[#5d5148] hover:bg-[#fbf7f0]'
  }
  if (status === 'doing') {
    return 'bg-[#d8951d] text-white hover:bg-[#c78317]'
  }
  return 'bg-[#c76738] text-white hover:bg-[#b65b31]'
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

function uniqueMemoTexts(memos: BoardMemo[]) {
  const seen = new Set<string>()
  return memos
    .map((memo) => memo.text.trim())
    .filter((text) => {
      if (!text || seen.has(text)) {
        return false
      }
      seen.add(text)
      return true
    })
}

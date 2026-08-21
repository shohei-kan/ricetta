export type NavigateOptions = {
  replace?: boolean
}

export type Navigate = (path: string, options?: NavigateOptions) => void

export type CollectionPath = '/recipes' | '/ingredients'

type BrowserHistoryWriter = Pick<History, 'pushState' | 'replaceState'>

export const hierarchyBackOptions = { replace: true } as const

export function getDetailBackPath(collectionPath: CollectionPath) {
  return collectionPath
}

export function getFormBackPath(collectionPath: CollectionPath, id?: number) {
  return id === undefined ? collectionPath : `${collectionPath}/${id}`
}

export function updateBrowserHistory(
  history: BrowserHistoryWriter,
  currentPath: string,
  nextPath: string,
  options: NavigateOptions = {},
) {
  if (currentPath === nextPath) {
    return false
  }

  if (options.replace) {
    history.replaceState(null, '', nextPath)
  } else {
    history.pushState(null, '', nextPath)
  }

  return true
}

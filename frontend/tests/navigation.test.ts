import assert from 'node:assert/strict'
import test from 'node:test'
import {
  getDetailBackPath,
  getFormBackPath,
  hierarchyBackOptions,
  updateBrowserHistory,
  type NavigateOptions,
} from '../src/navigation.ts'

class MemoryHistory {
  private entries: string[]
  private index: number

  constructor(initialPath: string) {
    this.entries = [initialPath]
    this.index = 0
  }

  get currentPath() {
    return this.entries[this.index]
  }

  get length() {
    return this.entries.length
  }

  pushState(_data: unknown, _unused: string, url?: string | URL | null) {
    this.entries = this.entries.slice(0, this.index + 1)
    this.entries.push(String(url))
    this.index += 1
  }

  replaceState(_data: unknown, _unused: string, url?: string | URL | null) {
    this.entries[this.index] = String(url)
  }

  back() {
    if (this.index > 0) {
      this.index -= 1
    }
  }

  forward() {
    if (this.index < this.entries.length - 1) {
      this.index += 1
    }
  }
}

function navigate(history: MemoryHistory, path: string, options?: NavigateOptions) {
  updateBrowserHistory(history, history.currentPath, path, options)
}

for (const route of [
  { collection: '/recipes', detail: '/recipes/42', edit: '/recipes/42/edit', new: '/recipes/new' },
  { collection: '/ingredients', detail: '/ingredients/42', edit: '/ingredients/42/edit', new: '/ingredients/new' },
] as const) {
  test(`${route.collection}: app back follows the screen hierarchy without a loop`, () => {
    const history = new MemoryHistory(route.collection)

    navigate(history, route.detail)
    navigate(history, route.edit)
    navigate(history, getFormBackPath(route.collection, 42), hierarchyBackOptions)
    assert.equal(history.currentPath, route.detail)

    navigate(history, getDetailBackPath(route.collection), hierarchyBackOptions)
    assert.equal(history.currentPath, route.collection)
  })

  test(`${route.collection}: direct detail and edit access have deterministic back targets`, () => {
    const detailHistory = new MemoryHistory(route.detail)
    navigate(detailHistory, getDetailBackPath(route.collection), hierarchyBackOptions)
    assert.equal(detailHistory.currentPath, route.collection)

    const editHistory = new MemoryHistory(route.edit)
    navigate(editHistory, getFormBackPath(route.collection, 42), hierarchyBackOptions)
    assert.equal(editHistory.currentPath, route.detail)
  })

  test(`${route.collection}: new back and form cancel return to the expected parent`, () => {
    const newHistory = new MemoryHistory(route.new)
    navigate(newHistory, getFormBackPath(route.collection), hierarchyBackOptions)
    assert.equal(newHistory.currentPath, route.collection)

    const editHistory = new MemoryHistory(route.edit)
    navigate(editHistory, getFormBackPath(route.collection, 42), hierarchyBackOptions)
    assert.equal(editHistory.currentPath, route.detail)
  })

  test(`${route.collection}: browser back and forward retain normal history behavior`, () => {
    const history = new MemoryHistory(route.collection)
    navigate(history, route.detail)
    navigate(history, route.edit)

    history.back()
    assert.equal(history.currentPath, route.detail)

    history.forward()
    assert.equal(history.currentPath, route.edit)
  })
}

test('regular navigation pushes while hierarchy back replaces the current entry', () => {
  const history = new MemoryHistory('/recipes')

  navigate(history, '/recipes/42')
  assert.equal(history.length, 2)
  history.back()
  assert.equal(history.currentPath, '/recipes')
  history.forward()
  assert.equal(history.currentPath, '/recipes/42')

  navigate(history, '/recipes', hierarchyBackOptions)
  assert.equal(history.length, 2)
  history.back()
  assert.equal(history.currentPath, '/recipes')
})

test('navigating to the current path does not write another history entry', () => {
  const history = new MemoryHistory('/recipes')
  const changed = updateBrowserHistory(history, history.currentPath, '/recipes')

  assert.equal(changed, false)
  assert.equal(history.currentPath, '/recipes')
  assert.equal(history.length, 1)
})

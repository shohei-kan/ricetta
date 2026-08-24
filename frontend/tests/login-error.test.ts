import assert from 'node:assert/strict'
import test from 'node:test'
import { apiRequest, ApiError } from '../src/api/api.ts'
import type { AuthSession } from '../src/api/auth.ts'
import {
  getLoginErrorMessage,
  INVALID_CREDENTIALS_MESSAGE,
  LOGIN_FAILURE_MESSAGE,
  LOGIN_THROTTLED_MESSAGE,
  NETWORK_FAILURE_MESSAGE,
} from '../src/auth/login-error.ts'

const backendDetail = 'backend-sensitive-detail'

test('HTTP 400 uses the generic authentication message without exposing backend detail', () => {
  const error = new ApiError(backendDetail, 400, { detail: backendDetail })

  const message = getLoginErrorMessage(error)

  assert.equal(message, INVALID_CREDENTIALS_MESSAGE)
  assert.doesNotMatch(message, /backend-sensitive-detail/)
})

test('a failure without an HTTP response uses the network failure message', () => {
  const message = getLoginErrorMessage(new TypeError('Failed to fetch'))

  assert.equal(message, NETWORK_FAILURE_MESSAGE)
})

test('HTTP 429 uses a distinct throttling message', () => {
  const error = new ApiError(backendDetail, 429, { detail: backendDetail })

  const message = getLoginErrorMessage(error)

  assert.equal(message, LOGIN_THROTTLED_MESSAGE)
  assert.notEqual(message, INVALID_CREDENTIALS_MESSAGE)
  assert.notEqual(message, NETWORK_FAILURE_MESSAGE)
  assert.doesNotMatch(message, /backend-sensitive-detail/)
})

test('other HTTP failures do not expose backend detail', () => {
  const error = new ApiError(backendDetail, 500, { detail: backendDetail })

  const message = getLoginErrorMessage(error)

  assert.equal(message, LOGIN_FAILURE_MESSAGE)
  assert.doesNotMatch(message, /backend-sensitive-detail/)
})

test('a successful login response is returned unchanged', async () => {
  const session: AuthSession = {
    user: { id: 1, email: 'test-user', name: 'Test User' },
    shop: { id: 1, name: 'Test Shop' },
    membership: { role: 'owner', display_name: 'Test Owner' },
  }
  const originalFetch = globalThis.fetch
  const originalDocument = Object.getOwnPropertyDescriptor(
    globalThis,
    'document',
  )

  Object.defineProperty(globalThis, 'document', {
    configurable: true,
    value: { cookie: '' },
  })
  globalThis.fetch = async (input, init) => {
    assert.equal(String(input), '/api/v1/auth/login/')
    assert.equal(init?.method, 'POST')
    return new Response(JSON.stringify(session), {
      headers: { 'Content-Type': 'application/json' },
      status: 200,
    })
  }

  try {
    const result = await apiRequest<AuthSession>('/auth/login/', {
      method: 'POST',
      body: {
        email: 'test-user',
        password: '',
      },
    })

    assert.deepEqual(result, session)
  } finally {
    globalThis.fetch = originalFetch
    if (originalDocument) {
      Object.defineProperty(globalThis, 'document', originalDocument)
    } else {
      delete (globalThis as { document?: Document }).document
    }
  }
})

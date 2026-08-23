import { ApiError } from '../api/api.ts'

export const INVALID_CREDENTIALS_MESSAGE =
  'メールアドレスまたはパスワードが正しくありません。'
export const NETWORK_FAILURE_MESSAGE =
  '通信に失敗しました。もう一度お試しください。'
export const LOGIN_THROTTLED_MESSAGE =
  'ログイン試行回数が上限に達しました。しばらく待ってからもう一度お試しください。'
export const LOGIN_FAILURE_MESSAGE =
  'ログインに失敗しました。もう一度お試しください。'

export function getLoginErrorMessage(caught: unknown): string {
  if (!(caught instanceof ApiError)) {
    return NETWORK_FAILURE_MESSAGE
  }

  if (caught.status === 400) {
    return INVALID_CREDENTIALS_MESSAGE
  }

  if (caught.status === 429) {
    return LOGIN_THROTTLED_MESSAGE
  }

  return LOGIN_FAILURE_MESSAGE
}

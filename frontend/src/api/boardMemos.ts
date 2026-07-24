import { apiRequest } from './api'

export type BoardMemo = {
  id: number
  text: string
  is_archived: boolean
  archived_at: string | null
  created_at: string
  updated_at: string
}

export function fetchBoardMemos(options: { includeArchived?: boolean } = {}): Promise<BoardMemo[]> {
  const query = options.includeArchived ? '?include_archived=1' : ''
  return apiRequest(`/board-memos/${query}`)
}

export function createBoardMemo(text: string): Promise<BoardMemo> {
  return apiRequest('/board-memos/', {
    method: 'POST',
    body: { text },
  })
}

export function archiveBoardMemo(id: number): Promise<BoardMemo> {
  return apiRequest(`/board-memos/${id}/archive/`, {
    method: 'PATCH',
  })
}

export function unarchiveBoardMemo(id: number): Promise<BoardMemo> {
  return apiRequest(`/board-memos/${id}/unarchive/`, {
    method: 'PATCH',
  })
}

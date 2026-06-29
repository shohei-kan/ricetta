import { apiRequest } from './api'

export type Shop = {
  id: number
  name: string
  business_type: string
  memo: string
  created_at: string
  updated_at: string
}

export type ShopUpdateInput = {
  name: string
  business_type: string
  memo: string
}

export function fetchShop(): Promise<Shop> {
  return apiRequest('/shop/me/')
}

export function updateShop(input: ShopUpdateInput): Promise<Shop> {
  return apiRequest('/shop/me/', {
    method: 'PATCH',
    body: input,
  })
}

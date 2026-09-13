import { apiClient } from './client'
import { useAuthStore } from '@/store/authStore'

export interface TokenResponse {
  access_token: string
  refresh_token?: string
  token_type: string
  expires_in?: number
}

export const login = async (data: { email: string; password: string }) => {
  const response = await apiClient.post<TokenResponse>('/auth/login', data)
  useAuthStore.getState().setToken(response.data.access_token)
  return response.data
}

export const signup = async (data: { email: string; password: string; full_name?: string }) => {
  const response = await apiClient.post<TokenResponse>('/auth/signup', data)
  useAuthStore.getState().setToken(response.data.access_token)
  return response.data
}

export const logout = async () => {
  try {
    await apiClient.post('/auth/logout')
  } finally {
    useAuthStore.getState().setToken(null)
  }
}

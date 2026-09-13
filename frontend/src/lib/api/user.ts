import { apiClient } from './client'

export interface PreferenceResponse {
  id: string
  profile_id: string
  preferred_roles: string[]
  skills: string[]
  preferred_locations: string[]
  remote_only: boolean
  salary_min: number | null
  salary_max: number | null
  salary_currency: string
  experience_level: string | null
  company_size: string | null
  employment_type: string | null
}

export const getPreferences = async () => {
  const response = await apiClient.get<PreferenceResponse>('/preferences')
  return response.data
}

export const updatePreferences = async (data: Partial<PreferenceResponse>) => {
  const response = await apiClient.put<PreferenceResponse>('/preferences', data)
  return response.data
}

export interface ProfileResponse {
  id: string
  email: string
  full_name: string | null
  avatar_url: string | null
  resume_url: string | null
  created_at: string
}

export const getProfile = async () => {
  const response = await apiClient.get<ProfileResponse>('/profile/me')
  return response.data
}

export const updateProfile = async (data: { full_name?: string | null; avatar_url?: string | null }) => {
  const response = await apiClient.put<ProfileResponse>('/profile/me', data)
  return response.data
}

export interface NotificationResponse {
  id: string
  type: string
  title: string
  body: string
  read: boolean
  delivered: boolean
  created_at: string
}

export const getNotifications = async (unreadOnly?: boolean) => {
  const params = unreadOnly ? { unread_only: true } : {}
  const response = await apiClient.get<NotificationResponse[]>('/notifications', { params })
  return response.data
}

export const markNotificationRead = async (id: string) => {
  const response = await apiClient.post<NotificationResponse>(`/notifications/${id}/read`)
  return response.data
}

export const markAllNotificationsRead = async () => {
  await apiClient.post('/notifications/read-all')
}

import { apiClient } from './client'

export interface JobResponse {
  id: string
  source: string
  source_url: string
  title: string
  company: string
  location: string | null
  remote: boolean
  salary_min: number | null
  salary_max: number | null
  salary_currency: string | null
  experience_level: string | null
  employment_type: string
  required_skills: string[]
  responsibilities: string[]
  benefits: string[]
  description_normalized: string | null
  description_raw: string | null
  is_active: boolean
  created_at: string
}

export interface SavedJobResponse {
  id: string
  job: JobResponse
  notes: string | null
  applied: boolean
  created_at: string
}

export const getJobs = async (params?: Record<string, any>) => {
  const response = await apiClient.get<JobResponse[]>('/jobs', { params })
  return response.data
}

export const getJob = async (id: string) => {
  const response = await apiClient.get<JobResponse>(`/jobs/${id}`)
  return response.data
}

export const getSavedJobs = async () => {
  const response = await apiClient.get<SavedJobResponse[]>('/saved')
  return response.data
}

export const saveJob = async (jobId: string, notes?: string) => {
  const response = await apiClient.post<SavedJobResponse>('/saved', { job_id: jobId, notes })
  return response.data
}

export const unsaveJob = async (jobId: string) => {
  await apiClient.delete(`/saved/${jobId}`)
}

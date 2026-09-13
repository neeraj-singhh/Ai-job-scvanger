import { apiClient } from './client'
import { JobResponse } from './jobs'

export interface JobMatchResponse {
  id: string
  job: JobResponse
  score: number
  matched_skills: string[]
  missing_skills: string[]
  explanation: string
  notified: boolean
  created_at: string
}

export const getMatches = async (minScore?: number) => {
  const params = minScore ? { min_score: minScore } : {}
  const response = await apiClient.get<JobMatchResponse[]>('/matches', { params })
  return response.data
}

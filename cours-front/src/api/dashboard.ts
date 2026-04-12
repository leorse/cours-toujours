import api from './client'

export interface SubjectSummary {
  id: string
  name: string
  image: string
  xp: number
  totalSteps: number
  completedSteps: number
  progressPercent: number
}

export const getDashboard = () =>
  api.get<{ subjects: SubjectSummary[] }>('/api/dashboard').then(r => r.data)

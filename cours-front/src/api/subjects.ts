import api from './client'

export interface ChapterSummary {
  id: string
  title: string
  icon: string
  order: number
  totalSteps: number
  completedSteps: number
}

export interface StepSummary {
  id: string
  title: string
  subtitle: string
  type: string
  order: number
  activated: boolean
  completed: boolean
  mastery: number
}

export const getSubject = (subjectId: string) =>
  api.get<{ subject: { id: string; name: string; image: string }; chapters: ChapterSummary[] }>(
    `/api/subjects/${subjectId}`
  ).then(r => r.data)

export const getChapter = (subjectId: string, chapterId: string) =>
  api.get<{ subject: { id: string; name: string }; chapterId: string; steps: StepSummary[] }>(
    `/api/subjects/${subjectId}/chapters/${chapterId}`
  ).then(r => r.data)

import api from './client'

export interface GeneratedExercise {
  id: string
  templateId: string
  type: string
  renderType: string
  multiple: boolean
  question: string
  options?: string[]
  answer: string | string[]
  explanation?: string
  unit?: string
  variables?: Record<string, unknown>
  tags: string[]
  meta?: Record<string, unknown>
}

export interface StepPayload {
  id: string
  title: string
  type: string
  subjectId: string
  chapterId: string
  totalPages: number
  currentPage: number
  isLastPage: boolean
  pageType: string
  markdownHtml?: string
  inlineExercises?: GeneratedExercise[]
  exercises?: GeneratedExercise[]
  dialogue?: Record<string, unknown>
  characters?: Record<string, unknown>
  conditions?: string | string[]
}

export interface StepResult {
  success: boolean
  xpEarned: number
  correctCount: number
  totalCount: number
  scorePercent: number
  answerResults: Record<string, boolean>
  nextUrl?: string
  message: string
}

export const getStep = (stepId: string, pageIdx = 0) =>
  api.get<StepPayload>(`/api/steps/${stepId}`, { params: { pageIdx } }).then(r => r.data)

export const submitStep = (stepId: string, answers: Record<string, unknown>, generatedExercises?: GeneratedExercise[]) =>
  api.post<StepResult>('/api/submit', { stepId, answers, generatedExercises }).then(r => r.data)

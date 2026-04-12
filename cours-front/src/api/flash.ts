import api from './client'
import type { GeneratedExercise, StepResult } from './steps'

export const getFlashSession = (subjectId: string, count = 10) =>
  api.get<{ subjectId: string; exercises: GeneratedExercise[]; count: number }>(
    `/api/flash/${subjectId}`, { params: { count } }
  ).then(r => r.data)

export const submitFlash = (subjectId: string, answers: Record<string, unknown>, generatedExercises: GeneratedExercise[]) =>
  api.post<StepResult>(`/api/flash/${subjectId}/submit`, { answers, generatedExercises }).then(r => r.data)

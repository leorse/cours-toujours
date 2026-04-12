import { useState } from 'react'
import type { GeneratedExercise, StepResult } from '../api/steps'
import InputExercise from './exercises/InputExercise'
import QcmExercise from './exercises/QcmExercise'
import DragDropExercise from './exercises/DragDropExercise'
import ResultView from './exercises/ResultView'
import styles from './ExerciseSession.module.css'

interface Props {
  exercises: GeneratedExercise[]
  stepType: string
  onSubmit: (answers: Record<string, unknown>, exercises: GeneratedExercise[]) => Promise<StepResult | null>
  onNext: () => void
}

export default function ExerciseSession({ exercises, onSubmit, onNext }: Props) {
  const [answers, setAnswers] = useState<Record<string, unknown>>({})
  const [result, setResult] = useState<StepResult | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const setAnswer = (id: string, value: unknown) => setAnswers(p => ({ ...p, [id]: value }))

  const handleSubmit = async () => {
    setSubmitting(true)
    try { const r = await onSubmit(answers, exercises); setResult(r) }
    finally { setSubmitting(false) }
  }

  if (result) return <ResultView result={result} exercises={exercises} answers={answers} onNext={onNext} />

  return (
    <div className={styles.session}>
      <div className={styles.list}>
        {exercises.map((ex, i) => (
          <div key={ex.id} className={styles.card}>
            <div className={styles.num}>Question {i + 1}</div>
            {renderEx(ex, answers[ex.id], v => setAnswer(ex.id, v))}
          </div>
        ))}
      </div>
      <div className={styles.footer}>
        <button className="btn-primary" onClick={handleSubmit} disabled={submitting}>
          {submitting ? 'Correction...' : 'Vérifier'}
        </button>
      </div>
    </div>
  )
}

function renderEx(ex: GeneratedExercise, value: unknown, onChange: (v: unknown) => void) {
  const t = ex.type || ex.renderType || 'input'
  if (t === 'qcm' || t === 'multiselect') return <QcmExercise exercise={ex} value={value as string | string[]} onChange={onChange} />
  if (t === 'drag_drop' || t === 'dragdrop') return <DragDropExercise exercise={ex} value={value as string[]} onChange={onChange} />
  return <InputExercise exercise={ex} value={value as string} onChange={onChange} />
}

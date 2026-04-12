import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getFlashSession, submitFlash } from '../api/flash'
import type { GeneratedExercise } from '../api/steps'
import ExerciseSession from '../components/ExerciseSession'
import styles from './FlashPage.module.css'

export default function FlashPage() {
  const { subjectId } = useParams<{ subjectId: string }>()
  const [exercises, setExercises] = useState<GeneratedExercise[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    if (!subjectId) return
    getFlashSession(subjectId, 10).then(d => setExercises(d.exercises)).finally(() => setLoading(false))
  }, [subjectId])

  const handleSubmit = async (answers: Record<string, unknown>, exs: GeneratedExercise[]) => {
    if (!subjectId) return null
    return submitFlash(subjectId, answers, exs)
  }

  if (loading) return <div className="loading">Chargement du mode flash...</div>

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <button className="btn-secondary" onClick={() => navigate(`/subjects/${subjectId}`)}>← Retour</button>
        <h1>⚡ Mode Flash</h1>
      </header>
      <ExerciseSession exercises={exercises} stepType="flash" onSubmit={handleSubmit}
        onNext={() => navigate(`/subjects/${subjectId}`)} />
    </div>
  )
}

import { useState, useEffect } from 'react'
import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import { getStep, submitStep, type StepPayload, type GeneratedExercise } from '../api/steps'
import CoursContent from '../components/CoursContent'
import ExerciseSession from '../components/ExerciseSession'
import DialogueView from '../components/DialogueView'
import styles from './StepPage.module.css'

export default function StepPage() {
  const { stepId } = useParams<{ stepId: string }>()
  const [searchParams] = useSearchParams()
  const pageIdx = parseInt(searchParams.get('pageIdx') ?? '0')
  const [step, setStep] = useState<StepPayload | null>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    if (!stepId) return
    setLoading(true)
    getStep(stepId, pageIdx).then(setStep).finally(() => setLoading(false))
  }, [stepId, pageIdx])

  const handleNext = () => {
    if (!step) return
    if (!step.isLastPage) {
      navigate(`/step/${stepId}?pageIdx=${pageIdx + 1}`)
    } else {
      if (step.chapterId) {
        const parts = step.chapterId.split('.')
        navigate(`/subjects/${step.subjectId}/chapters/${parts[parts.length - 1]}`)
      } else {
        navigate(`/subjects/${step.subjectId}`)
      }
    }
  }

  const handleSubmit = async (answers: Record<string, unknown>, exercises: GeneratedExercise[]) => {
    if (!stepId) return null
    return submitStep(stepId, answers, exercises)
  }

  if (loading) return <div className="loading">Chargement...</div>
  if (!step) return <div>Étape introuvable</div>

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <button className="btn-secondary" onClick={() => navigate(-1)}>← Retour</button>
        <h1 className={styles.title}>{step.title}</h1>
        {step.totalPages > 1 && <span className={styles.paging}>{pageIdx + 1}/{step.totalPages}</span>}
      </header>
      <div className={styles.content}>
        {step.pageType === 'dialogue' && step.dialogue ? (
          <DialogueView dialogue={step.dialogue} characters={step.characters ?? {}} onComplete={handleNext} />
        ) : step.pageType === 'cours' || step.pageType === 'theory' ? (
          <CoursContent markdownHtml={step.markdownHtml ?? ''} inlineExercises={step.inlineExercises} onComplete={handleNext} />
        ) : step.exercises && step.exercises.length > 0 ? (
          <ExerciseSession exercises={step.exercises} stepType={step.type} onSubmit={handleSubmit} onNext={handleNext} />
        ) : (
          <div className={styles.empty}>
            <p>Contenu en préparation...</p>
            <button className="btn-primary" onClick={handleNext}>Continuer →</button>
          </div>
        )}
      </div>
    </div>
  )
}

import type { GeneratedExercise } from '../../api/steps'
import styles from './Exercise.module.css'

interface Props {
  exercise: GeneratedExercise
  value: string
  onChange: (v: string) => void
  readonly?: boolean
  correct?: boolean
}

export default function InputExercise({ exercise, value, onChange, readonly, correct }: Props) {
  return (
    <div className={styles.ex}>
      <p className={styles.q}>{exercise.question}</p>
      <div className={styles.inputRow}>
        <input type="text" value={value ?? ''} onChange={e => onChange(e.target.value)} disabled={readonly}
          className={`${styles.input} ${readonly ? (correct ? styles.correct : styles.incorrect) : ''}`}
          placeholder="Votre réponse..." />
        {exercise.unit && <span className={styles.unit}>{exercise.unit}</span>}
      </div>
      {readonly && exercise.explanation && <p className={styles.expl}>{exercise.explanation}</p>}
    </div>
  )
}

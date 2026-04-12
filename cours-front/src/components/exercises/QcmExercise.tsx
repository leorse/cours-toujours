import type { GeneratedExercise } from '../../api/steps'
import styles from './Exercise.module.css'

interface Props {
  exercise: GeneratedExercise
  value: string | string[]
  onChange: (v: string | string[]) => void
  readonly?: boolean
  correct?: boolean
}

export default function QcmExercise({ exercise, value, onChange, readonly }: Props) {
  const multiple = exercise.multiple
  const selected = Array.isArray(value) ? value : value ? [value] : []
  const correct = Array.isArray(exercise.answer) ? exercise.answer : [exercise.answer as string]

  const toggle = (opt: string) => {
    if (readonly) return
    if (multiple) {
      const s = selected.includes(opt) ? selected.filter(x => x !== opt) : [...selected, opt]
      onChange(s)
    } else { onChange(opt) }
  }

  return (
    <div className={styles.ex}>
      <p className={styles.q}>{exercise.question}</p>
      <div className={styles.opts}>
        {exercise.options?.map(opt => {
          const sel = selected.includes(opt)
          const isCorrect = correct.includes(opt)
          let cls = styles.opt
          if (readonly) { if (isCorrect) cls += ` ${styles.optCorrect}`; else if (sel) cls += ` ${styles.optWrong}` }
          else if (sel) cls += ` ${styles.optSel}`
          return <button key={opt} className={cls} onClick={() => toggle(opt)} disabled={readonly}>{opt}</button>
        })}
      </div>
      {readonly && exercise.explanation && <p className={styles.expl}>{exercise.explanation}</p>}
    </div>
  )
}

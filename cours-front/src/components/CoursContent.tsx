import { useEffect, useRef, useState } from 'react'
import renderMathInElement from 'katex/contrib/auto-render'
import 'katex/dist/katex.min.css'
import type { GeneratedExercise } from '../api/steps'
import InputExercise from './exercises/InputExercise'
import QcmExercise from './exercises/QcmExercise'
import styles from './CoursContent.module.css'

interface Props {
  markdownHtml: string
  inlineExercises?: GeneratedExercise[]
  onComplete: () => void
}

export default function CoursContent({ markdownHtml, inlineExercises, onComplete }: Props) {
  const mdRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!mdRef.current) return
    renderMathInElement(mdRef.current, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '$', right: '$', display: false },
      ],
      throwOnError: false,
    })
  }, [markdownHtml])

  return (
    <div className={styles.wrap}>
      <div ref={mdRef} className={styles.md} dangerouslySetInnerHTML={{ __html: markdownHtml }} />
      {inlineExercises && inlineExercises.length > 0 && (
        <div className={styles.inlineExos}>
          <h3 className={styles.exosTitle}>Exercices pratiques</h3>
          {inlineExercises.map(ex => <InlineExo key={ex.id} exercise={ex} />)}
        </div>
      )}
      <div className={styles.footer}>
        <button className="btn-primary" onClick={onComplete}>Continuer →</button>
      </div>
    </div>
  )
}

function InlineExo({ exercise }: { exercise: GeneratedExercise }) {
  const [answer, setAnswer] = useState<unknown>('')
  const [revealed, setRevealed] = useState(false)
  const isQcm = exercise.type === 'qcm' || exercise.type === 'multiselect'
    || exercise.renderType === 'qcm' || exercise.renderType === 'multiselect'

  // Comparaison côté client pour input libre
  const isCorrect = (() => {
    if (!revealed || isQcm) return false
    const expected = Array.isArray(exercise.answer) ? exercise.answer[0] : exercise.answer as string
    return String(answer).trim().toLowerCase() === String(expected).trim().toLowerCase()
  })()

  return (
    <div className={styles.inlineExo}>
      {isQcm ? (
        <QcmExercise
          exercise={exercise}
          value={answer as string | string[]}
          onChange={setAnswer}
          readonly={revealed}
        />
      ) : (
        <InputExercise
          exercise={exercise}
          value={answer as string}
          onChange={v => setAnswer(v)}
          readonly={revealed}
          correct={isCorrect}
        />
      )}
      {!revealed && (
        <div className={styles.exoActions}>
          <button className="btn-secondary" onClick={() => setRevealed(true)}>
            Vérifier
          </button>
        </div>
      )}
    </div>
  )
}

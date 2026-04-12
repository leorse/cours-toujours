import { useEffect, useRef, useState } from 'react'
import renderMathInElement from 'katex/contrib/auto-render'
import 'katex/dist/katex.min.css'
import type { GeneratedExercise } from '../api/steps'
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
  const [answer, setAnswer] = useState('')
  const [revealed, setRevealed] = useState(false)

  const check = () => setRevealed(true)
  const expected = Array.isArray(exercise.answer) ? exercise.answer.join(', ') : exercise.answer

  return (
    <div className={styles.inlineExo}>
      <p className={styles.exoQ}>{exercise.question}</p>
      <div className={styles.exoRow}>
        <input
          className={`${styles.exoInput} ${revealed ? styles.revealed : ''}`}
          type="text"
          value={answer}
          onChange={e => setAnswer(e.target.value)}
          disabled={revealed}
          placeholder="Ta réponse..."
        />
        {exercise.unit && <span className={styles.exoUnit}>{exercise.unit}</span>}
        {!revealed && (
          <button className="btn-secondary" onClick={check}>Vérifier</button>
        )}
      </div>
      {revealed && (
        <p className={styles.exoAnswer}>Réponse : <strong>{expected}</strong></p>
      )}
      {revealed && exercise.explanation && (
        <p className={styles.exoExpl}>{exercise.explanation}</p>
      )}
    </div>
  )
}

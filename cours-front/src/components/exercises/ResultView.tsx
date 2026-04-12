import type { GeneratedExercise, StepResult } from '../../api/steps'
import InputExercise from './InputExercise'
import QcmExercise from './QcmExercise'
import styles from './Exercise.module.css'

interface Props {
  result: StepResult
  exercises: GeneratedExercise[]
  answers: Record<string, unknown>
  onNext: () => void
}

export default function ResultView({ result, exercises, answers, onNext }: Props) {
  return (
    <div className={styles.resultWrap}>
      <div className={`${styles.banner} ${result.success ? styles.bannerOk : styles.bannerFail}`}>
        <span className={styles.emoji}>{result.success ? '🎉' : '😅'}</span>
        <div>
          <div className={styles.score}>{result.correctCount}/{result.totalCount}</div>
          <div className={styles.msg}>{result.message}</div>
          {result.xpEarned > 0 && <div className={styles.xp}>+{result.xpEarned} XP</div>}
        </div>
      </div>
      <div className={styles.exList}>
        {exercises.map(ex => {
          const ok = result.answerResults[ex.id]
          const t = ex.type || ex.renderType || 'input'
          return (
            <div key={ex.id} className={`${styles.exCard} ${ok ? styles.cardOk : styles.cardFail}`}>
              <div className={styles.icon}>{ok ? '✅' : '❌'}</div>
              {(t === 'qcm' || t === 'multiselect')
                ? <QcmExercise exercise={ex} value={answers[ex.id] as string | string[]} onChange={() => {}} readonly correct={ok} />
                : <InputExercise exercise={ex} value={answers[ex.id] as string} onChange={() => {}} readonly correct={ok} />}
              {!ok && <div className={styles.correctAns}>Bonne réponse : <strong>{Array.isArray(ex.answer) ? ex.answer.join(', ') : ex.answer as string}</strong></div>}
            </div>
          )
        })}
      </div>
      <div className={styles.footer}>
        <button className="btn-primary" onClick={onNext}>Continuer →</button>
      </div>
    </div>
  )
}

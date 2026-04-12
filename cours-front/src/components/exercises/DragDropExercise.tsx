import { useState } from 'react'
import type { GeneratedExercise } from '../../api/steps'
import styles from './Exercise.module.css'

interface Props {
  exercise: GeneratedExercise
  value: string[]
  onChange: (v: string[]) => void
  readonly?: boolean
}

export default function DragDropExercise({ exercise, value, onChange, readonly }: Props) {
  const [dragging, setDragging] = useState<string | null>(null)
  const placed = value ?? []
  const remaining = (exercise.options ?? []).filter(o => !placed.includes(o))

  const drop = () => { if (!dragging || readonly) return; onChange([...placed, dragging]); setDragging(null) }
  const remove = (opt: string) => { if (readonly) return; onChange(placed.filter(p => p !== opt)) }

  return (
    <div className={styles.ex}>
      <p className={styles.q}>{exercise.question}</p>
      <div className={styles.dropZone} onDragOver={e => e.preventDefault()} onDrop={drop}>
        {!placed.length && <span className={styles.hint}>Glisse ici les éléments dans l'ordre</span>}
        {placed.map((o, i) => <span key={i} className={styles.placed} onClick={() => remove(o)}>{o} {!readonly && '×'}</span>)}
      </div>
      <div className={styles.dragOpts}>
        {remaining.map(o => (
          <span key={o} className={styles.dragItem} draggable={!readonly}
            onDragStart={() => setDragging(o)} onClick={() => !readonly && onChange([...placed, o])}>{o}</span>
        ))}
      </div>
    </div>
  )
}

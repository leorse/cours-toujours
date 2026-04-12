import { useState } from 'react'
import styles from './DialogueView.module.css'

interface Props {
  dialogue: Record<string, unknown>
  characters: Record<string, unknown>
  onComplete: () => void
}

export default function DialogueView({ dialogue, characters, onComplete }: Props) {
  const messages = (dialogue.dialogue as Array<Record<string, unknown>>) ?? []
  const [idx, setIdx] = useState(0)

  if (!messages.length) return <button className="btn-primary" onClick={onComplete}>Continuer →</button>

  const current = messages[idx]
  const isLast = idx >= messages.length - 1
  const next = () => isLast ? onComplete() : setIdx(i => i + 1)

  const charId = current.character as string | undefined
  const char = charId ? (characters[charId] as Record<string, unknown> | undefined) : undefined
  const emotion = current.emotion as string | undefined
  const text = current.page as string ?? ''
  const monoImage = current.image as string | undefined

  return (
    <div className={styles.wrap}>
      {char ? (
        <div className={styles.charArea}>
          <CharSprite char={char} emotion={emotion} />
          <div className={styles.charName}>{char.name as string}</div>
        </div>
      ) : monoImage ? (
        <div className={styles.charArea}>
          <img src={`/images/${monoImage}`} className={styles.monoImg} alt="" />
        </div>
      ) : null}
      <div className={styles.bubble} onClick={next}>
        <p className={styles.text}>{text}</p>
        <span className={styles.cta}>{isLast ? '✓ Fin' : '▶'}</span>
      </div>
      <div className={styles.dots}>
        {messages.map((_, i) => (
          <span key={i} className={`${styles.dot} ${i === idx ? styles.active : ''}`} />
        ))}
      </div>
    </div>
  )
}

function CharSprite({ char, emotion }: { char: Record<string, unknown>; emotion?: string }) {
  const emotions = char.emotions as Record<string, number[]> | undefined
  const sheet = char.spritesheet as string | undefined
  const fw = (char.frameWidth as number) ?? 379
  const fh = (char.frameHeight as number) ?? 379
  const coords = emotion && emotions ? emotions[emotion] : undefined
  const ox = coords ? -coords[0] * fw : 0
  const oy = coords ? -coords[1] * fh : 0
  if (!sheet) return null
  return (
    <div className={styles.sprite} style={{
      width: fw, height: fh,
      backgroundImage: `url(/images/${sheet})`,
      backgroundPosition: `${ox}px ${oy}px`,
    }} />
  )
}

import { useMemo, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import styles from './DialogueView.module.css'

interface Message {
  character?: string
  emotion?: string
  page?: string
  image?: string
}

interface Props {
  dialogue: Record<string, unknown>
  characters: Record<string, unknown>
  onComplete: () => void
}

export default function DialogueView({ dialogue, characters, onComplete }: Props) {
  const messages = (dialogue.dialogue as Message[]) ?? []
  const [idx, setIdx] = useState(0)

  // Détermine l'ordre d'apparition des personnages → le 2ème est à droite (miroir)
  const characterSides = useMemo(() => {
    const sides = new Map<string, 'left' | 'right'>()
    for (const msg of messages) {
      if (msg.character && !sides.has(msg.character)) {
        sides.set(msg.character, sides.size === 0 ? 'left' : 'right')
      }
    }
    return sides
  }, [messages])

  if (!messages.length) return <button className="btn-primary" onClick={onComplete}>Continuer →</button>

  const current = messages[idx]
  const isLast = idx >= messages.length - 1
  const next = () => isLast ? onComplete() : setIdx(i => i + 1)

  const charId = current.character
  const char = charId ? (characters[charId] as Record<string, unknown> | undefined) : undefined
  const emotion = current.emotion
  const text = current.page ?? ''
  const monoImage = current.image
  const side = charId ? (characterSides.get(charId) ?? 'left') : 'left'
  const isRight = side === 'right'

  return (
    <div className={styles.wrap}>
      {/* Personnage spritesheet */}
      {char && (
        <div className={`${styles.charArea} ${isRight ? styles.charRight : styles.charLeft}`}>
          <CharSprite char={char} emotion={emotion} mirrored={isRight} />
          <div className={styles.charName}>{char.name as string}</div>
        </div>
      )}

      {/* Image monologue (pas de spritesheet) */}
      {!char && monoImage && (
        <div className={styles.charArea}>
          <img src={`/images/${monoImage}`} className={styles.monoImg} alt="" />
        </div>
      )}

      {/* Bulle de dialogue */}
      <div className={`${styles.bubble} ${isRight ? styles.bubbleRight : styles.bubbleLeft}`} onClick={next}>
        <div className={styles.text}>
          <ReactMarkdown components={{ p: ({ children }) => <>{children}</> }}>
            {text}
          </ReactMarkdown>
        </div>
        <span className={styles.cta}>{isLast ? '✓ Fin' : '▶'}</span>
      </div>

      {/* Points de progression */}
      <div className={styles.dots}>
        {messages.map((_, i) => (
          <span key={i} className={`${styles.dot} ${i === idx ? styles.active : ''}`} />
        ))}
      </div>
    </div>
  )
}

function CharSprite({ char, emotion, mirrored }: { char: Record<string, unknown>; emotion?: string; mirrored?: boolean }) {
  const emotions = char.emotions as Record<string, number[]> | undefined
  const sheet = char.spritesheet as string | undefined
  const fw = (char.frameWidth as number) || 220
  const fh = (char.frameHeight as number) || 220
  const coords = emotion && emotions ? emotions[emotion] : undefined
  const ox = coords ? -coords[0] * fw : 0
  const oy = coords ? -coords[1] * fh : 0
  if (!sheet) return null
  return (
    <div
      className={styles.sprite}
      style={{
        width: fw,
        height: fh,
        backgroundImage: `url(/images/${sheet})`,
        backgroundPosition: `${ox}px ${oy}px`,
        transform: mirrored ? 'scaleX(-1)' : undefined,
      }}
    />
  )
}

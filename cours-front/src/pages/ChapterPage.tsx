import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getChapter, type StepSummary } from '../api/subjects'
import styles from './ChapterPage.module.css'

const POSITIONS = ['center', 'left', 'center', 'right'] as const

export default function ChapterPage() {
  const { subjectId, chapterId } = useParams<{ subjectId: string; chapterId: string }>()
  const [steps, setSteps] = useState<StepSummary[]>([])
  const [subject, setSubject] = useState<{ id: string; name: string } | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const svgRef = useRef<SVGSVGElement>(null)
  const navigate = useNavigate()

  useEffect(() => {
    if (!subjectId || !chapterId) return
    getChapter(subjectId, chapterId).then(d => { setSubject(d.subject); setSteps(d.steps) })
  }, [subjectId, chapterId])

  useEffect(() => {
    if (!steps.length) return
    const update = () => {
      const container = containerRef.current
      const svg = svgRef.current
      if (!container || !svg) return
      const anchors = container.querySelectorAll<HTMLElement>('.road-anchor')
      if (!anchors.length) return
      let d = ''
      anchors.forEach((el, i) => {
        const r = el.getBoundingClientRect(), cr = container.getBoundingClientRect()
        const x = r.left + r.width / 2 - cr.left, y = r.top + r.height / 2 - cr.top
        if (i === 0) { d += `M ${x} ${y}` } else {
          const pr = anchors[i-1].getBoundingClientRect()
          const px = pr.left + pr.width/2 - cr.left, py = pr.top + pr.height/2 - cr.top
          const cy = (py + y) / 2
          d += ` C ${px} ${cy}, ${x} ${cy}, ${x} ${y}`
        }
      })
      svg.setAttribute('viewBox', `0 0 ${container.offsetWidth} ${container.offsetHeight}`)
      svg.querySelectorAll('path').forEach(p => p.setAttribute('d', d))
    }
    setTimeout(update, 100)
    window.addEventListener('resize', update)
    return () => window.removeEventListener('resize', update)
  }, [steps])

  const isUnlocked = (step: StepSummary, idx: number) =>
    idx === 0 || step.activated || steps[idx - 1]?.completed

  const getIcon = (s: StepSummary) => {
    if (s.completed) return s.mastery >= 3 ? '🏆' : '✅'
    if (s.type === 'cours' || s.type === 'theory') return '📖'
    if (s.type === 'validation') return '🎓'
    if (s.type === 'flash') return '⚡'
    return '🎯'
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <button className="btn-secondary" onClick={() => navigate(`/subjects/${subjectId}`)}>← Retour</button>
        <h1>{subject?.name}</h1>
      </header>
      <div className={styles.road} ref={containerRef}>
        <svg ref={svgRef} className={styles.svg}>
          <path className={styles.asphalt} d="" />
          <path className={styles.line} d="" />
        </svg>
        {steps.map((step, idx) => {
          const pos = POSITIONS[idx % 4]
          const unlocked = isUnlocked(step, idx)
          return (
            <div key={step.id} className={`${styles.wrapper} ${styles[pos]}`}>
              <button
                className={`${styles.node} ${!unlocked ? styles.locked : ''} ${step.completed ? styles.done : ''} ${styles[step.type] || styles.practice}`}
                onClick={() => unlocked && navigate(`/step/${step.id}`)}
                disabled={!unlocked}
              >
                <div className={`${styles.point} road-anchor`}>
                  {step.mastery > 0 && step.mastery < 3 && (
                    <svg className={styles.ring} viewBox="0 0 100 100">
                      <circle cx="50" cy="50" r="46" fill="transparent" stroke="rgba(255,255,255,0.2)" strokeWidth="8"/>
                      <circle cx="50" cy="50" r="46" fill="transparent" stroke="#f1c40f" strokeWidth="8"
                        strokeDasharray={`${step.mastery * 33.3} 100`} strokeDashoffset="0" transform="rotate(-90 50 50)"/>
                    </svg>
                  )}
                  <span>{getIcon(step)}</span>
                </div>
                <div className={styles.signs}>
                  <div className={styles.sign}>{step.title}</div>
                  {step.subtitle && <div className={`${styles.sign} ${styles.sub}`}>{step.subtitle}</div>}
                </div>
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}

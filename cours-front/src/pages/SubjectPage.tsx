import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getSubject, type ChapterSummary } from '../api/subjects'
import styles from './SubjectPage.module.css'

export default function SubjectPage() {
  const { subjectId } = useParams<{ subjectId: string }>()
  const [subject, setSubject] = useState<{ id: string; name: string; image: string } | null>(null)
  const [chapters, setChapters] = useState<ChapterSummary[]>([])
  const navigate = useNavigate()

  useEffect(() => {
    if (!subjectId) return
    getSubject(subjectId).then(d => { setSubject(d.subject); setChapters(d.chapters) })
  }, [subjectId])

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <button className="btn-secondary" onClick={() => navigate('/dashboard')}>← Retour</button>
        <h1>{subject?.name}</h1>
      </header>
      <div className={styles.list}>
        {chapters.map(c => (
          <button key={c.id} className={styles.banner}
            onClick={() => navigate(`/subjects/${subjectId}/chapters/${c.id}`)}>
            {c.icon && <span className={styles.icon}>{c.icon}</span>}
            <span className={styles.chTitle}>{c.title}</span>
            <span className={styles.meta}>{c.completedSteps}/{c.totalSteps}</span>
            <span className={styles.arrow}>›</span>
          </button>
        ))}
      </div>
    </div>
  )
}

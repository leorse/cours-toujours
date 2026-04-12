import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getDashboard, type SubjectSummary } from '../api/dashboard'
import styles from './DashboardPage.module.css'

export default function DashboardPage() {
  const [subjects, setSubjects] = useState<SubjectSummary[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    getDashboard().then(d => setSubjects(d.subjects)).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading">Chargement...</div>

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Mes matières</h1>
      <div className={styles.grid}>
        {subjects.map(s => (
          <button key={s.id} className={styles.card} onClick={() => navigate(`/subjects/${s.id}`)}
            style={s.image ? { '--bg': `url(/images/${s.image})` } as React.CSSProperties : {}}>
            <div className={styles.inner}>
              <h2 className={styles.name}>{s.name}</h2>
              <div className={styles.bar}><div className={styles.fill} style={{ width: `${s.progressPercent}%` }} /></div>
              <span className={styles.stats}>{s.completedSteps}/{s.totalSteps} étapes · {s.xp} XP</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getUsers, login, createUser, type User } from '../api/auth'
import { useUserStore } from '../store/userStore'
import styles from './LoginPage.module.css'

export default function LoginPage() {
  const [users, setUsers] = useState<User[]>([])
  const [showCreate, setShowCreate] = useState(false)
  const [newUsername, setNewUsername] = useState('')
  const [error, setError] = useState('')
  const { setUser, user } = useUserStore()
  const navigate = useNavigate()

  useEffect(() => {
    if (user) { navigate('/dashboard'); return }
    getUsers().then(setUsers).catch(() => setUsers([]))
  }, [user, navigate])

  const handleLogin = async (userId: string) => {
    try { const u = await login(userId); setUser(u); navigate('/dashboard') }
    catch { setError('Connexion échouée') }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newUsername.trim()) return
    try { const u = await createUser(newUsername.trim()); setUser(u); navigate('/dashboard') }
    catch { setError('Ce nom est déjà pris') }
  }

  return (
    <div className={styles.page}>
      <div className={styles.hero}>
        <h1 className={styles.title}>Parcours</h1>
        <p className={styles.subtitle}>Ta plateforme d'apprentissage</p>
      </div>

      {users.length > 0 && (
        <div className={styles.grid}>
          {users.map(u => (
            <button key={u.id} className={styles.card} onClick={() => handleLogin(u.id)}>
              <div className={styles.avatar}>{u.initials}</div>
              <span className={styles.username}>{u.username}</span>
              <span className={styles.xp}>⭐ {u.totalXp} XP</span>
            </button>
          ))}
        </div>
      )}

      {!showCreate ? (
        <button className={styles.newBtn} onClick={() => setShowCreate(true)}>+ Nouveau profil</button>
      ) : (
        <form className={styles.form} onSubmit={handleCreate}>
          <input type="text" placeholder="Ton prénom" value={newUsername}
            onChange={e => setNewUsername(e.target.value)} className={styles.input} autoFocus maxLength={30} />
          <div className={styles.actions}>
            <button type="submit" className="btn-primary">Créer</button>
            <button type="button" className="btn-secondary" onClick={() => setShowCreate(false)}>Annuler</button>
          </div>
          {error && <p className={styles.error}>{error}</p>}
        </form>
      )}
    </div>
  )
}

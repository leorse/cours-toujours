import { Outlet, useNavigate } from 'react-router-dom'
import { useUserStore } from '../store/userStore'
import { logout } from '../api/auth'

export default function Layout() {
  const { user, setUser } = useUserStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    setUser(null)
    navigate('/')
  }

  return (
    <div className="app-wrapper">
      {user && (
        <nav className="top-nav">
          <a href="/dashboard" className="nav-logo">Parcours</a>
          <div className="nav-user">
            <span className="nav-xp">⭐ {user.totalXp} XP</span>
            <span className="nav-avatar">{user.initials}</span>
            <button onClick={handleLogout} className="btn-secondary">Déconnexion</button>
          </div>
        </nav>
      )}
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}

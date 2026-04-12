import { Navigate } from 'react-router-dom'
import { useUserStore } from '../store/userStore'

interface Props { children: React.ReactNode }

export default function ProtectedRoute({ children }: Props) {
  const { user } = useUserStore()
  if (!user) return <Navigate to="/" replace />
  return <>{children}</>
}

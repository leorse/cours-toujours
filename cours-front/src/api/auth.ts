import api from './client'

export interface User {
  id: string
  username: string
  avatar: string
  totalXp: number
  isAdmin: boolean
  initials: string
}

export const getUsers = () => api.get<User[]>('/api/auth/users').then(r => r.data)
export const login = (userId: string) => api.post<User>('/api/auth/login', { userId }).then(r => r.data)
export const logout = () => api.post('/api/auth/logout')
export const getMe = () => api.get<User>('/api/auth/me').then(r => r.data)
export const createUser = (username: string, avatar?: string) =>
  api.post<User>('/api/auth/users', { username, avatar }).then(r => r.data)

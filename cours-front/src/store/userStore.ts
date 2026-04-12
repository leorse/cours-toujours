import { create } from 'zustand'
import type { User } from '../api/auth'

interface UserState {
  user: User | null
  setUser: (user: User | null) => void
  isLoggedIn: () => boolean
}

export const useUserStore = create<UserState>((set, get) => ({
  user: null,
  setUser: (user) => set({ user }),
  isLoggedIn: () => get().user !== null,
}))

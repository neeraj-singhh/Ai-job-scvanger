import { create } from 'zustand'
import { persist, StateStorage, createJSONStorage } from 'zustand/middleware'

interface AuthState {
  token: string | null
  setToken: (token: string | null) => void
  isAuthenticated: () => boolean
}


const electronStorage: StateStorage = {
  getItem: async (name: string): Promise<string | null> => {
    if (window.electron && window.electron.secureGet) {
      return await window.electron.secureGet(name)
    }
    return null
  },
  setItem: async (name: string, value: string): Promise<void> => {
    if (window.electron && window.electron.secureSet) {
      await window.electron.secureSet(name, value)
    }
  },
  removeItem: async (name: string): Promise<void> => {
    if (window.electron && window.electron.secureDelete) {
      await window.electron.secureDelete(name)
    }
  },
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      setToken: (token) => set({ token }),
      isAuthenticated: () => !!get().token,
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => electronStorage),
    }
  )
)

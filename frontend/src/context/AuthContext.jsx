import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('rassay_token'))
  const [user, setUser] = useState(() => {
    try {
      const s = localStorage.getItem('rassay_user')
      return s ? JSON.parse(s) : null
    } catch {
      return null
    }
  })

  function storeSession(accessToken, userData) {
    localStorage.setItem('rassay_token', accessToken)
    localStorage.setItem('rassay_user', JSON.stringify(userData))
    setToken(accessToken)
    setUser(userData)
  }

  function clearSession() {
    localStorage.removeItem('rassay_token')
    localStorage.removeItem('rassay_user')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ token, user, storeSession, clearSession }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}

import React, { createContext, useContext, useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Setup from './pages/Setup'
import Research from './pages/Research'
import History from './pages/History'
import type { AppContextType, SharedContext } from './types'

export const AppContext = createContext<AppContextType | null>(null)

export function useApp(): AppContextType {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useApp must be used within AppContext.Provider')
  return ctx
}

export default function App() {
  const [apiKey, setApiKey] = useState<string>(() => localStorage.getItem('mck_api_key') || '')
  const [theme, setTheme] = useState<string>(() => localStorage.getItem('mck_theme') || 'mckinsey-dark')
  const [sessionId, setSessionId] = useState<string | null>(() => localStorage.getItem('mck_session_id') || null)
  const [sharedContext, setSharedContext] = useState<Partial<SharedContext>>(() => {
    try {
      return JSON.parse(localStorage.getItem('mck_shared_context') || '{}') as Partial<SharedContext>
    } catch {
      return {}
    }
  })

  // Apply theme to <html> element
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('mck_theme', theme)
  }, [theme])

  useEffect(() => {
    if (apiKey) localStorage.setItem('mck_api_key', apiKey)
    else localStorage.removeItem('mck_api_key')
  }, [apiKey])

  useEffect(() => {
    if (sessionId) localStorage.setItem('mck_session_id', sessionId)
    else localStorage.removeItem('mck_session_id')
  }, [sessionId])

  useEffect(() => {
    localStorage.setItem('mck_shared_context', JSON.stringify(sharedContext))
  }, [sharedContext])

  const ctx: AppContextType = {
    apiKey,
    setApiKey,
    theme,
    setTheme,
    sessionId,
    setSessionId,
    sharedContext,
    setSharedContext,
  }

  return (
    <AppContext.Provider value={ctx}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to={apiKey ? '/research' : '/setup'} replace />} />
          <Route path="/setup" element={<Setup />} />
          <Route path="/research" element={apiKey ? <Research /> : <Navigate to="/setup" replace />} />
          <Route path="/history" element={apiKey ? <History /> : <Navigate to="/setup" replace />} />
        </Routes>
      </BrowserRouter>
    </AppContext.Provider>
  )
}

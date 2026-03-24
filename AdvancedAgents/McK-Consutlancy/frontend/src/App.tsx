import React, { createContext, useContext, useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Setup from './pages/Setup'
import Research from './pages/Research'
import History from './pages/History'
import BusinessCasePage from './pages/BusinessCase'
import type { AppContextType, SharedContext, BusinessCase } from './types'

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
  const [businessCase, setBusinessCase] = useState<BusinessCase | null>(() => {
    try {
      return JSON.parse(localStorage.getItem('mck_business_case') || 'null') as BusinessCase | null
    } catch {
      return null
    }
  })
  const [enrichPromptsWithBusinessCase, setEnrichPromptsWithBusinessCase] = useState<boolean>(
    () => localStorage.getItem('mck_bc_enrich') === 'true'
  )

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

  useEffect(() => {
    if (businessCase) localStorage.setItem('mck_business_case', JSON.stringify(businessCase))
    else localStorage.removeItem('mck_business_case')
  }, [businessCase])

  useEffect(() => {
    localStorage.setItem('mck_bc_enrich', String(enrichPromptsWithBusinessCase))
  }, [enrichPromptsWithBusinessCase])

  const ctx: AppContextType = {
    apiKey,
    setApiKey,
    theme,
    setTheme,
    sessionId,
    setSessionId,
    sharedContext,
    setSharedContext,
    businessCase,
    setBusinessCase,
    enrichPromptsWithBusinessCase,
    setEnrichPromptsWithBusinessCase,
  }

  return (
    <AppContext.Provider value={ctx}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to={apiKey ? '/research' : '/setup'} replace />} />
          <Route path="/setup" element={<Setup />} />
          <Route path="/research" element={apiKey ? <Research /> : <Navigate to="/setup" replace />} />
          <Route path="/history" element={apiKey ? <History /> : <Navigate to="/setup" replace />} />
          <Route path="/business-case" element={apiKey ? <BusinessCasePage /> : <Navigate to="/setup" replace />} />
        </Routes>
      </BrowserRouter>
    </AppContext.Provider>
  )
}

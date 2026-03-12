import { useState, useEffect, useCallback } from 'react'
import { fetchSession, updateSession, createSession } from '../lib/api'
import type { Session, StoredAnalysis, SharedContext } from '../types'

/**
 * Manages the active session — loads it from backend and keeps analyses in sync.
 */
export function useSession(
  sessionId: string | null,
  setSessionId: (id: string | null) => void
) {
  const [session, setSession] = useState<Session | null>(null)
  const [analyses, setAnalyses] = useState<Record<string, StoredAnalysis>>({})
  const [loading, setLoading] = useState<boolean>(false)

  const load = useCallback(async (id: string) => {
    if (!id) return
    setLoading(true)
    try {
      const data = await fetchSession(id)
      setSession(data)
      // Build map from prompt_id → latest analysis
      const map: Record<string, StoredAnalysis> = {}
      for (const a of (data.analyses || [])) {
        map[a.prompt_id] = a
      }
      setAnalyses(map)
    } catch (err) {
      console.error('Failed to load session:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (sessionId) load(sessionId)
  }, [sessionId, load])

  const addAnalysis = useCallback((promptId: string, analysis: StoredAnalysis) => {
    setAnalyses(prev => ({ ...prev, [promptId]: analysis }))
  }, [])

  const ensureSession = useCallback(async (
    sharedContext: Partial<SharedContext>,
    theme = 'mckinsey-dark'
  ): Promise<string> => {
    if (sessionId) return sessionId
    // Create a new session with a default name from business_name
    const name = sharedContext?.business_name
      ? `${sharedContext.business_name} — Research`
      : `Research Session ${new Date().toLocaleDateString()}`
    const created = await createSession({ name, shared_context: sharedContext, theme })
    setSessionId(created.id)
    return created.id
  }, [sessionId, setSessionId])

  const syncContext = useCallback(async (sharedContext: Partial<SharedContext>) => {
    if (!sessionId) return
    try {
      await updateSession(sessionId, { shared_context: sharedContext as SharedContext })
    } catch (err) {
      console.error('Failed to sync context:', err)
    }
  }, [sessionId])

  return { session, analyses, loading, load, addAnalysis, ensureSession, syncContext }
}

import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../App'
import { useSession } from '../hooks/useSession'
import { fetchPrompts } from '../lib/api'
import Sidebar from '../components/Sidebar'
import SharedContextPanel from '../components/SharedContextPanel'
import AnalysisTab from '../components/AnalysisTab'
import CostTracker from '../components/CostTracker'
import ExportModal from '../components/ExportModal'
import type { Prompt, StoredAnalysis, SharedContext } from '../types'

export default function Research() {
  const { apiKey, sessionId, setSessionId, sharedContext, theme: _theme } = useApp()
  const navigate = useNavigate()

  const [prompts, setPrompts] = useState<Prompt[]>([])
  const [activePromptId, setActivePromptId] = useState<string | null>(null)
  const [showExport, setShowExport] = useState<boolean>(false)
  const [sessionName, setSessionName] = useState<string>('')

  const { session, analyses, loading: _loading, addAnalysis, ensureSession, syncContext } = useSession(
    sessionId,
    setSessionId
  )

  // Load prompts on mount
  useEffect(() => {
    fetchPrompts()
      .then(data => {
        const sorted = [...data].sort((a, b) => a.order - b.order)
        setPrompts(sorted)
        if (sorted.length > 0 && !activePromptId) {
          setActivePromptId(sorted[0].id)
        }
      })
      .catch(console.error)
  }, [])

  const completedIds = Object.keys(analyses)
  const activePrompt = prompts.find(p => p.id === activePromptId)

  // Enrich active prompt with existing analysis data
  const enrichedPrompt: Prompt | null = activePrompt
    ? {
        ...activePrompt,
        existingOutput: analyses[activePrompt.id]?.output || '',
        existingMeta: analyses[activePrompt.id]
          ? {
              from_cache: analyses[activePrompt.id].from_cache,
              input_tokens: analyses[activePrompt.id].input_tokens,
              output_tokens: analyses[activePrompt.id].output_tokens,
              cost_usd: analyses[activePrompt.id].cost_usd,
            }
          : null,
      }
    : null

  async function handleContextSave(ctx: Partial<SharedContext>) {
    await ensureSession(ctx, _theme)
    await syncContext(ctx)
  }

  async function handleAnalysisComplete(promptId: string, analysisData: StoredAnalysis) {
    addAnalysis(promptId, analysisData)

    // Ensure session exists
    await ensureSession(sharedContext, _theme)

    // Update session name from business name if not set
    if (!sessionId || !session?.name) {
      const name = sharedContext?.business_name
        ? `${sharedContext.business_name} — Research`
        : `Research ${new Date().toLocaleDateString()}`
      setSessionName(name)
    }
  }

  if (!apiKey) {
    navigate('/setup')
    return null
  }

  return (
    <div style={{ display: 'flex', height: '100vh', background: 'var(--bg-primary)' }}>
      {/* Sidebar */}
      <Sidebar
        prompts={prompts}
        activePromptId={activePromptId}
        onSelectPrompt={setActivePromptId}
        completedIds={completedIds}
      />

      {/* Main content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Top bar */}
        <div style={{
          height: '52px',
          background: 'var(--bg-secondary)',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          padding: '0 20px',
          gap: '12px',
          flexShrink: 0,
        }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', flex: 1 }}>
            {session?.name || sharedContext?.business_name
              ? `📁 ${session?.name || sharedContext.business_name}`
              : '📁 New Research Session'}
          </span>

          <button
            className="theme-btn-secondary"
            onClick={() => navigate('/history')}
            style={{ fontSize: '12px', padding: '5px 10px' }}
          >
            History
          </button>

          <button
            className="theme-btn-secondary"
            onClick={() => navigate('/setup')}
            style={{ fontSize: '12px', padding: '5px 10px' }}
          >
            Settings
          </button>

          {completedIds.length > 0 && (
            <button
              className="theme-btn-primary"
              onClick={() => setShowExport(true)}
              style={{ fontSize: '12px', padding: '6px 14px' }}
            >
              Export Report
            </button>
          )}
        </div>

        {/* Content area */}
        <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
          {/* Left: analysis content */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '20px 24px' }}>
            <SharedContextPanel onSave={handleContextSave} />

            {enrichedPrompt && (
              <AnalysisTab
                key={activePromptId ?? undefined}
                prompt={enrichedPrompt}
                sessionId={sessionId}
                onComplete={handleAnalysisComplete}
              />
            )}
          </div>

          {/* Right: cost tracker */}
          <div style={{
            width: '220px',
            borderLeft: '1px solid var(--border-color)',
            padding: '16px',
            overflowY: 'auto',
            flexShrink: 0,
          }}>
            <CostTracker analyses={analyses} />

            {completedIds.length > 0 && (
              <div style={{ marginTop: '12px' }}>
                <div style={{
                  fontSize: '11px',
                  fontWeight: 700,
                  color: 'var(--text-muted)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.08em',
                  marginBottom: '8px',
                }}>
                  Completed
                </div>
                {prompts
                  .filter(p => completedIds.includes(p.id))
                  .map(p => (
                    <button
                      key={p.id}
                      onClick={() => setActivePromptId(p.id)}
                      style={{
                        width: '100%',
                        textAlign: 'left',
                        padding: '5px 8px',
                        borderRadius: '4px',
                        background: activePromptId === p.id ? 'var(--bg-hover)' : 'transparent',
                        border: 'none',
                        color: 'var(--text-secondary)',
                        cursor: 'pointer',
                        fontSize: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                      }}
                    >
                      <span style={{ color: 'var(--badge-complete-text)' }}>✓</span>
                      {p.short_name || p.title}
                    </button>
                  ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {showExport && (
        <ExportModal
          sessionId={sessionId}
          prompts={prompts}
          completedIds={completedIds}
          onClose={() => setShowExport(false)}
        />
      )}
    </div>
  )
}

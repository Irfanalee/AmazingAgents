import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../App'
import { useSession } from '../hooks/useSession'
import { fetchPrompts, runBatchAnalysis, updateSession } from '../lib/api'
import Sidebar from '../components/Sidebar'
import SharedContextPanel from '../components/SharedContextPanel'
import AnalysisTab from '../components/AnalysisTab'
import CostTracker from '../components/CostTracker'
import ExportModal from '../components/ExportModal'
import type { Prompt, StoredAnalysis, SharedContext } from '../types'

export default function Research() {
  const { apiKey, sessionId, setSessionId, sharedContext, setSharedContext, theme: _theme } = useApp()
  const navigate = useNavigate()

  const [prompts, setPrompts] = useState<Prompt[]>([])
  const [activePromptId, setActivePromptId] = useState<string | null>(null)
  const [showExport, setShowExport] = useState<boolean>(false)
  const [sessionName, setSessionName] = useState<string>('')
  const [batchRunning, setBatchRunning] = useState(false)
  const [batchMsg, setBatchMsg] = useState('')
  const [batchErrors, setBatchErrors] = useState<{ prompt_id: string; error: string }[]>([])

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

  // Detect when the user has typed a different company name on an existing session
  const sessionBusinessName = (session?.shared_context as Partial<SharedContext> | undefined)?.business_name
  const currentBusinessName = sharedContext?.business_name
  const companyChanged =
    !!sessionId &&
    completedIds.length > 0 &&
    !!sessionBusinessName &&
    !!currentBusinessName &&
    currentBusinessName.trim().toLowerCase() !== sessionBusinessName.trim().toLowerCase()

  // Enrich each prompt with its existing analysis data
  function enrichPrompt(p: Prompt): Prompt {
    return {
      ...p,
      existingOutput: analyses[p.id]?.output || '',
      existingMeta: analyses[p.id]
        ? {
            from_cache: analyses[p.id].from_cache,
            input_tokens: analyses[p.id].input_tokens,
            output_tokens: analyses[p.id].output_tokens,
            cost_usd: analyses[p.id].cost_usd,
            analysis_id: analyses[p.id].analysis_id,
          }
        : null,
    }
  }

  async function handleContextSave(ctx: Partial<SharedContext>) {
    await ensureSession(ctx, _theme)
    await syncContext(ctx)
  }

  async function handleNewResearch() {
    // Persist current session name if it was derived from business name
    if (sessionId && sharedContext?.business_name) {
      try {
        await updateSession(sessionId, {
          name: `${sharedContext.business_name} — Research`,
          shared_context: sharedContext as SharedContext,
        })
      } catch {
        // session save failed — still proceed with fresh start
      }
    }
    // Clear active session and context → fresh slate
    setSessionId(null)
    setSharedContext({})
  }

  async function handlePreFillAll() {
    if (!apiKey || batchRunning) return
    setBatchRunning(true)
    setBatchMsg('Running all 12 analyses with Haiku…')
    setBatchErrors([])
    try {
      const sid = await ensureSession(sharedContext, _theme)
      const { results, errors } = await runBatchAnalysis(apiKey, {
        shared_context: sharedContext,
        model: 'claude-haiku-4-5-20251001',
        session_id: sid,
      })
      for (const r of results) {
        if (!r.error && r.output) {
          addAnalysis(r.prompt_id, {
            prompt_id: r.prompt_id,
            output: r.output,
            from_cache: r.from_cache ?? false,
            input_tokens: r.input_tokens,
            output_tokens: r.output_tokens,
            cost_usd: r.cost_usd,
            analysis_id: r.analysis_id,
          })
        }
      }
      if (errors.length > 0) {
        setBatchMsg(`${results.length - errors.length}/${results.length} complete — ${errors.length} failed`)
        setBatchErrors(errors.map(e => ({ prompt_id: e.prompt_id, error: e.error ?? 'Unknown error' })))
      } else {
        setBatchMsg(`All ${results.length} analyses complete ✓`)
      }
    } catch (e) {
      setBatchMsg('Batch failed')
      setBatchErrors([{ prompt_id: 'all', error: e instanceof Error ? e.message : String(e) }])
    } finally {
      setBatchRunning(false)
    }
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
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {session?.name || sharedContext?.business_name
              ? `📁 ${session?.name || sharedContext.business_name}`
              : '📁 New Research Session'}
          </span>

          <button
            className="theme-btn-secondary"
            onClick={handleNewResearch}
            title="Save current session and start a fresh research"
            style={{ fontSize: '12px', padding: '5px 12px', display: 'flex', alignItems: 'center', gap: '5px' }}
          >
            ＋ New Research
          </button>

          <button
            className={batchRunning ? 'theme-btn-secondary' : 'theme-btn-primary'}
            onClick={handlePreFillAll}
            disabled={batchRunning || !sharedContext?.business_name}
            style={{ fontSize: '12px', padding: '6px 14px' }}
          >
            {batchRunning ? '⏳ Pre-filling…' : '⚡ Pre-fill All'}
          </button>
          {batchMsg && (
            <span style={{ fontSize: '11px', color: batchErrors.length > 0 ? '#fca5a5' : 'var(--text-muted)' }}>
              {batchMsg}
            </span>
          )}

          <button
            className="theme-btn-secondary"
            onClick={() => navigate('/history')}
            style={{ fontSize: '12px', padding: '5px 10px' }}
          >
            📚 Library
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

        {/* Batch error banner */}
        {batchErrors.length > 0 && (
          <div style={{
            background: 'color-mix(in srgb, #ef4444 10%, var(--bg-secondary))',
            borderBottom: '1px solid color-mix(in srgb, #ef4444 30%, transparent)',
            padding: '10px 20px',
            flexShrink: 0,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
              <span style={{ fontSize: '13px', fontWeight: 600, color: '#fca5a5' }}>
                ⚠️ {batchErrors.length} framework{batchErrors.length > 1 ? 's' : ''} failed to generate
              </span>
              <button
                onClick={() => setBatchErrors([])}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#fca5a5', fontSize: '16px', lineHeight: 1, marginLeft: 'auto' }}
              >
                ×
              </button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              {batchErrors.map((e, i) => {
                const promptName = prompts.find(p => p.id === e.prompt_id)?.title || e.prompt_id
                return (
                  <div key={i} style={{ display: 'flex', gap: '10px', fontSize: '12px' }}>
                    <span
                      style={{ color: '#fca5a5', fontWeight: 600, cursor: 'pointer', textDecoration: 'underline', flexShrink: 0 }}
                      onClick={() => setActivePromptId(e.prompt_id)}
                    >
                      {promptName}
                    </span>
                    <span style={{ color: '#f87171', opacity: 0.85 }}>{e.error}</span>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Content area */}
        <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
          {/* Left: analysis content */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '20px 24px' }}>
            {/* Company-changed banner */}
            {companyChanged && (
              <div style={{
                background: 'color-mix(in srgb, #f59e0b 12%, var(--bg-card))',
                border: '1px solid color-mix(in srgb, #f59e0b 40%, transparent)',
                borderRadius: '8px',
                padding: '10px 16px',
                marginBottom: '12px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                fontSize: '13px',
                color: '#fcd34d',
              }}>
                <span>⚠️</span>
                <span style={{ flex: 1 }}>
                  This looks like a different company from the current session (<strong>{sessionBusinessName}</strong>).
                </span>
                <button
                  className="theme-btn-primary"
                  onClick={handleNewResearch}
                  style={{ fontSize: '12px', padding: '5px 12px', flexShrink: 0 }}
                >
                  Start New Research
                </button>
                <button
                  onClick={() => setSharedContext(prev => ({ ...prev, business_name: sessionBusinessName ?? '' }))}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#fcd34d', fontSize: '18px', lineHeight: 1, padding: '0 2px' }}
                  title="Dismiss"
                >
                  ×
                </button>
              </div>
            )}

            <SharedContextPanel onSave={handleContextSave} />

            {/* Render all tabs but only show the active one — keeps hooks/streams alive on tab switch */}
            {prompts.map(p => (
              <div key={p.id} style={{ display: p.id === activePromptId ? 'block' : 'none' }}>
                <AnalysisTab
                  prompt={enrichPrompt(p)}
                  sessionId={sessionId}
                  onComplete={handleAnalysisComplete}
                />
              </div>
            ))}
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

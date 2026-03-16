import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../App'
import { fetchSessions, deleteSession, fetchPrompts, exportReport } from '../lib/api'
import { formatDate, formatCost } from '../lib/utils'
import type { Session, Prompt } from '../types'

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export default function History() {
  const navigate = useNavigate()
  const { apiKey, setSessionId, setSharedContext } = useApp()
  const [sessions, setSessions] = useState<Session[]>([])
  const [prompts, setPrompts] = useState<Prompt[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [search, setSearch] = useState<string>('')
  const [deleting, setDeleting] = useState<string | null>(null)
  const [exporting, setExporting] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([fetchSessions(), fetchPrompts()])
      .then(([s, p]) => {
        setSessions(s)
        setPrompts(p.sort((a, b) => a.order - b.order))
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  function handleOpen(session: Session) {
    setSessionId(session.id)
    if (session.shared_context) setSharedContext(session.shared_context)
    navigate('/research')
  }

  function handleNewResearch() {
    setSessionId(null)
    setSharedContext({})
    navigate('/research')
  }

  async function handleDelete(sessionId: string, name: string) {
    if (!confirm(`Delete "${name}" and all its analyses? This cannot be undone.`)) return
    setDeleting(sessionId)
    try {
      await deleteSession(sessionId)
      setSessions(prev => prev.filter(s => s.id !== sessionId))
    } catch {
      alert('Failed to delete session')
    } finally {
      setDeleting(null)
    }
  }

  async function handleExport(session: Session, format: 'docx' | 'pdf') {
    setExporting(session.id + format)
    try {
      const res = await exportReport(apiKey, {
        session_id: session.id,
        format,
        selected_analyses: session.completed_prompts,
      })
      const safeName = session.name.replace(/[^a-z0-9 _-]/gi, '').trim().slice(0, 40) || 'report'
      downloadBlob(res.data as Blob, `${safeName}.${format}`)
    } catch {
      alert('Export failed — make sure the session has analyses.')
    } finally {
      setExporting(null)
    }
  }

  const filtered = sessions.filter(s => {
    if (!search.trim()) return true
    const q = search.toLowerCase()
    return (
      s.name.toLowerCase().includes(q) ||
      (s.shared_context?.industry || '').toLowerCase().includes(q) ||
      (s.shared_context?.business_name || '').toLowerCase().includes(q) ||
      (s.shared_context?.stage || '').toLowerCase().includes(q)
    )
  })

  // Map prompt id → short_name for the completion grid
  const promptMap = Object.fromEntries(prompts.map(p => [p.id, p.short_name || p.title]))

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      {/* Header */}
      <div style={{
        background: 'var(--bg-secondary)',
        borderBottom: '1px solid var(--border-color)',
        padding: '0 24px',
        height: '56px',
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
      }}>
        <button
          onClick={() => navigate('/research')}
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)', fontSize: '20px', lineHeight: 1, padding: '4px 6px' }}
        >
          ←
        </button>
        <div>
          <span style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)' }}>
            Research Library
          </span>
        </div>
        <div style={{ flex: 1 }} />

        {/* Search */}
        <input
          className="theme-input"
          type="text"
          placeholder="Search by company, industry…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ width: '240px', fontSize: '13px', padding: '6px 12px' }}
        />

        <button className="theme-btn-primary" onClick={handleNewResearch} style={{ fontSize: '13px', padding: '7px 16px', flexShrink: 0 }}>
          ＋ New Research
        </button>
      </div>

      {/* Content */}
      <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '28px 20px' }}>
        {loading ? (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '80px' }}>
            <div className="spinner" style={{ margin: '0 auto 16px' }} />
            Loading library…
          </div>
        ) : filtered.length === 0 ? (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '80px 20px' }}>
            {sessions.length === 0 ? (
              <>
                <div style={{ fontSize: '52px', marginBottom: '16px' }}>📚</div>
                <div style={{ fontSize: '20px', fontWeight: 600, marginBottom: '8px', color: 'var(--text-secondary)' }}>
                  Your library is empty
                </div>
                <p style={{ fontSize: '14px', margin: '0 0 24px' }}>
                  Run your first strategic analysis to see it here.
                </p>
                <button className="theme-btn-primary" onClick={handleNewResearch}>
                  Start Research
                </button>
              </>
            ) : (
              <>
                <div style={{ fontSize: '36px', marginBottom: '12px' }}>🔍</div>
                <div style={{ fontSize: '16px', color: 'var(--text-secondary)' }}>No results for "{search}"</div>
              </>
            )}
          </div>
        ) : (
          <>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>
              {filtered.length} {filtered.length === 1 ? 'session' : 'sessions'}
              {search && ` matching "${search}"`}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {filtered.map(session => (
                <SessionCard
                  key={session.id}
                  session={session}
                  promptMap={promptMap}
                  allPrompts={prompts}
                  deleting={deleting === session.id}
                  exporting={exporting}
                  onOpen={() => handleOpen(session)}
                  onDelete={() => handleDelete(session.id, session.name)}
                  onExport={(fmt) => handleExport(session, fmt)}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

// ── Session card ──────────────────────────────────────────────────────────────

interface SessionCardProps {
  session: Session
  promptMap: Record<string, string>
  allPrompts: Prompt[]
  deleting: boolean
  exporting: string | null
  onOpen: () => void
  onDelete: () => void
  onExport: (fmt: 'docx' | 'pdf') => void
}

function SessionCard({ session, promptMap, allPrompts, deleting, exporting, onOpen, onDelete, onExport }: SessionCardProps) {
  const [showExportMenu, setShowExportMenu] = useState(false)
  const ctx = session.shared_context
  const completedSet = new Set(session.completed_prompts || [])
  const initials = (ctx?.business_name || session.name || '?')
    .split(' ')
    .slice(0, 2)
    .map(w => w[0]?.toUpperCase() || '')
    .join('')

  const stageColor: Record<string, string> = {
    'Idea': '#a78bfa', 'MVP': '#60a5fa', 'Early Traction': '#34d399',
    'Growth': '#fbbf24', 'Scale': '#f97316', 'Enterprise': '#f43f5e',
  }

  return (
    <div
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '12px',
        overflow: 'hidden',
        transition: 'border-color 0.15s, box-shadow 0.15s',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.borderColor = 'var(--accent-primary)'
        e.currentTarget.style.boxShadow = '0 2px 12px rgba(0,0,0,0.15)'
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = 'var(--border-color)'
        e.currentTarget.style.boxShadow = 'none'
      }}
    >
      {/* Card body */}
      <div style={{ padding: '18px 20px', display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
        {/* Avatar */}
        <div style={{
          width: '44px',
          height: '44px',
          borderRadius: '10px',
          background: 'var(--accent-primary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '16px',
          fontWeight: 700,
          color: '#fff',
          flexShrink: 0,
        }}>
          {initials || '?'}
        </div>

        {/* Info */}
        <div style={{ flex: 1, minWidth: 0 }}>
          {/* Title row */}
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px', marginBottom: '6px', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)' }}>
              {ctx?.business_name || session.name}
            </span>
            {ctx?.stage && (
              <span style={{
                fontSize: '10px',
                fontWeight: 700,
                padding: '2px 8px',
                borderRadius: '20px',
                background: `color-mix(in srgb, ${stageColor[ctx.stage] || '#94a3b8'} 18%, transparent)`,
                color: stageColor[ctx.stage] || '#94a3b8',
                border: `1px solid color-mix(in srgb, ${stageColor[ctx.stage] || '#94a3b8'} 35%, transparent)`,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}>
                {ctx.stage}
              </span>
            )}
          </div>

          {/* Meta row */}
          <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap', fontSize: '12px', color: 'var(--text-muted)', marginBottom: '12px' }}>
            {ctx?.industry && <span>🏭 {ctx.industry}</span>}
            {ctx?.geography && <span>🌍 {ctx.geography}</span>}
            <span>🗓 {formatDate(session.updated_at || session.created_at)}</span>
            {session.total_cost_usd > 0 && <span>💰 {formatCost(session.total_cost_usd)}</span>}
            <span style={{ color: completedSet.size > 0 ? 'var(--badge-complete-text)' : 'var(--text-muted)' }}>
              ✓ {completedSet.size} / {allPrompts.length} frameworks
            </span>
          </div>

          {/* Framework completion grid */}
          {allPrompts.length > 0 && (
            <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
              {allPrompts.map(p => (
                <span
                  key={p.id}
                  title={p.title}
                  style={{
                    fontSize: '10px',
                    padding: '2px 7px',
                    borderRadius: '4px',
                    background: completedSet.has(p.id)
                      ? 'var(--badge-complete-bg)'
                      : 'var(--bg-secondary)',
                    color: completedSet.has(p.id)
                      ? 'var(--badge-complete-text)'
                      : 'var(--text-muted)',
                    border: `1px solid ${completedSet.has(p.id) ? 'transparent' : 'var(--border-color)'}`,
                    transition: 'all 0.1s',
                  }}
                >
                  {completedSet.has(p.id) ? '✓ ' : ''}{promptMap[p.id] || p.id}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Actions */}
        <div style={{ display: 'flex', gap: '8px', flexShrink: 0, alignItems: 'flex-start' }}>
          <button
            className="theme-btn-primary"
            onClick={onOpen}
            style={{ padding: '8px 18px', fontSize: '13px', fontWeight: 600 }}
          >
            Open →
          </button>

          {/* Export dropdown */}
          {completedSet.size > 0 && (
            <div style={{ position: 'relative' }}>
              <button
                className="theme-btn-secondary"
                onClick={() => setShowExportMenu(m => !m)}
                disabled={!!exporting}
                style={{ padding: '8px 10px', fontSize: '13px' }}
                title="Export report"
              >
                {exporting?.startsWith(session.id) ? '…' : '⬇'}
              </button>
              {showExportMenu && (
                <>
                  {/* backdrop to close */}
                  <div
                    style={{ position: 'fixed', inset: 0, zIndex: 10 }}
                    onClick={() => setShowExportMenu(false)}
                  />
                  <div style={{
                    position: 'absolute',
                    right: 0,
                    top: '100%',
                    marginTop: '4px',
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '8px',
                    padding: '6px',
                    zIndex: 20,
                    minWidth: '140px',
                    boxShadow: '0 4px 16px rgba(0,0,0,0.2)',
                  }}>
                    <button
                      style={{ width: '100%', textAlign: 'left', padding: '7px 12px', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)', fontSize: '13px', borderRadius: '4px' }}
                      onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-hover)'}
                      onMouseLeave={e => e.currentTarget.style.background = 'none'}
                      onClick={() => { setShowExportMenu(false); onExport('docx') }}
                    >
                      📄 Export DOCX
                    </button>
                    <button
                      style={{ width: '100%', textAlign: 'left', padding: '7px 12px', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)', fontSize: '13px', borderRadius: '4px' }}
                      onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-hover)'}
                      onMouseLeave={e => e.currentTarget.style.background = 'none'}
                      onClick={() => { setShowExportMenu(false); onExport('pdf') }}
                    >
                      📑 Export PDF
                    </button>
                  </div>
                </>
              )}
            </div>
          )}

          <button
            className="theme-btn-secondary"
            onClick={onDelete}
            disabled={deleting}
            style={{ padding: '8px 10px', fontSize: '13px', color: '#ef4444' }}
            title="Delete session"
          >
            {deleting ? '…' : '🗑'}
          </button>
        </div>
      </div>
    </div>
  )
}

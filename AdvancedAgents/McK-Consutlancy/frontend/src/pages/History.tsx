import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../App'
import { fetchSessions, deleteSession } from '../lib/api'
import { formatDateTime, formatCost } from '../lib/utils'
import type { Session } from '../types'

export default function History() {
  const navigate = useNavigate()
  const { setSessionId, setSharedContext } = useApp()
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [deleting, setDeleting] = useState<string | null>(null)

  useEffect(() => {
    fetchSessions()
      .then(setSessions)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  async function handleResume(session: Session) {
    setSessionId(session.id)
    if (session.shared_context) {
      setSharedContext(session.shared_context)
    }
    navigate('/research')
  }

  async function handleDelete(sessionId: string) {
    if (!confirm('Delete this session and all its analyses?')) return
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

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      {/* Header */}
      <div style={{
        background: 'var(--bg-secondary)',
        borderBottom: '1px solid var(--border-color)',
        padding: '16px 24px',
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
      }}>
        <button
          onClick={() => navigate('/research')}
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)', fontSize: '18px' }}
        >
          ←
        </button>
        <div>
          <h1 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
            Research History
          </h1>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', margin: 0 }}>
            {sessions.length} saved session{sessions.length !== 1 ? 's' : ''}
          </p>
        </div>
        <div style={{ flex: 1 }} />
        <button
          className="theme-btn-primary"
          onClick={() => {
            setSessionId(null)
            navigate('/research')
          }}
        >
          + New Session
        </button>
      </div>

      {/* Content */}
      <div style={{ maxWidth: '900px', margin: '0 auto', padding: '24px 20px' }}>
        {loading ? (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '60px' }}>
            <div className="spinner" style={{ margin: '0 auto 12px' }} />
            Loading sessions…
          </div>
        ) : sessions.length === 0 ? (
          <div style={{
            textAlign: 'center',
            color: 'var(--text-muted)',
            padding: '80px 20px',
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>📂</div>
            <div style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>No sessions yet</div>
            <p style={{ fontSize: '14px', margin: '0 0 20px' }}>
              Start your first research session to see it here.
            </p>
            <button
              className="theme-btn-primary"
              onClick={() => navigate('/research')}
            >
              Start Research
            </button>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {sessions.map(session => (
              <div
                key={session.id}
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '10px',
                  padding: '18px 20px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  transition: 'border-color 0.15s',
                }}
                onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--accent-primary)'}
                onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border-color)'}
              >
                {/* Session info */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
                    {session.name}
                  </div>
                  <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap', fontSize: '12px', color: 'var(--text-muted)' }}>
                    <span>{formatDateTime(session.updated_at || session.created_at)}</span>
                    <span>
                      <span style={{ color: 'var(--badge-complete-text)', fontWeight: 600 }}>
                        {session.analysis_count}
                      </span> analyses
                    </span>
                    {session.total_cost_usd > 0 && (
                      <span>{formatCost(session.total_cost_usd)}</span>
                    )}
                    {session.shared_context?.industry && (
                      <span>🏭 {session.shared_context.industry}</span>
                    )}
                    {session.shared_context?.stage && (
                      <span>📍 {session.shared_context.stage}</span>
                    )}
                  </div>

                  {/* Completed analysis badges */}
                  {session.completed_prompts && session.completed_prompts.length > 0 && (
                    <div style={{ marginTop: '8px', display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                      {session.completed_prompts.slice(0, 8).map(id => (
                        <span
                          key={id}
                          style={{
                            fontSize: '10px',
                            padding: '2px 6px',
                            borderRadius: '3px',
                            background: 'var(--badge-complete-bg)',
                            color: 'var(--badge-complete-text)',
                          }}
                        >
                          {id.replace('_', ' ')}
                        </span>
                      ))}
                      {session.completed_prompts.length > 8 && (
                        <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                          +{session.completed_prompts.length - 8} more
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div style={{ display: 'flex', gap: '8px', flexShrink: 0 }}>
                  <button
                    className="theme-btn-primary"
                    onClick={() => handleResume(session)}
                    style={{ padding: '7px 14px', fontSize: '13px' }}
                  >
                    Resume →
                  </button>
                  <button
                    className="theme-btn-secondary"
                    onClick={() => handleDelete(session.id)}
                    disabled={deleting === session.id}
                    style={{ padding: '7px 10px', fontSize: '13px', color: '#ef4444' }}
                  >
                    {deleting === session.id ? '…' : '🗑'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

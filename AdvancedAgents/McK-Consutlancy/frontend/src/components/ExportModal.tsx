import React, { useState } from 'react'
import { exportReport } from '../lib/api'
import { downloadBlob } from '../lib/utils'
import { useApp } from '../App'
import type { Prompt } from '../types'

interface ExportModalProps {
  sessionId: string | null
  prompts: Prompt[]
  completedIds: string[]
  onClose: () => void
}

export default function ExportModal({ sessionId, prompts, completedIds, onClose }: ExportModalProps) {
  const { apiKey } = useApp()
  const [format, setFormat] = useState<string>('docx')
  const [selected, setSelected] = useState<Set<string>>(new Set(completedIds))
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  function togglePrompt(id: string) {
    setSelected(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  function selectAll() { setSelected(new Set(completedIds)) }
  function selectNone() { setSelected(new Set()) }

  async function handleExport() {
    if (selected.size === 0) {
      setError('Select at least one analysis to export.')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const res = await exportReport(apiKey, {
        session_id: sessionId,
        format,
        selected_analyses: Array.from(selected),
      })
      const ext = format === 'pdf' ? 'pdf' : 'docx'
      downloadBlob(res.data, `mck_report.${ext}`)
      onClose()
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } }; message?: string }
      setError(axiosErr.response?.data?.detail || axiosErr.message || 'Export failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 1000,
      background: 'rgba(0,0,0,0.7)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: '20px',
    }}
      onClick={e => e.target === e.currentTarget && onClose()}
    >
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '12px',
        width: '100%',
        maxWidth: '520px',
        maxHeight: '80vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}>
        {/* Header */}
        <div style={{
          padding: '18px 20px',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <div>
            <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)' }}>
              Export Report
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Download your analyses as a formatted report
            </div>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', fontSize: '20px' }}
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '16px 20px' }}>
          {/* Format */}
          <div style={{ marginBottom: '20px' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Format
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              {[
                { id: 'docx', label: 'Word Document (.docx)', icon: '📝' },
                { id: 'pdf', label: 'PDF Report (.pdf)', icon: '📄' },
              ].map(f => (
                <button
                  key={f.id}
                  onClick={() => setFormat(f.id)}
                  style={{
                    flex: 1,
                    padding: '10px',
                    borderRadius: '8px',
                    border: format === f.id ? '2px solid var(--accent-primary)' : '2px solid var(--border-color)',
                    background: format === f.id ? 'color-mix(in srgb, var(--accent-primary) 12%, var(--bg-card))' : 'var(--bg-card)',
                    color: format === f.id ? 'var(--accent-primary)' : 'var(--text-secondary)',
                    cursor: 'pointer',
                    fontSize: '13px',
                    fontWeight: format === f.id ? 600 : 400,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '4px',
                  }}
                >
                  <span style={{ fontSize: '20px' }}>{f.icon}</span>
                  <span>{f.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Select chapters */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                Include Chapters ({selected.size}/{completedIds.length})
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button className="theme-btn-secondary" style={{ padding: '3px 8px', fontSize: '11px' }} onClick={selectAll}>All</button>
                <button className="theme-btn-secondary" style={{ padding: '3px 8px', fontSize: '11px' }} onClick={selectNone}>None</button>
              </div>
            </div>

            {completedIds.length === 0 ? (
              <div style={{ color: 'var(--text-muted)', fontSize: '13px', textAlign: 'center', padding: '20px' }}>
                No completed analyses to export. Run some analyses first.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {prompts
                  .filter(p => completedIds.includes(p.id))
                  .map(p => (
                    <label
                      key={p.id}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                        padding: '8px 10px',
                        borderRadius: '6px',
                        background: selected.has(p.id) ? 'color-mix(in srgb, var(--accent-primary) 8%, var(--bg-card))' : 'transparent',
                        border: '1px solid ' + (selected.has(p.id) ? 'color-mix(in srgb, var(--accent-primary) 30%, transparent)' : 'transparent'),
                        cursor: 'pointer',
                        fontSize: '13px',
                        color: 'var(--text-secondary)',
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={selected.has(p.id)}
                        onChange={() => togglePrompt(p.id)}
                        style={{ accentColor: 'var(--accent-primary)' }}
                      />
                      <span>{p.short_name || p.title}</span>
                    </label>
                  ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div style={{
          padding: '14px 20px',
          borderTop: '1px solid var(--border-color)',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
        }}>
          {error && (
            <div style={{ fontSize: '13px', color: '#fca5a5' }}>⚠️ {error}</div>
          )}
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
            <button className="theme-btn-secondary" onClick={onClose}>Cancel</button>
            <button
              className="theme-btn-primary"
              onClick={handleExport}
              disabled={loading || selected.size === 0}
              style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
            >
              {loading ? (
                <><span className="spinner" style={{ width: '14px', height: '14px' }} /> Generating…</>
              ) : (
                `Export ${selected.size} Chapter${selected.size !== 1 ? 's' : ''}`
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

import React, { useRef, useState, useEffect } from 'react'
import { useApp } from '../App'
import { useSession } from '../hooks/useSession'
import { useSanityCheck } from '../hooks/useSanityCheck'
import Layout from '../components/Layout'
import OutputRenderer from '../components/OutputRenderer'
import { uploadBusinessCase, deleteBusinessCase } from '../lib/api'
import { formatCost, formatTokens } from '../lib/utils'
import type { BusinessCase } from '../types'

const ACCEPTED = '.pdf,.xlsx,.xls,.docx'
const MODEL_OPTIONS = [
  { value: 'claude-sonnet-4-6', label: 'Claude Sonnet 4.6 (Recommended)' },
  { value: 'claude-opus-4-6', label: 'Claude Opus 4.6 (Highest Quality)' },
]

export default function BusinessCasePage() {
  const { apiKey, sessionId, setSessionId, businessCase, setBusinessCase, enrichPromptsWithBusinessCase, setEnrichPromptsWithBusinessCase } = useApp()
  const { analyses } = useSession(sessionId, setSessionId)
  const { status, output, meta, error, run, stop, reset } = useSanityCheck()

  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [dragging, setDragging] = useState(false)
  const [model, setModel] = useState('claude-sonnet-4-6')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const completedCount = Object.keys(analyses).length
  const canSanityCheck = !!businessCase && !!sessionId && completedCount > 0
  const isRunning = status === 'loading' || status === 'streaming'

  async function handleFile(file: File) {
    setUploading(true)
    setUploadError(null)
    try {
      const bc = await uploadBusinessCase(file, sessionId)
      setBusinessCase(bc)
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      // Try to extract FastAPI detail message
      const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setUploadError(detail || msg)
    } finally {
      setUploading(false)
    }
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
    e.target.value = ''
  }

  async function handleRemove() {
    if (!businessCase) return
    try {
      await deleteBusinessCase(businessCase.id)
    } catch {
      // best-effort deletion
    }
    setBusinessCase(null)
    setEnrichPromptsWithBusinessCase(false)
    reset()
  }

  async function handleRunSanityCheck() {
    if (!apiKey || !sessionId || !businessCase) return
    reset()
    await run(apiKey, {
      session_id: sessionId,
      business_case_id: businessCase.id,
      model,
    })
  }

  return (
    <Layout title="Business Case">
      <div style={{ maxWidth: '860px', margin: '0 auto', padding: '28px 24px', display: 'flex', flexDirection: 'column', gap: '28px' }}>

        {/* ── Section A: Upload ── */}
        <section>
          <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text-primary)', margin: '0 0 4px' }}>
            Business Case Document
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: '0 0 20px' }}>
            Upload your actual business case (PDF, Excel, or Word) to enrich framework prompts with real data or run a post-analysis sanity check.
          </p>

          {businessCase ? (
            /* Loaded card */
            <div style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '10px',
              padding: '18px 20px',
              display: 'flex',
              flexDirection: 'column',
              gap: '14px',
            }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px' }}>
                <span style={{ fontSize: '28px', flexShrink: 0 }}>
                  {businessCase.file_type === 'pdf' ? '📕' : businessCase.file_type === 'docx' ? '📘' : '📗'}
                </span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '2px', wordBreak: 'break-all' }}>
                    {businessCase.filename}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    {businessCase.char_count.toLocaleString()} characters extracted
                  </div>
                  <div style={{
                    marginTop: '10px',
                    fontSize: '12px',
                    color: 'var(--text-secondary)',
                    background: 'var(--bg-primary)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '6px',
                    padding: '10px 12px',
                    maxHeight: '80px',
                    overflow: 'hidden',
                    lineHeight: 1.5,
                    fontFamily: 'monospace',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                  }}>
                    {businessCase.preview.slice(0, 300)}{businessCase.preview.length > 300 ? '…' : ''}
                  </div>
                </div>
                <button
                  onClick={handleRemove}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', fontSize: '18px', lineHeight: 1, flexShrink: 0, padding: '2px 4px' }}
                  title="Remove business case"
                >
                  ×
                </button>
              </div>

              {/* Enrich toggle */}
              <label style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                cursor: 'pointer',
                padding: '10px 12px',
                background: enrichPromptsWithBusinessCase
                  ? 'color-mix(in srgb, var(--accent-primary) 10%, var(--bg-primary))'
                  : 'var(--bg-primary)',
                border: `1px solid ${enrichPromptsWithBusinessCase ? 'color-mix(in srgb, var(--accent-primary) 40%, transparent)' : 'var(--border-color)'}`,
                borderRadius: '8px',
                transition: 'all 0.15s',
              }}>
                <input
                  type="checkbox"
                  checked={enrichPromptsWithBusinessCase}
                  onChange={e => setEnrichPromptsWithBusinessCase(e.target.checked)}
                  style={{ width: '16px', height: '16px', accentColor: 'var(--accent-primary)', flexShrink: 0 }}
                />
                <div>
                  <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                    Enrich all framework prompts with this document
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
                    When enabled, the business case content is appended to every framework analysis you run.
                  </div>
                </div>
              </label>

              {/* Replace button */}
              <div>
                <button
                  className="theme-btn-secondary"
                  style={{ fontSize: '12px' }}
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploading}
                >
                  Replace Document
                </button>
                <input ref={fileInputRef} type="file" accept={ACCEPTED} style={{ display: 'none' }} onChange={handleInputChange} />
              </div>
            </div>
          ) : (
            /* Drop zone */
            <div
              onDragOver={e => { e.preventDefault(); setDragging(true) }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
              onClick={() => !uploading && fileInputRef.current?.click()}
              style={{
                border: `2px dashed ${dragging ? 'var(--accent-primary)' : 'var(--border-color)'}`,
                borderRadius: '12px',
                padding: '48px 24px',
                textAlign: 'center',
                cursor: uploading ? 'wait' : 'pointer',
                background: dragging ? 'color-mix(in srgb, var(--accent-primary) 5%, var(--bg-card))' : 'var(--bg-card)',
                transition: 'all 0.15s',
              }}
            >
              {uploading ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                  <span className="spinner" style={{ width: '28px', height: '28px' }} />
                  <span style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Extracting text…</span>
                </div>
              ) : (
                <>
                  <div style={{ fontSize: '40px', marginBottom: '12px' }}>📂</div>
                  <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '6px' }}>
                    Drop your business case here
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                    Supports PDF, Excel (.xlsx / .xls), and Word (.docx) · Click to browse
                  </div>
                </>
              )}
              <input ref={fileInputRef} type="file" accept={ACCEPTED} style={{ display: 'none' }} onChange={handleInputChange} />
            </div>
          )}

          {uploadError && (
            <div style={{
              marginTop: '12px',
              background: 'color-mix(in srgb, #ef4444 15%, var(--bg-card))',
              border: '1px solid color-mix(in srgb, #ef4444 40%, transparent)',
              borderRadius: '8px',
              padding: '10px 14px',
              color: '#fca5a5',
              fontSize: '13px',
            }}>
              ⚠️ {uploadError}
            </div>
          )}
        </section>

        {/* ── Section B: Sanity Check ── */}
        <section>
          <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text-primary)', margin: '0 0 4px' }}>
            Sanity Check Report
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: '0 0 20px' }}>
            Run a McKinsey QA review that compares your completed framework analyses against the uploaded business case — surfacing conflicts, missing context, and a confidence score per framework.
          </p>

          {!businessCase && (
            <div style={{
              background: 'var(--bg-card)',
              border: '1px dashed var(--border-color)',
              borderRadius: '8px',
              padding: '24px',
              textAlign: 'center',
              color: 'var(--text-muted)',
              fontSize: '13px',
            }}>
              Upload a business case document above to enable the sanity check.
            </div>
          )}

          {businessCase && !sessionId && (
            <div style={{
              background: 'var(--bg-card)',
              border: '1px dashed var(--border-color)',
              borderRadius: '8px',
              padding: '24px',
              textAlign: 'center',
              color: 'var(--text-muted)',
              fontSize: '13px',
            }}>
              No active session. Run at least one framework analysis on the Research page first.
            </div>
          )}

          {businessCase && sessionId && completedCount === 0 && (
            <div style={{
              background: 'var(--bg-card)',
              border: '1px dashed var(--border-color)',
              borderRadius: '8px',
              padding: '24px',
              textAlign: 'center',
              color: 'var(--text-muted)',
              fontSize: '13px',
            }}>
              No framework analyses yet. Run at least one on the Research page to enable the sanity check.
            </div>
          )}

          {canSanityCheck && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
                <select
                  className="theme-input"
                  value={model}
                  onChange={e => setModel(e.target.value)}
                  style={{ width: 'auto', minWidth: '220px' }}
                  disabled={isRunning}
                >
                  {MODEL_OPTIONS.map(o => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </select>

                <button
                  className="theme-btn-primary"
                  onClick={handleRunSanityCheck}
                  disabled={isRunning}
                  style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
                >
                  {isRunning ? (
                    <>
                      <span className="spinner" style={{ width: '14px', height: '14px' }} />
                      {status === 'loading' ? 'Preparing…' : 'Analysing…'}
                    </>
                  ) : (
                    `🔍 Run Sanity Check (${completedCount} framework${completedCount !== 1 ? 's' : ''})`
                  )}
                </button>

                {isRunning && (
                  <button className="theme-btn-secondary" onClick={stop}>Stop</button>
                )}

                {output && !isRunning && (
                  <button className="theme-btn-secondary" style={{ fontSize: '12px' }} onClick={reset}>Clear</button>
                )}
              </div>

              {error && (
                <div style={{
                  background: 'color-mix(in srgb, #ef4444 15%, var(--bg-card))',
                  border: '1px solid color-mix(in srgb, #ef4444 40%, transparent)',
                  borderRadius: '8px',
                  padding: '12px 16px',
                  color: '#fca5a5',
                  fontSize: '14px',
                }}>
                  ⚠️ {error}
                </div>
              )}

              {meta && (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  flexWrap: 'wrap',
                  fontSize: '12px',
                  color: 'var(--text-muted)',
                  padding: '6px 0',
                  borderBottom: '1px solid var(--border-color)',
                }}>
                  {meta.from_cache && <span className="badge-cached">⚡ Cached</span>}
                  {meta.input_tokens != null && <span>↑ {formatTokens(meta.input_tokens)} tokens</span>}
                  {meta.output_tokens != null && <span>↓ {formatTokens(meta.output_tokens)} tokens</span>}
                  {meta.cost_usd != null && (
                    <span style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>{formatCost(meta.cost_usd)}</span>
                  )}
                </div>
              )}

              {output && (
                <div style={{
                  background: 'var(--output-bg)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  padding: '20px 24px',
                  maxHeight: '70vh',
                  overflowY: 'auto',
                }}>
                  <OutputRenderer content={output} isStreaming={status === 'streaming'} />
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </Layout>
  )
}

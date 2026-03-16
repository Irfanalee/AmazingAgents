import React, { useState, useEffect, useRef } from 'react'
import { useApp } from '../App'
import { useFeedback } from '../hooks/useFeedback'
import { fetchFeedbackHistory } from '../lib/api'
import type { FeedbackMessage } from '../types'

interface FeedbackPanelProps {
  analysisId: string
  /** Called with each streamed chunk so the parent output pane shows live updates */
  onOutputChunk: (accumulated: string) => void
  /** Called with the final revised output when streaming completes */
  onOutputDone: (finalOutput: string) => void
  /** True while the main analysis is streaming — disables the panel */
  disabled?: boolean
}

export default function FeedbackPanel({
  analysisId,
  onOutputChunk,
  onOutputDone,
  disabled = false,
}: FeedbackPanelProps) {
  const { apiKey } = useApp()
  const [isOpen, setIsOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [model, setModel] = useState('claude-sonnet-4-6')
  const [history, setHistory] = useState<FeedbackMessage[]>([])
  const historyRef = useRef<HTMLDivElement>(null)

  const { status, error, send, stop } = useFeedback(
    apiKey,
    analysisId,
    onOutputChunk,
    (finalOutput) => {
      onOutputDone(finalOutput)
      // Reload history to show the new exchange
      loadHistory()
    },
  )

  const isStreaming = status === 'loading' || status === 'streaming'

  async function loadHistory() {
    if (!apiKey || !analysisId) return
    try {
      const msgs = await fetchFeedbackHistory(apiKey, analysisId)
      setHistory(msgs)
    } catch {
      // silently ignore — history is nice-to-have
    }
  }

  useEffect(() => {
    if (isOpen && analysisId) loadHistory()
  }, [isOpen, analysisId])

  // Scroll history to bottom when new messages arrive
  useEffect(() => {
    if (historyRef.current) {
      historyRef.current.scrollTop = historyRef.current.scrollHeight
    }
  }, [history])

  async function handleSend() {
    if (!message.trim() || isStreaming) return
    const msg = message.trim()
    setMessage('')
    await send(msg, model)
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div style={{
      border: '1px solid var(--border-color)',
      borderRadius: '8px',
      overflow: 'hidden',
      background: 'var(--bg-card)',
    }}>
      {/* Toggle header */}
      <button
        onClick={() => !disabled && setIsOpen(o => !o)}
        disabled={disabled}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 16px',
          background: 'transparent',
          border: 'none',
          cursor: disabled ? 'not-allowed' : 'pointer',
          color: 'var(--text-secondary)',
          fontSize: '13px',
          fontWeight: 600,
          textAlign: 'left',
          opacity: disabled ? 0.5 : 1,
        }}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>💬</span>
          <span>Refine with Feedback</span>
          {history.length > 0 && (
            <span style={{
              background: 'var(--accent-primary)',
              color: '#fff',
              borderRadius: '10px',
              padding: '1px 7px',
              fontSize: '11px',
              fontWeight: 700,
            }}>
              {Math.floor(history.length / 2)}
            </span>
          )}
        </span>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
          {isOpen ? '▲' : '▼'}
        </span>
      </button>

      {isOpen && (
        <div style={{ borderTop: '1px solid var(--border-color)', padding: '16px' }}>
          {/* Conversation history */}
          {history.length > 0 && (
            <div
              ref={historyRef}
              style={{
                maxHeight: '220px',
                overflowY: 'auto',
                marginBottom: '14px',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
              }}
            >
              {history.map(msg => (
                <div key={msg.id} style={{
                  display: 'flex',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                }}>
                  {msg.role === 'user' ? (
                    <div style={{
                      maxWidth: '80%',
                      background: 'var(--accent-primary)',
                      color: '#fff',
                      borderRadius: '12px 12px 2px 12px',
                      padding: '8px 12px',
                      fontSize: '13px',
                      lineHeight: '1.4',
                    }}>
                      {msg.content}
                    </div>
                  ) : (
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      background: 'color-mix(in srgb, #22c55e 12%, var(--bg-card))',
                      border: '1px solid color-mix(in srgb, #22c55e 30%, transparent)',
                      borderRadius: '12px 12px 12px 2px',
                      padding: '7px 12px',
                      fontSize: '12px',
                      color: '#86efac',
                    }}>
                      <span>✓</span>
                      <span>Analysis revised</span>
                    </div>
                  )}
                </div>
              ))}
              {isStreaming && (
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '7px 12px',
                  fontSize: '12px',
                  color: 'var(--text-muted)',
                }}>
                  <span className="spinner" style={{ width: '12px', height: '12px' }} />
                  <span>Revising analysis…</span>
                </div>
              )}
            </div>
          )}

          {/* Error */}
          {error && (
            <div style={{
              background: 'color-mix(in srgb, #ef4444 15%, var(--bg-card))',
              border: '1px solid color-mix(in srgb, #ef4444 40%, transparent)',
              borderRadius: '6px',
              padding: '8px 12px',
              color: '#fca5a5',
              fontSize: '13px',
              marginBottom: '12px',
            }}>
              ⚠️ {error}
            </div>
          )}

          {/* Input area */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <textarea
              className="theme-input"
              rows={3}
              placeholder="Describe corrections or feedback, e.g. 'My monthly revenue is $50k not $10k, and the growth rate is 40%'"
              value={message}
              onChange={e => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isStreaming}
              style={{
                resize: 'vertical',
                minHeight: '72px',
                fontFamily: 'inherit',
                fontSize: '13px',
                lineHeight: '1.5',
              }}
            />

            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
              <select
                className="theme-input"
                value={model}
                onChange={e => setModel(e.target.value)}
                disabled={isStreaming}
                style={{ width: 'auto', minWidth: '180px', fontSize: '12px' }}
              >
                <option value="claude-sonnet-4-6">Sonnet 4.6 (Recommended)</option>
                <option value="claude-opus-4-6">Opus 4.6 (Highest Quality)</option>
                <option value="claude-haiku-4-5-20251001">Haiku 4.5 (Fastest)</option>
              </select>

              {isStreaming ? (
                <button className="theme-btn-secondary" onClick={stop} style={{ fontSize: '12px' }}>
                  Stop
                </button>
              ) : (
                <button
                  className="theme-btn-primary"
                  onClick={handleSend}
                  disabled={!message.trim()}
                  style={{ fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}
                >
                  Revise Analysis
                </button>
              )}

              <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                ⌘↵ to send
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

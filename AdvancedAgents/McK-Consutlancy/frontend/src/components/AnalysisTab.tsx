import React, { useState, useRef, useEffect, useCallback } from 'react'
import { useApp } from '../App'
import { useAnalysis } from '../hooks/useAnalysis'
import OutputRenderer from './OutputRenderer'
import FeedbackPanel from './FeedbackPanel'
import { formatCost, formatTokens } from '../lib/utils'
import { fetchCostEstimate } from '../lib/api'
import type { Prompt, StoredAnalysis, AnalysisMeta } from '../types'

interface AnalysisTabProps {
  prompt: Prompt
  sessionId: string | null
  onComplete?: (promptId: string, data: StoredAnalysis) => void
  businessCaseId?: string | null
}

export default function AnalysisTab({ prompt, sessionId, onComplete, businessCaseId }: AnalysisTabProps) {
  const { apiKey, sharedContext } = useApp()
  const { status, output, meta, error, run, reset, stop } = useAnalysis()
  const [extraInputs, setExtraInputs] = useState<Record<string, string>>({})
  const [model, setModel] = useState<string>('claude-sonnet-4-6')
  const [costEstimate, setCostEstimate] = useState<number | null>(null)
  const outputRef = useRef<HTMLDivElement>(null)

  // Restore previous output if passed in
  const [savedOutput, setSavedOutput] = useState<string>(prompt.existingOutput || '')
  const [savedMeta, setSavedMeta] = useState<AnalysisMeta | null>(prompt.existingMeta || null)
  // Live feedback streaming output — replaces savedOutput while feedback is in progress
  const [feedbackOutput, setFeedbackOutput] = useState<string>('')
  const [generatedAt, setGeneratedAt] = useState<Date | null>(
    prompt.existingMeta ? new Date() : null
  )

  const displayOutput = output || feedbackOutput || savedOutput
  const displayMeta = meta || savedMeta
  const isRunning = status === 'loading' || status === 'streaming'

  const analysisId = savedMeta?.analysis_id ?? null

  const handleFeedbackChunk = useCallback((accumulated: string) => {
    setFeedbackOutput(accumulated)
  }, [])

  const handleFeedbackDone = useCallback((finalOutput: string) => {
    setSavedOutput(finalOutput)
    setFeedbackOutput('')
  }, [])

  // Auto-scroll output while streaming
  useEffect(() => {
    if (status === 'streaming' && outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight
    }
  }, [output, status])

  // Bubble completed analysis up
  useEffect(() => {
    if (status === 'done' && meta && output) {
      setSavedOutput(output)
      setSavedMeta(meta)
      setGeneratedAt(new Date())
      if (onComplete) {
        onComplete(prompt.id, {
          prompt_id: prompt.id,
          output,
          ...meta,
        })
      }
    }
  }, [status, meta, output])

  // Sync saved output if analyses load after mount (async session load)
  useEffect(() => {
    if (status === 'idle' && !savedOutput && prompt.existingOutput) {
      setSavedOutput(prompt.existingOutput)
      setSavedMeta(prompt.existingMeta || null)
    }
  }, [prompt.existingOutput, prompt.existingMeta])

  // Fetch cost estimate whenever model or extra inputs change
  useEffect(() => {
    if (!apiKey) return
    const controller = new AbortController()
    const timer = setTimeout(async () => {
      try {
        const result = await fetchCostEstimate(apiKey, {
          prompt_id: prompt.id,
          shared_context: sharedContext,
          extra_inputs: extraInputs,
          model,
        }, controller.signal)
        setCostEstimate(result.cost_usd_estimate)
      } catch {
        setCostEstimate(null)
      }
    }, 400)
    return () => {
      clearTimeout(timer)
      controller.abort()
    }
  }, [model, extraInputs, prompt.id])

  async function handleGenerate() {
    if (!apiKey) {
      alert('No API key set. Please go to Setup.')
      return
    }
    await run(apiKey, {
      prompt_id: prompt.id,
      shared_context: sharedContext,
      extra_inputs: extraInputs,
      model,
      session_id: sessionId,
      business_case_id: businessCaseId ?? null,
    })
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Prompt info header */}
      <div>
        <h2 style={{
          fontSize: '22px',
          fontWeight: 700,
          color: 'var(--text-primary)',
          margin: '0 0 6px',
        }}>
          {prompt.title}
        </h2>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: 0 }}>
          McKinsey-grade analysis powered by Claude AI
        </p>
      </div>

      {/* Extra inputs (prompt-specific) */}
      {prompt.extra_inputs && prompt.extra_inputs.length > 0 && (
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          padding: '14px 16px',
        }}>
          <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Additional Inputs
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '10px' }}>
            {prompt.extra_inputs.map(field => (
              <div key={field.key} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <label style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                  {field.label}
                  {!field.required && <span style={{ color: 'var(--text-muted)', marginLeft: '4px' }}>(optional)</span>}
                </label>
                <input
                  className="theme-input"
                  type="text"
                  placeholder={field.placeholder}
                  value={extraInputs[field.key] || ''}
                  onChange={e => setExtraInputs(prev => ({ ...prev, [field.key]: e.target.value }))}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Model selector + Generate button */}
      <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
        <select
          className="theme-input"
          value={model}
          onChange={e => setModel(e.target.value)}
          style={{ width: 'auto', minWidth: '200px' }}
          disabled={isRunning}
        >
          <option value="claude-sonnet-4-6">Claude Sonnet 4.6 (Recommended)</option>
          <option value="claude-opus-4-6">Claude Opus 4.6 (Highest Quality)</option>
          <option value="claude-haiku-4-5-20251001">Claude Haiku 4.5 (Fastest)</option>
        </select>

        <button
          className="theme-btn-primary"
          onClick={handleGenerate}
          disabled={isRunning}
          style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
        >
          {isRunning ? (
            <>
              <span className="spinner" style={{ width: '14px', height: '14px' }} />
              {status === 'loading' ? 'Preparing…' : 'Generating…'}
            </>
          ) : (
            <>
              ⚡ {displayOutput ? 'Regenerate' : 'Generate Analysis'}
            </>
          )}
        </button>

        {isRunning && (
          <button className="theme-btn-secondary" onClick={stop}>
            Stop
          </button>
        )}

        {!isRunning && !displayMeta && costEstimate !== null && (
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            Est. ~{formatCost(costEstimate)}
          </span>
        )}

        {displayOutput && !isRunning && (
          <button
            className="theme-btn-secondary"
            onClick={reset}
            style={{ fontSize: '12px' }}
          >
            Clear
          </button>
        )}
      </div>

      {/* Error */}
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

      {/* Meta bar (tokens / cost / cache) */}
      {displayMeta && (
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
          {displayMeta.from_cache && (
            <span className="badge-cached">⚡ Cached</span>
          )}
          {displayMeta.input_tokens != null && (
            <span>↑ {formatTokens(displayMeta.input_tokens)} tokens</span>
          )}
          {displayMeta.output_tokens != null && (
            <span>↓ {formatTokens(displayMeta.output_tokens)} tokens</span>
          )}
          {displayMeta.cost_usd != null && (
            <span style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>
              {formatCost(displayMeta.cost_usd)}
            </span>
          )}
          {generatedAt && (
            <span style={{ marginLeft: 'auto' }}>
              Generated {generatedAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          )}
        </div>
      )}

      {/* Feedback panel — shown whenever there is output */}
      {displayOutput && !isRunning && (
        <FeedbackPanel
          analysisId={analysisId}
          onOutputChunk={handleFeedbackChunk}
          onOutputDone={handleFeedbackDone}
          disabled={isRunning}
        />
      )}

      {/* Output */}
      {displayOutput && (
        <div
          ref={outputRef}
          style={{
            background: 'var(--output-bg)',
            border: '1px solid var(--border-color)',
            borderRadius: '8px',
            padding: '20px 24px',
            maxHeight: '70vh',
            overflowY: 'auto',
          }}
        >
          <OutputRenderer
            content={displayOutput}
            isStreaming={status === 'streaming'}
          />
        </div>
      )}

      {/* Empty state */}
      {!displayOutput && !isRunning && status === 'idle' && (
        <div style={{
          background: 'var(--bg-card)',
          border: '1px dashed var(--border-color)',
          borderRadius: '8px',
          padding: '40px 20px',
          textAlign: 'center',
          color: 'var(--text-muted)',
        }}>
          <div style={{ fontSize: '36px', marginBottom: '12px' }}>📄</div>
          <div style={{ fontSize: '15px', fontWeight: 500, marginBottom: '6px' }}>
            No analysis yet
          </div>
          <div style={{ fontSize: '13px' }}>
            Fill in your business context above, then click Generate Analysis.
          </div>
        </div>
      )}
    </div>
  )
}

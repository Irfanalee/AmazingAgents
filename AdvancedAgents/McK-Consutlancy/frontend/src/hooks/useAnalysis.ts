import { useState, useRef, useCallback } from 'react'
import { startAnalysisStream } from '../lib/api'
import type { AnalysisStatus, AnalysisMeta } from '../types'

/**
 * Hook for managing a streaming analysis request.
 * Returns state + a `run(payload)` trigger function.
 */
export function useAnalysis() {
  const [status, setStatus] = useState<AnalysisStatus>('idle')
  const [output, setOutput] = useState<string>('')
  const [meta, setMeta] = useState<AnalysisMeta | null>(null)
  const [error, setError] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  const run = useCallback(async (apiKey: string, payload: Record<string, unknown>) => {
    // Abort any in-progress stream
    if (abortRef.current) {
      abortRef.current.abort()
    }
    const controller = new AbortController()
    abortRef.current = controller

    setStatus('loading')
    setOutput('')
    setMeta(null)
    setError(null)

    try {
      const res = await startAnalysisStream(apiKey, payload)

      if (!res.ok) {
        const text = await res.text()
        throw new Error(`HTTP ${res.status}: ${text}`)
      }

      if (!res.body) throw new Error('No response body')

      setStatus('streaming')
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        if (controller.signal.aborted) break

        const { value, done } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? '' // keep incomplete last line

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const jsonStr = line.slice(6).trim()
          if (!jsonStr) continue

          try {
            const event = JSON.parse(jsonStr) as {
              type: string
              text?: string
              input_tokens?: number
              output_tokens?: number
              cost_usd?: number
              from_cache?: boolean
              analysis_id?: string
              message?: string
            }

            if (event.type === 'text') {
              setOutput(prev => prev + (event.text ?? ''))
            } else if (event.type === 'cache_hit') {
              setMeta({
                from_cache: true,
                input_tokens: event.input_tokens,
                output_tokens: event.output_tokens,
                cost_usd: event.cost_usd,
              })
            } else if (event.type === 'done') {
              setMeta(prev => ({
                from_cache: event.from_cache ?? prev?.from_cache ?? false,
                analysis_id: event.analysis_id,
                input_tokens: event.input_tokens ?? prev?.input_tokens,
                output_tokens: event.output_tokens ?? prev?.output_tokens,
                cost_usd: event.cost_usd ?? prev?.cost_usd,
              }))
              setStatus('done')
            } else if (event.type === 'error') {
              setError(event.message ?? 'Unknown error')
              setStatus('error')
            }
          } catch {
            // ignore JSON parse errors in stream
          }
        }
      }

      setStatus(s => (s !== 'error' ? 'done' : s))
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') return
      setError(err instanceof Error ? err.message : 'Stream failed')
      setStatus('error')
    }
  }, [])

  const reset = useCallback(() => {
    if (abortRef.current) abortRef.current.abort()
    setStatus('idle')
    setOutput('')
    setMeta(null)
    setError(null)
  }, [])

  const stop = useCallback(() => {
    if (abortRef.current) abortRef.current.abort()
    setStatus('done')
  }, [])

  return { status, output, meta, error, run, reset, stop }
}

import { useState, useRef, useCallback } from 'react'
import { startFeedbackStream } from '../lib/api'
import type { AnalysisStatus } from '../types'

/**
 * Hook for streaming feedback-driven analysis refinement.
 * Calls onOutputChunk per text chunk (live update) and onDone with final output.
 */
export function useFeedback(
  apiKey: string,
  analysisId: string | null,
  onOutputChunk: (accumulated: string) => void,
  onDone: (finalOutput: string) => void,
) {
  const [status, setStatus] = useState<AnalysisStatus>('idle')
  const [error, setError] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  const send = useCallback(async (message: string, model: string) => {
    if (!analysisId) return
    if (abortRef.current) abortRef.current.abort()

    const controller = new AbortController()
    abortRef.current = controller

    setStatus('loading')
    setError(null)

    try {
      const res = await startFeedbackStream(apiKey, analysisId, { message, model })

      if (!res.ok) {
        const text = await res.text()
        throw new Error(`HTTP ${res.status}: ${text}`)
      }
      if (!res.body) throw new Error('No response body')

      setStatus('streaming')
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let accumulated = ''

      while (true) {
        if (controller.signal.aborted) break
        const { value, done } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

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
              message?: string
            }

            if (event.type === 'text') {
              accumulated += event.text ?? ''
              onOutputChunk(accumulated)
            } else if (event.type === 'done') {
              onDone(accumulated)
              setStatus('done')
            } else if (event.type === 'error') {
              setError(event.message ?? 'Unknown error')
              setStatus('error')
            }
          } catch {
            // ignore JSON parse errors
          }
        }
      }

      setStatus(s => (s !== 'error' ? 'done' : s))
    } catch (err: unknown) {
      if (err instanceof Error && err.name === 'AbortError') return
      setError(err instanceof Error ? err.message : 'Stream failed')
      setStatus('error')
    }
  }, [apiKey, analysisId, onOutputChunk, onDone])

  const stop = useCallback(() => {
    if (abortRef.current) abortRef.current.abort()
    setStatus('done')
  }, [])

  const reset = useCallback(() => {
    if (abortRef.current) abortRef.current.abort()
    setStatus('idle')
    setError(null)
  }, [])

  return { status, error, send, stop, reset }
}

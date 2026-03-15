import axios, { type AxiosResponse } from 'axios'
import type { Prompt, Session, Analysis, CacheStats, SharedContext } from '../types'

const BASE = '/api'

function client(apiKey: string) {
  return axios.create({
    baseURL: BASE,
    headers: apiKey ? { 'X-API-Key': apiKey } : {},
  })
}

// ── Prompts ───────────────────────────────────────────────────────
export async function fetchPrompts(): Promise<Prompt[]> {
  const res = await axios.get<Prompt[]>(`${BASE}/prompts`)
  return res.data
}

export async function fetchPrompt(promptId: string): Promise<Prompt> {
  const res = await axios.get<Prompt>(`${BASE}/prompts/${promptId}`)
  return res.data
}

// ── Sessions ──────────────────────────────────────────────────────
export async function fetchSessions(): Promise<Session[]> {
  const res = await axios.get<Session[]>(`${BASE}/sessions`)
  return res.data
}

export async function createSession(data: {
  name: string
  shared_context: Partial<SharedContext>
  theme?: string
}): Promise<Session> {
  const res = await axios.post<Session>(`${BASE}/sessions`, data)
  return res.data
}

export async function fetchSession(sessionId: string): Promise<Session & { analyses: Analysis[] }> {
  const res = await axios.get<Session & { analyses: Analysis[] }>(`${BASE}/sessions/${sessionId}`)
  return res.data
}

export async function updateSession(sessionId: string, data: Partial<Session>): Promise<Session> {
  const res = await axios.put<Session>(`${BASE}/sessions/${sessionId}`, data)
  return res.data
}

export async function deleteSession(sessionId: string): Promise<{ success: boolean }> {
  const res = await axios.delete<{ success: boolean }>(`${BASE}/sessions/${sessionId}`)
  return res.data
}

// ── Cache ─────────────────────────────────────────────────────────
export async function fetchCacheStats(): Promise<CacheStats> {
  const res = await axios.get<CacheStats>(`${BASE}/cache/stats`)
  return res.data
}

export async function clearCache(): Promise<{ success: boolean }> {
  const res = await axios.delete<{ success: boolean }>(`${BASE}/cache`)
  return res.data
}

// ── Export ────────────────────────────────────────────────────────
export async function exportReport(
  apiKey: string,
  data: { session_id: string | null; format: string; selected_analyses: string[] }
): Promise<AxiosResponse<Blob>> {
  return client(apiKey).post<Blob>('/export', data, { responseType: 'blob' })
}

// ── Cost estimate ─────────────────────────────────────────────────
export interface CostEstimate {
  input_tokens_estimate: number
  output_tokens_estimate: number
  cost_usd_estimate: number
  model: string
}

export async function fetchCostEstimate(
  apiKey: string,
  payload: Record<string, unknown>
): Promise<CostEstimate> {
  const res = await client(apiKey).post<CostEstimate>('/analyze/estimate', payload)
  return res.data
}

// ── Batch analysis ────────────────────────────────────────────────
export interface BatchResult {
  prompt_id: string
  output?: string
  from_cache?: boolean
  analysis_id?: string
  input_tokens?: number
  output_tokens?: number
  cost_usd?: number
  error?: string
}

export async function runBatchAnalysis(
  apiKey: string,
  payload: {
    shared_context: Partial<SharedContext>
    model?: string
    session_id?: string | null
    prompt_ids?: string[]
  }
): Promise<{ results: BatchResult[]; total: number; errors: BatchResult[] }> {
  const res = await client(apiKey).post('/analyze/batch', payload)
  return res.data
}

// ── Streaming analysis ────────────────────────────────────────────
// Returns a fetch Response — caller should read the SSE stream
export function startAnalysisStream(
  apiKey: string,
  payload: Record<string, unknown>
): Promise<Response> {
  return fetch(`${BASE}/analyze/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': apiKey,
    },
    body: JSON.stringify(payload),
  })
}

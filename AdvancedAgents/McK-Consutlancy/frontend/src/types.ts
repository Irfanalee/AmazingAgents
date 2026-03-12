export interface SharedContext {
  business_name: string
  product_description: string
  industry: string
  stage: string
  target_customer: string
  geography: string
  revenue: string
  team_size: string
  main_challenge: string
}

export interface ExtraInput {
  key: string
  label: string
  placeholder: string
  required: boolean
}

export interface Prompt {
  id: string
  order: number
  title: string
  short_name: string
  body: string
  placeholders: string[]
  extra_inputs: ExtraInput[]
  existingOutput?: string
  existingMeta?: AnalysisMeta | null
}

export interface Analysis {
  id: string
  prompt_id: string
  prompt_title: string
  output: string
  model: string
  input_tokens: number
  output_tokens: number
  cost_usd: number
  from_cache: boolean
  created_at: string
}

export interface AnalysisMeta {
  from_cache: boolean
  input_tokens?: number
  output_tokens?: number
  cost_usd?: number
  analysis_id?: string
}

export type AnalysisStatus = 'idle' | 'loading' | 'streaming' | 'done' | 'error'

export interface StoredAnalysis {
  prompt_id: string
  output: string
  from_cache: boolean
  input_tokens?: number
  output_tokens?: number
  cost_usd?: number
  analysis_id?: string
}

export interface Session {
  id: string
  name: string
  shared_context: SharedContext
  theme: string
  created_at: string
  updated_at?: string
  analysis_count: number
  completed_prompts: string[]
  total_cost_usd: number
  analyses?: Analysis[]
}

export interface CacheStats {
  total_entries: number
  total_hits: number
  estimated_savings_usd: number
}

export interface AppContextType {
  apiKey: string
  setApiKey: (k: string) => void
  theme: string
  setTheme: (t: string) => void
  sessionId: string | null
  setSessionId: (id: string | null) => void
  sharedContext: Partial<SharedContext>
  setSharedContext: React.Dispatch<React.SetStateAction<Partial<SharedContext>>>
}

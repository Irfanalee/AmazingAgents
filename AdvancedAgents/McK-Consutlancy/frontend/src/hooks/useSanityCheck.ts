import { useAnalysis } from './useAnalysis'
import { startSanityCheckStream } from '../lib/api'

export function useSanityCheck() {
  return useAnalysis((apiKey, payload) =>
    startSanityCheckStream(apiKey, payload as { session_id: string; business_case_id: string; model: string })
  )
}

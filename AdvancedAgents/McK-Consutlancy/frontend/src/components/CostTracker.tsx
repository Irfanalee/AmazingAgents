import React, { useState, useEffect } from 'react'
import { fetchCacheStats, clearCache } from '../lib/api'
import { formatCost, formatTokens } from '../lib/utils'
import type { StoredAnalysis, CacheStats } from '../types'

interface StatRowProps {
  label: string
  value: string
  highlight?: boolean
  positive?: boolean
}

function StatRow({ label, value, highlight, positive }: StatRowProps) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{label}</span>
      <span style={{
        fontSize: '13px',
        fontWeight: highlight ? 700 : 500,
        color: positive ? 'var(--badge-complete-text)' : (highlight ? 'var(--accent-primary)' : 'var(--text-secondary)'),
        fontFamily: highlight ? 'var(--font-mono, monospace)' : 'inherit',
      }}>
        {value}
      </span>
    </div>
  )
}

interface CostTrackerProps {
  analyses?: Record<string, StoredAnalysis>
}

export default function CostTracker({ analyses = {} }: CostTrackerProps) {
  const [cacheStats, setCacheStats] = useState<CacheStats | null>(null)

  useEffect(() => {
    fetchCacheStats().then(setCacheStats).catch(() => {})
  }, [])

  const completedAnalyses = Object.values(analyses)
  const totalCost = completedAnalyses.reduce((sum, a) => sum + (a.cost_usd || 0), 0)
  const totalInputTokens = completedAnalyses.reduce((sum, a) => sum + (a.input_tokens || 0), 0)
  const totalOutputTokens = completedAnalyses.reduce((sum, a) => sum + (a.output_tokens || 0), 0)
  const cacheCount = completedAnalyses.filter(a => a.from_cache).length

  const handleClearCache = async () => {
    if (!confirm('Clear all cached responses?')) return
    await clearCache()
    setCacheStats({ total_entries: 0, total_hits: 0, estimated_savings_usd: 0 })
  }

  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border-color)',
      borderRadius: '8px',
      padding: '12px 16px',
    }}>
      <div style={{
        fontSize: '11px',
        fontWeight: 700,
        color: 'var(--text-muted)',
        textTransform: 'uppercase',
        letterSpacing: '0.08em',
        marginBottom: '10px',
      }}>
        Cost & Tokens
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        <StatRow label="Session cost" value={formatCost(totalCost)} highlight />
        <StatRow label="Input tokens" value={formatTokens(totalInputTokens)} />
        <StatRow label="Output tokens" value={formatTokens(totalOutputTokens)} />
        <StatRow label="Cached responses" value={`${cacheCount}`} />
        {cacheStats && (
          <>
            <div style={{ borderTop: '1px solid var(--border-color)', margin: '4px 0' }} />
            <StatRow
              label="Cache savings"
              value={formatCost(cacheStats.estimated_savings_usd)}
              positive
            />
            <StatRow label="Cache hits total" value={String(cacheStats.total_hits)} />
          </>
        )}
      </div>

      {cacheStats && cacheStats.total_entries > 0 && (
        <button
          onClick={handleClearCache}
          style={{
            marginTop: '10px',
            width: '100%',
            padding: '6px',
            background: 'transparent',
            border: '1px solid var(--border-color)',
            borderRadius: '4px',
            color: 'var(--text-muted)',
            fontSize: '11px',
            cursor: 'pointer',
          }}
        >
          Clear cache ({cacheStats.total_entries} entries)
        </button>
      )}
    </div>
  )
}

import React from 'react'
import { useApp } from '../App'
import ThemeToggle from './ThemeToggle'
import type { Prompt } from '../types'

const ICONS: Record<string, string> = {
  executive_strategy: '🎯',
  tam_analysis: '📈',
  competitive_landscape: '🏆',
  customer_personas: '👥',
  industry_trends: '🔭',
  swot_porters: '⚔️',
  pricing_strategy: '💰',
  gtm_strategy: '🚀',
  customer_journey: '🗺️',
  financial_model: '📊',
  risk_assessment: '🛡️',
  market_entry: '🌍',
}

interface SidebarProps {
  prompts: Prompt[]
  activePromptId: string | null
  onSelectPrompt: (id: string) => void
  completedIds?: string[]
}

export default function Sidebar({ prompts, activePromptId, onSelectPrompt, completedIds = [] }: SidebarProps) {
  const { theme: _theme } = useApp()

  return (
    <div style={{
      width: '260px',
      minWidth: '260px',
      background: 'var(--bg-secondary)',
      borderRight: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      position: 'sticky',
      top: 0,
      overflow: 'hidden',
    }}>
      {/* Logo / Title */}
      <div style={{
        padding: '20px 16px 16px',
        borderBottom: '1px solid var(--border-color)',
      }}>
        <div style={{
          fontSize: '14px',
          fontWeight: 800,
          color: 'var(--accent-primary)',
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
        }}>
          ProductLaunchStrategy Suite
        </div>
        <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
          {completedIds.length}/12 analyses complete
        </div>

        {/* Progress bar */}
        <div style={{
          marginTop: '8px',
          height: '3px',
          background: 'var(--border-color)',
          borderRadius: '2px',
          overflow: 'hidden',
        }}>
          <div style={{
            height: '100%',
            width: `${(completedIds.length / 12) * 100}%`,
            background: 'var(--accent-primary)',
            borderRadius: '2px',
            transition: 'width 0.4s ease',
          }} />
        </div>
      </div>

      {/* Analysis list */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '8px 0' }}>
        {prompts.map(prompt => {
          const isActive = prompt.id === activePromptId
          const isComplete = completedIds.includes(prompt.id)

          return (
            <button
              key={prompt.id}
              onClick={() => onSelectPrompt(prompt.id)}
              style={{
                width: '100%',
                padding: '10px 16px',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                background: isActive ? 'color-mix(in srgb, var(--accent-primary) 12%, var(--bg-secondary))' : 'transparent',
                borderLeft: isActive ? '3px solid var(--accent-primary)' : '3px solid transparent',
                border: 'none',
                borderRight: 'none',
                borderTop: 'none',
                borderBottom: 'none',
                color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)',
                cursor: 'pointer',
                textAlign: 'left',
                transition: 'all 0.15s',
                fontSize: '13px',
              }}
              onMouseEnter={e => {
                if (!isActive) {
                  e.currentTarget.style.background = 'var(--bg-hover)'
                  e.currentTarget.style.color = 'var(--text-primary)'
                }
              }}
              onMouseLeave={e => {
                if (!isActive) {
                  e.currentTarget.style.background = 'transparent'
                  e.currentTarget.style.color = 'var(--text-secondary)'
                }
              }}
            >
              <span style={{ fontSize: '16px', flexShrink: 0 }}>
                {ICONS[prompt.id] || '📄'}
              </span>
              <span style={{ flex: 1, lineHeight: '1.3' }}>
                {prompt.short_name || prompt.title}
              </span>
              {isComplete && (
                <span style={{
                  fontSize: '10px',
                  fontWeight: 600,
                  padding: '2px 6px',
                  borderRadius: '4px',
                  background: 'var(--badge-complete-bg)',
                  color: 'var(--badge-complete-text)',
                  flexShrink: 0,
                }}>
                  ✓
                </span>
              )}
            </button>
          )
        })}
      </div>

      {/* Footer: theme toggle */}
      <div style={{
        padding: '12px',
        borderTop: '1px solid var(--border-color)',
      }}>
        <ThemeToggle compact />
      </div>
    </div>
  )
}

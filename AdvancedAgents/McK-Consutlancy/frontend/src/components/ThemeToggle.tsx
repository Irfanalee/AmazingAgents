import React from 'react'
import { useApp } from '../App'

interface ThemeOption {
  id: string
  label: string
  icon: string
  color: string
}

const THEMES: ThemeOption[] = [
  { id: 'mckinsey-dark', label: 'McKinsey Dark', icon: '🌑', color: '#C9A84C' },
  { id: 'premium-white', label: 'Premium White', icon: '☀️', color: '#2563EB' },
  { id: 'data-dashboard', label: 'Data Dashboard', icon: '📊', color: '#00D4FF' },
]

interface ThemeToggleProps {
  compact?: boolean
}

export default function ThemeToggle({ compact = false }: ThemeToggleProps) {
  const { theme, setTheme } = useApp()

  if (compact) {
    const current = THEMES.find(t => t.id === theme) || THEMES[0]
    const next = THEMES[(THEMES.findIndex(t => t.id === theme) + 1) % THEMES.length]
    return (
      <button
        onClick={() => setTheme(next.id)}
        title={`Switch to ${next.label}`}
        style={{
          background: 'transparent',
          border: '1px solid var(--border-color)',
          borderRadius: '6px',
          padding: '6px 10px',
          color: 'var(--text-secondary)',
          cursor: 'pointer',
          fontSize: '13px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
        }}
      >
        <span>{current.icon}</span>
        <span style={{ fontSize: '11px' }}>{current.label}</span>
      </button>
    )
  }

  return (
    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
      {THEMES.map(t => (
        <button
          key={t.id}
          onClick={() => setTheme(t.id)}
          style={{
            flex: 1,
            minWidth: '120px',
            padding: '10px 14px',
            borderRadius: '8px',
            border: theme === t.id
              ? `2px solid ${t.color}`
              : '2px solid var(--border-color)',
            background: theme === t.id
              ? `color-mix(in srgb, ${t.color} 12%, var(--bg-card))`
              : 'var(--bg-card)',
            color: theme === t.id ? t.color : 'var(--text-secondary)',
            cursor: 'pointer',
            fontWeight: theme === t.id ? 600 : 400,
            fontSize: '13px',
            transition: 'all 0.2s',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '4px',
          }}
        >
          <span style={{ fontSize: '20px' }}>{t.icon}</span>
          <span>{t.label}</span>
          {theme === t.id && (
            <span style={{ fontSize: '10px', opacity: 0.7 }}>Active</span>
          )}
        </button>
      ))}
    </div>
  )
}

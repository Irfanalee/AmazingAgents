import React, { useState } from 'react'
import { useApp } from '../App'
import type { SharedContext } from '../types'

interface TextField {
  key: keyof SharedContext
  label: string
  placeholder: string
  textarea?: boolean
  type?: never
  options?: never
}

interface SelectField {
  key: keyof SharedContext
  label: string
  placeholder?: string
  type: 'select'
  options: string[]
  textarea?: never
}

type Field = TextField | SelectField

const FIELDS: Field[] = [
  { key: 'business_name', label: 'Business Name', placeholder: 'e.g. AcmeCorp AI' },
  { key: 'product_description', label: 'Product / Service', placeholder: 'e.g. AI-powered CRM for SMBs', textarea: true },
  { key: 'industry', label: 'Industry', placeholder: 'e.g. B2B SaaS / Healthcare Tech' },
  {
    key: 'stage', label: 'Company Stage', placeholder: 'Select stage', type: 'select',
    options: ['Idea', 'MVP', 'Early Traction', 'Growth', 'Scale', 'Enterprise'],
  },
  { key: 'target_customer', label: 'Target Customer', placeholder: 'e.g. SMB operations managers' },
  { key: 'geography', label: 'Primary Market / Geography', placeholder: 'e.g. North America, Global' },
  { key: 'revenue', label: 'Current Revenue', placeholder: 'e.g. $50k MRR or pre-revenue' },
  { key: 'team_size', label: 'Team Size', placeholder: 'e.g. 12 FTEs' },
  { key: 'main_challenge', label: 'Main Challenge', placeholder: 'e.g. Struggling with enterprise sales cycles', textarea: true },
]

interface SharedContextPanelProps {
  onSave?: (ctx: Partial<SharedContext>) => void
}

export default function SharedContextPanel({ onSave }: SharedContextPanelProps) {
  const { sharedContext, setSharedContext } = useApp()
  const [expanded, setExpanded] = useState<boolean>(true)
  const [saved, setSaved] = useState<boolean>(false)

  const isPopulated = sharedContext?.business_name || sharedContext?.product_description

  function handleChange(key: keyof SharedContext, value: string) {
    setSharedContext(prev => ({ ...prev, [key]: value }))
    setSaved(false)
  }

  function handleSave() {
    if (onSave) onSave(sharedContext)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border-color)',
      borderRadius: '8px',
      overflow: 'hidden',
      marginBottom: '16px',
    }}>
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        style={{
          width: '100%',
          padding: '14px 16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: 'transparent',
          border: 'none',
          cursor: 'pointer',
          color: 'var(--text-primary)',
          borderBottom: expanded ? '1px solid var(--border-color)' : 'none',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontSize: '16px' }}>📋</span>
          <div style={{ textAlign: 'left' }}>
            <div style={{ fontSize: '14px', fontWeight: 600 }}>Shared Business Context</div>
            {!expanded && isPopulated && (
              <div style={{ fontSize: '12px', color: 'var(--accent-primary)', marginTop: '2px' }}>
                {sharedContext.business_name || 'Context filled'} — auto-applied to all analyses
              </div>
            )}
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {isPopulated && (
            <span style={{
              fontSize: '11px',
              padding: '2px 8px',
              borderRadius: '4px',
              background: 'var(--badge-complete-bg)',
              color: 'var(--badge-complete-text)',
              fontWeight: 600,
            }}>
              ✓ Filled
            </span>
          )}
          <span style={{ color: 'var(--text-muted)', fontSize: '18px' }}>
            {expanded ? '▲' : '▼'}
          </span>
        </div>
      </button>

      {/* Form */}
      {expanded && (
        <div style={{ padding: '16px' }}>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', margin: '0 0 16px' }}>
            Fill once — this context automatically populates all 12 analysis prompts.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '12px' }}>
            {FIELDS.map(field => (
              <div key={field.key} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <label style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-secondary)' }}>
                  {field.label}
                </label>
                {field.type === 'select' ? (
                  <select
                    className="theme-input"
                    value={sharedContext[field.key] || ''}
                    onChange={e => handleChange(field.key, e.target.value)}
                    style={{ height: '36px' }}
                  >
                    <option value="">Select stage…</option>
                    {field.options.map(o => (
                      <option key={o} value={o}>{o}</option>
                    ))}
                  </select>
                ) : field.textarea ? (
                  <textarea
                    className="theme-input"
                    rows={2}
                    placeholder={field.placeholder}
                    value={sharedContext[field.key] || ''}
                    onChange={e => handleChange(field.key, e.target.value)}
                    style={{ resize: 'vertical', minHeight: '60px' }}
                  />
                ) : (
                  <input
                    className="theme-input"
                    type="text"
                    placeholder={field.placeholder}
                    value={sharedContext[field.key] || ''}
                    onChange={e => handleChange(field.key, e.target.value)}
                  />
                )}
              </div>
            ))}
          </div>

          <div style={{ marginTop: '16px', display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
            <button
              className="theme-btn-secondary"
              onClick={() => setExpanded(false)}
            >
              Collapse
            </button>
            <button
              className="theme-btn-primary"
              onClick={handleSave}
            >
              {saved ? '✓ Saved' : 'Save Context'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

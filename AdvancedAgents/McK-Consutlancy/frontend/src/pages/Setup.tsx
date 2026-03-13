import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../App'
import ThemeToggle from '../components/ThemeToggle'
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

const SHARED_CONTEXT_FIELDS: Field[] = [
  { key: 'business_name', label: 'Business Name', placeholder: 'e.g. AcmeCorp AI' },
  { key: 'product_description', label: 'Product / Service', placeholder: 'e.g. AI-powered CRM for SMBs', textarea: true },
  { key: 'industry', label: 'Industry', placeholder: 'e.g. B2B SaaS / Healthcare Tech' },
  {
    key: 'stage', label: 'Company Stage', type: 'select',
    options: ['Idea', 'MVP', 'Early Traction', 'Growth', 'Scale', 'Enterprise'],
  },
  { key: 'target_customer', label: 'Target Customer', placeholder: 'e.g. SMB operations managers' },
  { key: 'geography', label: 'Primary Market', placeholder: 'e.g. North America, Global' },
  { key: 'revenue', label: 'Current Revenue', placeholder: 'e.g. $50k MRR or pre-revenue' },
  { key: 'team_size', label: 'Team Size', placeholder: 'e.g. 12 FTEs' },
  { key: 'main_challenge', label: 'Main Challenge', placeholder: 'e.g. Struggling with enterprise sales cycles', textarea: true },
]

export default function Setup() {
  const navigate = useNavigate()
  const { apiKey, setApiKey, sharedContext, setSharedContext, theme: _theme } = useApp()
  const [keyInput, setKeyInput] = useState<string>(apiKey || '')
  const [showKey, setShowKey] = useState<boolean>(false)
  const [error, setError] = useState<string>('')

  function handleContextChange(key: keyof SharedContext, value: string) {
    setSharedContext(prev => ({ ...prev, [key]: value }))
  }

  function handleContinue() {
    if (!keyInput.trim()) {
      setError('Please enter your Anthropic API key.')
      return
    }
    if (!keyInput.startsWith('sk-ant-')) {
      setError('API key should start with "sk-ant-". Please check your key.')
      return
    }
    setApiKey(keyInput.trim())
    setError('')
    navigate('/research')
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--bg-primary)',
      display: 'flex',
      alignItems: 'flex-start',
      justifyContent: 'center',
      padding: '40px 20px 60px',
    }}>
      <div style={{ width: '100%', maxWidth: '700px' }}>
        {/* Hero */}
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <div style={{ fontSize: '48px', marginBottom: '12px' }}>🏛️</div>
          <h1 style={{
            fontSize: '32px',
            fontWeight: 800,
            color: 'var(--text-primary)',
            margin: '0 0 8px',
            letterSpacing: '-0.5px',
          }}>
            NPI Strategy Suite
          </h1>
          <p style={{ fontSize: '16px', color: 'var(--text-secondary)', margin: 0 }}>
            12 AI-powered consulting frameworks • Professional-grade market research
          </p>
        </div>

        {/* API Key section */}
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: '12px',
          padding: '24px',
          marginBottom: '20px',
        }}>
          <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', margin: '0 0 6px' }}>
            🔑 Anthropic API Key
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: '0 0 14px' }}>
            Your key is stored locally only — never sent to any server except Anthropic's API.
          </p>
          <div style={{ display: 'flex', gap: '8px' }}>
            <input
              className="theme-input"
              type={showKey ? 'text' : 'password'}
              placeholder="sk-ant-api03-…"
              value={keyInput}
              onChange={e => { setKeyInput(e.target.value); setError('') }}
              onKeyDown={e => e.key === 'Enter' && handleContinue()}
              style={{ flex: 1 }}
            />
            <button
              className="theme-btn-secondary"
              onClick={() => setShowKey(!showKey)}
              style={{ flexShrink: 0, padding: '8px 12px' }}
            >
              {showKey ? '🙈' : '👁️'}
            </button>
          </div>
          {error && (
            <p style={{ color: '#fca5a5', fontSize: '13px', margin: '8px 0 0' }}>{error}</p>
          )}
          <p style={{ fontSize: '11px', color: 'var(--text-muted)', margin: '10px 0 0' }}>
            Get your key at console.anthropic.com → API Keys
          </p>
        </div>

        {/* Shared context section */}
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: '12px',
          padding: '24px',
          marginBottom: '20px',
        }}>
          <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', margin: '0 0 6px' }}>
            📋 Business Context <span style={{ fontSize: '13px', fontWeight: 400, color: 'var(--text-muted)' }}>(optional — can fill later)</span>
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', margin: '0 0 16px' }}>
            Fill once and it auto-populates all 12 analysis prompts.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '12px' }}>
            {SHARED_CONTEXT_FIELDS.map(field => (
              <div key={field.key} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <label style={{ fontSize: '12px', fontWeight: 500, color: 'var(--text-secondary)' }}>
                  {field.label}
                </label>
                {field.type === 'select' ? (
                  <select
                    className="theme-input"
                    value={sharedContext[field.key] || ''}
                    onChange={e => handleContextChange(field.key, e.target.value)}
                    style={{ height: '36px' }}
                  >
                    <option value="">Select…</option>
                    {field.options.map(o => <option key={o} value={o}>{o}</option>)}
                  </select>
                ) : field.textarea ? (
                  <textarea
                    className="theme-input"
                    rows={2}
                    placeholder={field.placeholder}
                    value={sharedContext[field.key] || ''}
                    onChange={e => handleContextChange(field.key, e.target.value)}
                    style={{ resize: 'vertical', minHeight: '60px' }}
                  />
                ) : (
                  <input
                    className="theme-input"
                    type="text"
                    placeholder={field.placeholder}
                    value={sharedContext[field.key] || ''}
                    onChange={e => handleContextChange(field.key, e.target.value)}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Theme selection */}
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: '12px',
          padding: '24px',
          marginBottom: '24px',
        }}>
          <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)', margin: '0 0 14px' }}>
            🎨 UI Theme
          </h2>
          <ThemeToggle />
        </div>

        {/* CTA */}
        <button
          className="theme-btn-primary glow-accent"
          onClick={handleContinue}
          style={{
            width: '100%',
            padding: '14px',
            fontSize: '16px',
            fontWeight: 700,
            borderRadius: '10px',
          }}
        >
          Launch Research Suite →
        </button>
      </div>
    </div>
  )
}

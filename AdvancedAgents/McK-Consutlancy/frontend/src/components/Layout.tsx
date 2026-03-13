import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useApp } from '../App'
import ThemeToggle from './ThemeToggle'

interface LayoutProps {
  children: React.ReactNode
  title?: string
  actions?: React.ReactNode
}

export default function Layout({ children, title, actions }: LayoutProps) {
  const { apiKey, setApiKey } = useApp()
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: 'var(--bg-primary)' }}>
      {/* Top bar */}
      <header style={{
        height: '52px',
        background: 'var(--bg-secondary)',
        borderBottom: '1px solid var(--border-color)',
        display: 'flex',
        alignItems: 'center',
        padding: '0 20px',
        gap: '16px',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}>
        <div
          onClick={() => navigate('/research')}
          style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}
        >
          <span style={{ fontSize: '20px' }}>🏛️</span>
          <span style={{
            fontSize: '14px',
            fontWeight: 800,
            color: 'var(--accent-primary)',
            letterSpacing: '0.04em',
          }}>
            NPI Strategy Suite
          </span>
        </div>

        {title && (
          <div style={{
            fontSize: '14px',
            color: 'var(--text-secondary)',
            paddingLeft: '12px',
            borderLeft: '1px solid var(--border-color)',
          }}>
            {title}
          </div>
        )}

        <div style={{ flex: 1 }} />

        {/* Nav links */}
        <nav style={{ display: 'flex', gap: '4px' }}>
          {[
            { path: '/research', label: 'Research' },
            { path: '/history', label: 'History' },
            { path: '/setup', label: 'Settings' },
          ].map(link => (
            <button
              key={link.path}
              onClick={() => navigate(link.path)}
              style={{
                background: location.pathname === link.path
                  ? 'color-mix(in srgb, var(--accent-primary) 15%, transparent)'
                  : 'transparent',
                border: 'none',
                borderRadius: '6px',
                padding: '5px 12px',
                color: location.pathname === link.path ? 'var(--accent-primary)' : 'var(--text-secondary)',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: location.pathname === link.path ? 600 : 400,
                transition: 'all 0.15s',
              }}
            >
              {link.label}
            </button>
          ))}
        </nav>

        {actions && <div>{actions}</div>}
      </header>

      {/* Page content */}
      <main style={{ flex: 1 }}>
        {children}
      </main>
    </div>
  )
}

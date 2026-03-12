import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface OutputRendererProps {
  content: string
  isStreaming?: boolean
}

export default function OutputRenderer({ content, isStreaming = false }: OutputRendererProps) {
  if (!content) return null

  return (
    <div className={`markdown-output ${isStreaming ? 'streaming-cursor' : ''}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Tables
          table: ({ children }) => (
            <div style={{ overflowX: 'auto', margin: '16px 0' }}>
              <table>{children}</table>
            </div>
          ),
          // Code blocks
          code: ({ node: _node, className, children, ...props }: {
            node?: unknown
            inline?: boolean
            className?: string
            children?: React.ReactNode
            [key: string]: unknown
          }) => {
            const inline = props['inline'] as boolean | undefined
            if (inline) {
              return <code className={className} {...(props as React.HTMLAttributes<HTMLElement>)}>{children}</code>
            }
            return (
              <pre>
                <code className={className} {...(props as React.HTMLAttributes<HTMLElement>)}>{children}</code>
              </pre>
            )
          },
          // Links open in new tab
          a: ({ children, href }) => (
            <a href={href} target="_blank" rel="noopener noreferrer"
              style={{ color: 'var(--accent-primary)', textDecoration: 'underline' }}>
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

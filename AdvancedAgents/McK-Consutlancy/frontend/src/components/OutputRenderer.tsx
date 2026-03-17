import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface OutputRendererProps {
  content: string
  isStreaming?: boolean
}

function unwrapCodeBlockTables(text: string): string {
  // If a fenced code block's body is entirely pipe-table lines, strip the fences
  // so ReactMarkdown + remarkGfm renders them as HTML tables instead of <pre><code>
  return text.replace(
    /```[^\n]*\n((?:\|[^\n]+\n)+)```/g,
    '$1'
  )
}

export default function OutputRenderer({ content, isStreaming = false }: OutputRendererProps) {
  if (!content) return null

  const processedContent = unwrapCodeBlockTables(content)

  return (
    <div className={`markdown-output ${isStreaming ? 'streaming-cursor' : ''}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Tables
          table: ({ children }) => (
            <div style={{ border: '1px solid var(--border-color)', borderRadius: '8px', overflow: 'hidden', margin: '16px 0' }}>
              <div style={{ overflowX: 'auto' }}>
                <table>{children}</table>
              </div>
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
        {processedContent}
      </ReactMarkdown>
    </div>
  )
}

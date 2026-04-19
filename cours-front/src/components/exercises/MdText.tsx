import { useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import renderMathInElement from 'katex/contrib/auto-render'
import 'katex/dist/katex.min.css'

interface Props {
  children: string
}

/**
 * Rendu inline : markdown (gras, italique…) + KaTeX ($...$).
 * Utilisé pour les questions, options et explications des exercices.
 */
export default function MdText({ children }: Props) {
  const ref = useRef<HTMLSpanElement>(null)

  useEffect(() => {
    if (!ref.current) return
    renderMathInElement(ref.current, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '$', right: '$', display: false },
      ],
      throwOnError: false,
    })
  }, [children])

  return (
    <span ref={ref}>
      <ReactMarkdown components={{ p: ({ children }) => <>{children}</> }}>
        {children}
      </ReactMarkdown>
    </span>
  )
}

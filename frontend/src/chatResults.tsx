import { createContext, useContext, useState, type ReactNode } from 'react'
import type { Product } from './types'

/**
 * Shared state that lets the floating chat widget push product matches onto the
 * page. The ChatPanel writes results here; the Products page reads them and
 * renders them as cards. Kept in context (not local state) because the chat and
 * the page are different parts of the tree.
 */
interface ChatResultsState {
  results: Product[]
  query: string | null
  show: (query: string, results: Product[]) => void
  clear: () => void
}

const ChatResultsContext = createContext<ChatResultsState | null>(null)

export function ChatResultsProvider({ children }: { children: ReactNode }) {
  const [results, setResults] = useState<Product[]>([])
  const [query, setQuery] = useState<string | null>(null)

  function show(nextQuery: string, nextResults: Product[]) {
    setQuery(nextQuery)
    setResults(nextResults)
  }

  function clear() {
    setQuery(null)
    setResults([])
  }

  return (
    <ChatResultsContext.Provider value={{ results, query, show, clear }}>
      {children}
    </ChatResultsContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useChatResults(): ChatResultsState {
  const context = useContext(ChatResultsContext)
  if (!context) {
    throw new Error('useChatResults must be used within a ChatResultsProvider')
  }
  return context
}

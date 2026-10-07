import { useEffect, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import { fetchChatHistory, sendChatMessage } from '../api'
import { useAuth } from '../auth'
import { useChatResults } from '../chatResults'
import type { ChatMessage } from '../types'

const GREETING: ChatMessage = {
  role: 'assistant',
  content:
    "Hi! I'm the Campus Customs shop assistant. Ask me about sizes, colors, " +
    'or what to get someone, and I\'ll point you to the right gear.',
}

/** Pull the product id out of the path when on a product detail page. */
function currentProductId(pathname: string): string | null {
  const match = pathname.match(/^\/products\/(.+)$/)
  return match ? match[1] : null
}

export default function ChatPanel() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([GREETING])
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const logRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useAuth()
  const chatResults = useChatResults()

  // Reload saved history when a shopper signs in; reset to the greeting on
  // sign-out. Keyed on the user id so it runs on login/logout, not every render.
  useEffect(() => {
    if (!user) {
      setMessages([GREETING])
      return
    }
    fetchChatHistory().then((history) => {
      setMessages(history.length ? [GREETING, ...history] : [GREETING])
    })
  }, [user?.id])

  // Keep the newest message in view as the conversation grows.
  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, open])

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    const text = draft.trim()
    if (!text || sending) return

    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setDraft('')
    setSending(true)

    try {
      const pageId = currentProductId(location.pathname)
      const reply = await sendChatMessage(text, pageId)

      // Don't surface the product the shopper is already viewing as a "result":
      // answering "is this in white?" should not yank them to a page showing the
      // same item. Only products they are not already looking at update the page.
      const pageResults = (reply.products ?? []).filter(
        (product) => product.product_id !== pageId,
      )

      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: reply.reply, products: pageResults },
      ])

      if (pageResults.length > 0) {
        chatResults.show(text, pageResults)
        navigate('/products')
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            "Sorry, I couldn't reach the shop assistant. Make sure the backend " +
            'is running on port 8000 and try again.',
        },
      ])
    } finally {
      setSending(false)
    }
  }

  if (!open) {
    return (
      <button
        className="chat-launcher"
        onClick={() => setOpen(true)}
        aria-label="Open shop assistant chat"
      >
        <span className="chat-launcher-icon" aria-hidden="true">
          💬
        </span>
        Ask us anything
      </button>
    )
  }

  return (
    <div className="chat-panel" role="dialog" aria-label="Shop assistant">
      <div className="chat-head">
        <div className="chat-ident">
          <span className="chat-avatar" aria-hidden="true">CC</span>
          <div>
            <div className="title">
              Shop Assistant <span className="online-dot" aria-hidden="true" />
            </div>
            <div className="sub">Usually replies in a few seconds</div>
          </div>
        </div>
        <button className="chat-close" onClick={() => setOpen(false)} aria-label="Close chat">
          &times;
        </button>
      </div>

      <div className="chat-log" ref={logRef}>
        {messages.map((message, index) => (
          <div key={index} className={`bubble ${message.role}`}>
            {message.role === 'assistant' ? (
              <div className="md">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            ) : (
              message.content
            )}
            {message.products && message.products.length > 0 && (
              <div className="bubble-note">
                Showing {message.products.length}{' '}
                {message.products.length === 1 ? 'item' : 'items'} on the page.
              </div>
            )}
          </div>
        ))}
        {sending && <div className="bubble assistant typing">Typing...</div>}
      </div>

      <form className="chat-form" onSubmit={handleSubmit}>
        <input
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="What hoodies do you have?"
          aria-label="Message"
          disabled={sending}
        />
        <button type="submit" className="chat-send" disabled={sending || !draft.trim()}>
          Send
        </button>
      </form>
    </div>
  )
}

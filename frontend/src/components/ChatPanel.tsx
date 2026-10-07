import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { sendChatMessage } from '../api'
import { useChatResults } from '../chatResults'
import type { ChatMessage } from '../types'

const GREETING: ChatMessage = {
  role: 'assistant',
  content:
    "Hi! I'm the Campus Customs shop assistant. Ask me about sizes, colors, " +
    'or what to get someone, and I\'ll point you to the right gear.',
}

export default function ChatPanel() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([GREETING])
  const [draft, setDraft] = useState('')
  const [sending, setSending] = useState(false)
  const logRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()
  const chatResults = useChatResults()

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
      const reply = await sendChatMessage(text)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: reply.reply, products: reply.products },
      ])
      // When the agent returns product matches, show them as cards on the
      // Products page and take the shopper there. The floating panel stays open
      // on top, so the conversation continues.
      if (reply.products && reply.products.length > 0) {
        chatResults.show(text, reply.products)
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
        Ask us anything
      </button>
    )
  }

  return (
    <div className="chat-panel" role="dialog" aria-label="Shop assistant">
      <div className="chat-head">
        <div>
          <div className="title">Shop Assistant</div>
          <div className="sub">Ask us anything about our gear</div>
        </div>
        <button className="chat-close" onClick={() => setOpen(false)} aria-label="Close chat">
          &times;
        </button>
      </div>

      <div className="chat-log" ref={logRef}>
        {messages.map((message, index) => (
          <div key={index} className={`bubble ${message.role}`}>
            {message.content}
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

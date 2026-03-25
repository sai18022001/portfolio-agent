// frontend/src/App.jsx

import { useState, useRef, useEffect } from "react"
import axios from "axios"

const API_BASE = "http://localhost:8000"

// Generates a random session ID for each browser tab
const generateSessionId = () => crypto.randomUUID()

export default function App() {
  const [messages, setMessages]     = useState([])
  const [input, setInput]           = useState("")
  const [loading, setLoading]       = useState(false)
  const [sessionId, setSessionId]   = useState(generateSessionId)
  const bottomRef                   = useRef(null)

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loading])

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || loading) return

    // Add user message immediately to UI
    const userMsg = { role: "human", content: text }
    setMessages(prev => [...prev, userMsg])
    setInput("")
    setLoading(true)

    try {
      const res = await axios.post(`${API_BASE}/chat`, {
        message: text,
        session_id: sessionId
      })

      const agentMsg = { role: "ai", content: res.data.answer }
      setMessages(prev => [...prev, agentMsg])

    } catch (err) {
      const detail = err.response?.data?.detail || "Something went wrong."
      const errorMsg = {
        role: "ai",
        content: detail
      }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }

  const newChat = async () => {
    // Clear MongoDB memory for this session
    await axios.delete(`${API_BASE}/session/${sessionId}`)
    // Generate fresh session
    setSessionId(generateSessionId())
    setMessages([])
  }

  const handleKeyDown = (e) => {
    // Send on Enter, new line on Shift+Enter
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div style={styles.app}>

      {/* ---- Header ---- */}
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>Portfolio Research Agent</h1>
          <p style={styles.subtitle}>Powered by Gemini + RAG + Live Market Data</p>
        </div>
        <button onClick={newChat} style={styles.newChatBtn}>
          New Chat
        </button>
      </div>

      {/* ---- Messages area ---- */}
      <div style={styles.messages}>

        {/* Welcome message */}
        {messages.length === 0 && (
          <div style={styles.welcome}>
            <p style={styles.welcomeTitle}>Ask me anything about your portfolio</p>
            <div style={styles.suggestions}>
              {[
                "What are Apple's main business risks?",
                "What is AAPL's current stock price?",
                "Compare Apple and Microsoft risk profiles",
                "What did Apple say about AI in their 10-K?"
              ].map(s => (
                <button
                  key={s}
                  style={styles.suggestion}
                  onClick={() => setInput(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Chat messages */}
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              ...styles.messageRow,
              justifyContent: msg.role === "human" ? "flex-end" : "flex-start"
            }}
          >
            {msg.role === "ai" && (
              <div style={styles.avatar}>AI</div>
            )}
            <div style={{
              ...styles.bubble,
              ...(msg.role === "human" ? styles.humanBubble : styles.aiBubble)
            }}>
              {/* Render markdown-like bold text */}
              <MessageContent content={msg.content} />
            </div>
            {msg.role === "human" && (
              <div style={{ ...styles.avatar, background: "#6366f1" }}>You</div>
            )}
          </div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <div style={styles.messageRow}>
            <div style={styles.avatar}>AI</div>
            <div style={{ ...styles.bubble, ...styles.aiBubble }}>
              <div style={styles.typing}>
                <span style={styles.dot} />
                <span style={{ ...styles.dot, animationDelay: "0.2s" }} />
                <span style={{ ...styles.dot, animationDelay: "0.4s" }} />
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* ---- Input area ---- */}
      <div style={styles.inputArea}>
        <textarea
          style={styles.textarea}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about portfolio risks, stock prices, earnings reports..."
          rows={2}
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          style={{
            ...styles.sendBtn,
            opacity: loading || !input.trim() ? 0.5 : 1
          }}
        >
          {loading ? "..." : "Send"}
        </button>
      </div>

    </div>
  )
}

// Renders **bold** markdown in agent responses
function MessageContent({ content }) {
  const parts = content.split(/(\*\*[^*]+\*\*)/)
  return (
    <p style={{ margin: 0, whiteSpace: "pre-wrap", lineHeight: 1.6 }}>
      {parts.map((part, i) =>
        part.startsWith("**") && part.endsWith("**")
          ? <strong key={i}>{part.slice(2, -2)}</strong>
          : part
      )}
    </p>
  )
}

// ---- Styles ----
const styles = {
  app: {
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    maxWidth: 800,
    margin: "0 auto",
    fontFamily: "system-ui, sans-serif",
    background: "#0f0f0f",
    color: "#f0f0f0",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "16px 24px",
    borderBottom: "1px solid #2a2a2a",
  },
  title: {
    margin: 0,
    fontSize: 20,
    fontWeight: 600,
    color: "#f0f0f0",
  },
  subtitle: {
    margin: "4px 0 0",
    fontSize: 12,
    color: "#666",
  },
  newChatBtn: {
    padding: "8px 16px",
    background: "transparent",
    border: "1px solid #333",
    borderRadius: 8,
    color: "#aaa",
    cursor: "pointer",
    fontSize: 13,
  },
  messages: {
    flex: 1,
    overflowY: "auto",
    padding: "24px 16px",
    display: "flex",
    flexDirection: "column",
    gap: 16,
  },
  welcome: {
    textAlign: "center",
    marginTop: 60,
  },
  welcomeTitle: {
    fontSize: 18,
    color: "#aaa",
    marginBottom: 24,
  },
  suggestions: {
    display: "flex",
    flexDirection: "column",
    gap: 10,
    alignItems: "center",
  },
  suggestion: {
    padding: "10px 20px",
    background: "#1a1a1a",
    border: "1px solid #2a2a2a",
    borderRadius: 8,
    color: "#ccc",
    cursor: "pointer",
    fontSize: 13,
    maxWidth: 420,
    width: "100%",
    textAlign: "left",
  },
  messageRow: {
    display: "flex",
    gap: 10,
    alignItems: "flex-start",
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: "50%",
    background: "#1d9e75",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 10,
    fontWeight: 700,
    flexShrink: 0,
    color: "#fff",
  },
  bubble: {
    maxWidth: "75%",
    padding: "12px 16px",
    borderRadius: 12,
    fontSize: 14,
    lineHeight: 1.6,
  },
  humanBubble: {
    background: "#6366f1",
    color: "#fff",
    borderBottomRightRadius: 4,
  },
  aiBubble: {
    background: "#1a1a1a",
    border: "1px solid #2a2a2a",
    color: "#e0e0e0",
    borderBottomLeftRadius: 4,
  },
  typing: {
    display: "flex",
    gap: 4,
    alignItems: "center",
    height: 20,
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: "50%",
    background: "#666",
    animation: "bounce 1s infinite",
  },
  inputArea: {
    display: "flex",
    gap: 10,
    padding: "16px",
    borderTop: "1px solid #2a2a2a",
    alignItems: "flex-end",
  },
  textarea: {
    flex: 1,
    padding: "12px",
    background: "#1a1a1a",
    border: "1px solid #2a2a2a",
    borderRadius: 10,
    color: "#f0f0f0",
    fontSize: 14,
    resize: "none",
    outline: "none",
    fontFamily: "inherit",
  },
  sendBtn: {
    padding: "12px 20px",
    background: "#6366f1",
    border: "none",
    borderRadius: 10,
    color: "#fff",
    fontWeight: 600,
    cursor: "pointer",
    fontSize: 14,
  },
}
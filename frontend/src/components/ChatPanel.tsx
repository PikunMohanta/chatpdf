import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import io, { Socket } from 'socket.io-client'
import './ChatPanel.css'

interface Message {
  id: string
  text: string
  from: 'user' | 'ai'
  timestamp: Date
  sources?: Array<{ page: number; text: string }>
}

interface ChatPanelProps {
  documentId: string
  documentName: string
  onSourceClick: (pageNumber: number) => void
}

const ChatPanel = ({ documentId, documentName, onSourceClick }: ChatPanelProps) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [socket, setSocket] = useState<Socket | null>(null)
  const [connected, setConnected] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const newSocket = io('http://localhost:8000', {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    })

    newSocket.on('connect', () => {
      console.log('Socket connected:', newSocket.id)
      setConnected(true)
    })

    newSocket.on('disconnect', () => {
      console.log('Socket disconnected')
      setConnected(false)
    })

    newSocket.on('response', (data: { response: string; document_id: string }) => {
      console.log('Received response:', data)
      setIsTyping(false)

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          text: data.response,
          from: 'ai',
          timestamp: new Date(),
        },
      ])
    })

    newSocket.on('error', (error: { message: string }) => {
      console.error('Socket error:', error)
      setIsTyping(false)

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          text: `Error: ${error.message}`,
          from: 'ai',
          timestamp: new Date(),
        },
      ])
    })

    setSocket(newSocket)

    return () => {
      newSocket.close()
    }
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSendMessage = () => {
    if (!input.trim() || !socket || !connected) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      from: 'user',
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsTyping(true)

    socket.emit('query', {
      document_id: documentId,
      query: input,
    })
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <div className="chat-header-info">
          <h3 className="chat-title">{documentName}</h3>
          <div className={`connection-status ${connected ? 'connected' : 'disconnected'}`}>
            <span className="status-dot" />
            {connected ? 'Connected' : 'Disconnected'}
          </div>
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="empty-icon">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="1.5"
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                />
              </svg>
              <p className="empty-text">Start a conversation</p>
              <p className="empty-subtext">Ask questions about your PDF document</p>
            </motion.div>
          </div>
        ) : (
          <>
            <AnimatePresence>
              {messages.map((message, index) => (
                <motion.div
                  key={message.id}
                  className={`message ${message.from}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                >
                  <div className="message-avatar">
                    {message.from === 'user' ? (
                      <img
                        src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix"
                        alt="User"
                        className="avatar"
                      />
                    ) : (
                      <div className="ai-avatar">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                          />
                        </svg>
                      </div>
                    )}
                  </div>

                  <div className="message-content">
                    <p className="message-text">{message.text}</p>
                    {message.sources && message.sources.length > 0 && (
                      <div className="message-sources">
                        {message.sources.map((source, idx) => (
                          <motion.button
                            key={idx}
                            className="source-chip"
                            onClick={() => onSourceClick(source.page)}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                          >
                            Page {source.page}
                          </motion.button>
                        ))}
                      </div>
                    )}
                    <span className="message-time">
                      {message.timestamp.toLocaleTimeString('en-US', {
                        hour: 'numeric',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {isTyping && (
              <motion.div
                className="message ai typing"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="message-avatar">
                  <div className="ai-avatar">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                      />
                    </svg>
                  </div>
                </div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <div className="chat-input-container">
        <div className="chat-input-wrapper">
          <textarea
            className="chat-input"
            placeholder="Ask a question about your PDF..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={!connected}
            rows={1}
          />
          <motion.button
            className="send-button"
            onClick={handleSendMessage}
            disabled={!input.trim() || !connected}
            whileHover={input.trim() && connected ? { scale: 1.05 } : {}}
            whileTap={input.trim() && connected ? { scale: 0.95 } : {}}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </motion.button>
        </div>
      </div>
    </div>
  )
}

export default ChatPanel

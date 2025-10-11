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
  chatName?: string
  sessionId?: string
  onSourceClick: (pageNumber: number) => void
  onGenerateChatName?: (query: string) => void
  onSessionIdReceived?: (sessionId: string) => void
}

const ChatPanel = ({ documentId, documentName, chatName, sessionId, onSourceClick, onGenerateChatName, onSessionIdReceived }: ChatPanelProps) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [socket, setSocket] = useState<Socket | null>(null)
  const [connected, setConnected] = useState(false)
  const [currentSessionId, setCurrentSessionId] = useState<string | undefined>(sessionId)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Load chat history when session changes
  useEffect(() => {
    const loadChatHistory = async () => {
      console.log('🔄 Session ID changed:', { sessionId, documentId })
      
      // Skip if no session ID or if it's a temporary ID
      if (!sessionId || sessionId.startsWith('temp_')) {
        console.log('📄 Temporary or no session ID - starting fresh chat')
        setMessages([])
        setCurrentSessionId(sessionId)
        return
      }

      try {
        console.log('📥 Attempting to load chat history for session:', sessionId)
        const response = await fetch(`http://localhost:8000/api/chat/history/${sessionId}`)
        
        console.log('📡 History API response status:', response.status)
        
        if (response.ok) {
          const data = await response.json()
          console.log('📦 Received data:', { 
            messageCount: data.messages?.length || 0, 
            sessionId: data.session_id,
            documentId: data.document_id 
          })
          
          const loadedMessages: Message[] = data.messages.map((msg: any) => ({
            id: msg.message_id,
            text: msg.text,
            from: msg.sender as 'user' | 'ai',
            timestamp: new Date(msg.timestamp),
            sources: msg.sources ? msg.sources.map((s: string) => ({ text: s })) : undefined
          }))
          
          setMessages(loadedMessages)
          setCurrentSessionId(sessionId)
          console.log(`✅ Successfully loaded ${loadedMessages.length} messages from history`)
        } else {
          const errorText = await response.text()
          console.warn('⚠️ No chat history found:', { sessionId, status: response.status, error: errorText })
          setMessages([])
          setCurrentSessionId(sessionId)
        }
      } catch (error) {
        console.error('❌ Error loading chat history:', error)
        setMessages([])
        setCurrentSessionId(sessionId)
      }
    }

    loadChatHistory()
    setInput('')
    setIsTyping(false)
  }, [sessionId, documentId])

  useEffect(() => {
    console.log('🔌 Initializing Socket.IO connection to http://localhost:8000')
    
    const newSocket = io('http://localhost:8000', {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      timeout: 10000,
    })

    newSocket.on('connect', () => {
      console.log('✅ Socket connected:', newSocket.id)
      setConnected(true)
    })

    newSocket.on('connect_error', (error) => {
      console.error('❌ Socket connection error:', error.message)
      console.error('Error details:', error)
      setConnected(false)
    })

    newSocket.on('disconnect', (reason) => {
      console.log('🔌 Socket disconnected. Reason:', reason)
      setConnected(false)
    })

    newSocket.on('response', (data: { response: string; document_id: string; session_id?: string }) => {
      console.log('📨 Received response from backend:', {
        hasResponse: !!data.response,
        sessionId: data.session_id,
        documentId: data.document_id,
        currentSessionId
      })
      setIsTyping(false)

      // Update session ID if received from server
      if (data.session_id) {
        const needsUpdate = !currentSessionId || currentSessionId.startsWith('temp_')
        console.log('� Session ID check:', {
          receivedId: data.session_id,
          currentId: currentSessionId,
          needsUpdate
        })
        
        if (needsUpdate) {
          console.log('📌 Updating session ID from', currentSessionId, 'to', data.session_id)
          setCurrentSessionId(data.session_id)
          
          // Notify parent component to update the session in localStorage
          if (onSessionIdReceived) {
            console.log('🔔 Notifying parent of new session ID')
            onSessionIdReceived(data.session_id)
          }
        }
      }

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

    const queryText = input
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsTyping(true)

    // Generate chat name from first message
    if (messages.length === 0 && onGenerateChatName) {
      onGenerateChatName(queryText)
    }

    console.log('📤 Sending query to backend:', {
      documentId,
      sessionId: currentSessionId,
      queryLength: queryText.length,
      isFirstMessage: messages.length === 0
    })

    socket.emit('query', {
      document_id: documentId,
      query: queryText,
      session_id: currentSessionId,
      user_id: 'anonymous', // TODO: Replace with actual user ID from auth
    })
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const displayChatName = chatName || `Chat about ${documentName}`

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <div className="chat-header-info">
          <h3 className="chat-title">{displayChatName}</h3>
          <div className="chat-document-info">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="pdf-icon-header">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            <span className="chat-document-name">{documentName}</span>
          </div>
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
              className="empty-state-content"
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
              
              {/* Centered Search Bar */}
              <div className="centered-input-wrapper">
                <textarea
                  className="centered-chat-input"
                  placeholder="Message PDF Pal..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={!connected}
                  rows={1}
                />
                <motion.button
                  className="centered-send-button"
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

      {/* Only show bottom input when messages exist */}
      {messages.length > 0 && (
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
      )}
    </div>
  )
}

export default ChatPanel

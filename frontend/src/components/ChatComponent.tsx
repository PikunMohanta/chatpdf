import { useState, useEffect, useRef } from 'react'
import { io, Socket } from 'socket.io-client'
import axios from 'axios'
import './ChatComponent.css'

interface ChatComponentProps {
  documentId: string
}

interface Message {
  id: string
  text: string
  sender: 'user' | 'ai'
  timestamp: Date
}

const ChatComponent = ({ documentId }: ChatComponentProps) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [loading, setLoading] = useState(false)
  const [socket, setSocket] = useState<Socket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const suggestedQuestions = [
    'What is this document about?',
    'Summarize the key points',
    'What are the main conclusions?',
  ]

  // Initialize WebSocket connection
  useEffect(() => {
    const newSocket = io(import.meta.env.VITE_SOCKET_URL, {
      transports: ['websocket', 'polling'],
    })

    newSocket.on('connect', () => {
      console.log('Connected to chat server')
    })

    newSocket.on('response', (data: { message: string }) => {
      setIsTyping(false)
      addMessage(data.message, 'ai')
    })

    newSocket.on('error', (error: { message: string }) => {
      setIsTyping(false)
      addMessage(`Error: ${error.message}`, 'ai')
    })

    setSocket(newSocket)

    return () => {
      newSocket.close()
    }
  }, [])

  // Load chat history
  useEffect(() => {
    if (documentId) {
      loadChatHistory()
    }
  }, [documentId])

  // Auto-scroll to bottom
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const loadChatHistory = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('auth_token') || 'dev-token'
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL}/api/chat/history/${documentId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      )
      
      if (response.data.history && response.data.history.length > 0) {
        const loadedMessages: Message[] = response.data.history.map((msg: any, index: number) => ({
          id: `${Date.now()}-${index}`,
          text: msg.content || msg.text,
          sender: msg.role === 'user' ? 'user' : 'ai',
          timestamp: new Date(),
        }))
        setMessages(loadedMessages)
      }
    } catch (err) {
      console.error('Failed to load chat history:', err)
    } finally {
      setLoading(false)
    }
  }

  const addMessage = (text: string, sender: 'user' | 'ai') => {
    const newMessage: Message = {
      id: `${Date.now()}-${Math.random()}`,
      text,
      sender,
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, newMessage])
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = async (text?: string) => {
    const messageText = text || inputValue.trim()
    if (!messageText || !socket) return

    addMessage(messageText, 'user')
    setInputValue('')
    setIsTyping(true)

    // Send via WebSocket
    socket.emit('query', {
      document_id: documentId,
      query: messageText,
    })
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="chat-component">
      <div className="chat-header">
        <h3>💬 Chat with Document</h3>
        <span className="status-indicator">
          <span className={`status-dot ${socket?.connected ? 'connected' : 'disconnected'}`}></span>
          {socket?.connected ? 'Connected' : 'Disconnected'}
        </span>
      </div>

      <div className="messages-container">
        {loading ? (
          <div className="loading-history">
            <div className="spinner-small"></div>
            <p>Loading chat history...</p>
          </div>
        ) : messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🤖</div>
            <h4>Start a conversation!</h4>
            <p>Ask me anything about this document</p>
            <div className="suggested-questions">
              {suggestedQuestions.map((question, index) => (
                <button
                  key={index}
                  className="suggested-btn"
                  onClick={() => handleSendMessage(question)}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.sender}`}>
                <div className="message-avatar">
                  {message.sender === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content">
                  <div className="message-text">{message.text}</div>
                  <div className="message-time">
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="message ai typing">
                <div className="message-avatar">🤖</div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <textarea
          className="chat-input"
          placeholder="Ask a question about the document..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          rows={2}
          disabled={!socket?.connected}
        />
        <button
          className="send-button"
          onClick={() => handleSendMessage()}
          disabled={!inputValue.trim() || !socket?.connected}
        >
          <span className="send-icon">📤</span>
          Send
        </button>
      </div>
    </div>
  )
}

export default ChatComponent

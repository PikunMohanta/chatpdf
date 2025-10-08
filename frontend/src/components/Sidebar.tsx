import { useState } from 'react'
import { motion } from 'framer-motion'
import { ChatSession } from '../App'
import './Sidebar.css'

interface SidebarProps {
  chatSessions: ChatSession[]
  currentSessionId: string
  onNewChat: () => void
  onSelectSession: (session: ChatSession) => void
  onDeleteSession: (sessionId: string) => void
  onUpdateChatName?: (sessionId: string, newName: string) => void
}

const Sidebar = ({
  chatSessions,
  currentSessionId,
  onNewChat,
  onSelectSession,
  onDeleteSession,
  onUpdateChatName,
}: SidebarProps) => {
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null)
  const [editingName, setEditingName] = useState<string>('')

  const formatDate = (isoString: string) => {
    const date = new Date(isoString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))
    
    if (hours < 24) return 'Today'
    if (hours < 48) return 'Yesterday'
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  const handleStartEdit = (session: ChatSession, e: React.MouseEvent) => {
    e.stopPropagation()
    setEditingSessionId(session.session_id)
    setEditingName(session.chat_name || `Chat about ${session.document_name}`)
  }

  const handleSaveEdit = (sessionId: string) => {
    if (onUpdateChatName && editingName.trim()) {
      onUpdateChatName(sessionId, editingName.trim())
    }
    setEditingSessionId(null)
    setEditingName('')
  }

  const handleCancelEdit = () => {
    setEditingSessionId(null)
    setEditingName('')
  }

  const handleKeyPress = (e: React.KeyboardEvent, sessionId: string) => {
    if (e.key === 'Enter') {
      handleSaveEdit(sessionId)
    } else if (e.key === 'Escape') {
      handleCancelEdit()
    }
  }

  return (
    <div className="sidebar">
      <motion.button
        className="new-chat-button"
        onClick={onNewChat}
        whileHover={{ scale: 1.02, boxShadow: '0 4px 12px rgba(79, 70, 229, 0.2)' }}
        whileTap={{ scale: 0.98 }}
      >
        <span className="new-chat-icon">+</span>
        New Chat
      </motion.button>

      <div className="chat-history">
        <h3 className="chat-history-title">Recent Chats</h3>
        <div className="chat-history-list">
          {chatSessions.length === 0 ? (
            <p className="no-chats">No previous chats</p>
          ) : (
            chatSessions.map((session) => {
              const isEditing = editingSessionId === session.session_id
              const displayName = session.chat_name || `Chat about ${session.document_name}`
              
              return (
                <motion.div
                  key={session.session_id}
                  className={`chat-session-item ${session.document_id === currentSessionId ? 'active' : ''}`}
                  onClick={() => !isEditing && onSelectSession(session)}
                  whileHover={{ x: 4, backgroundColor: 'rgba(79, 70, 229, 0.05)' }}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                >
                  <div className="session-info">
                    {isEditing ? (
                      <div className="session-name-edit" onClick={(e) => e.stopPropagation()}>
                        <input
                          type="text"
                          className="session-name-input"
                          value={editingName}
                          onChange={(e) => setEditingName(e.target.value)}
                          onKeyDown={(e) => handleKeyPress(e, session.session_id)}
                          onBlur={() => handleSaveEdit(session.session_id)}
                          autoFocus
                        />
                      </div>
                    ) : (
                      <div className="session-name-container">
                        <p className="session-chat-name">{displayName}</p>
                        <button
                          className="edit-name-button"
                          onClick={(e) => handleStartEdit(session, e)}
                          title="Edit chat name"
                        >
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                        </button>
                      </div>
                    )}
                    
                    <div className="session-metadata">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="pdf-icon">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                      </svg>
                      <p className="session-document-name">{session.document_name}</p>
                    </div>
                    
                    <p className="session-date">{formatDate(session.created_at)}</p>
                    
                    {session.preview_message && (
                      <p className="session-preview">{session.preview_message}</p>
                    )}
                  </div>
                  
                  <motion.button
                    className="delete-session-button"
                    onClick={(e) => {
                      e.stopPropagation()
                      onDeleteSession(session.session_id)
                    }}
                    whileHover={{ scale: 1.2, color: '#ef4444' }}
                    whileTap={{ scale: 0.9 }}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </motion.button>
                </motion.div>
              )
            })
          )}
        </div>
      </div>
    </div>
  )
}

export default Sidebar

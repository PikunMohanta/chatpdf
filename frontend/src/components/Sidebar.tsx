import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
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
  const [menuOpenSessionId, setMenuOpenSessionId] = useState<string | null>(null)
  const menuRef = useRef<HTMLDivElement>(null)

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpenSessionId(null)
      }
    }

    if (menuOpenSessionId) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [menuOpenSessionId])

  const getTimeGroup = (isoString: string): string => {
    const date = new Date(isoString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    
    if (hours < 24) return 'Today'
    if (hours < 48) return 'Yesterday'
    if (days < 7) return 'Previous 7 Days'
    if (days < 30) return 'Previous 30 Days'
    
    // Return month name
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  }

  const groupSessionsByTime = () => {
    const groups: { [key: string]: ChatSession[] } = {}
    
    chatSessions.forEach(session => {
      const group = getTimeGroup(session.created_at)
      if (!groups[group]) {
        groups[group] = []
      }
      groups[group].push(session)
    })
    
    return groups
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

  const toggleMenu = (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    setMenuOpenSessionId(menuOpenSessionId === sessionId ? null : sessionId)
  }

  const handleMenuAction = (action: string, session: ChatSession, e: React.MouseEvent) => {
    e.stopPropagation()
    setMenuOpenSessionId(null)
    
    switch (action) {
      case 'pin':
        // TODO: Implement pin functionality
        console.log('Pin session:', session.session_id)
        break
      case 'rename':
        handleStartEdit(session, e)
        break
      case 'delete':
        onDeleteSession(session.session_id)
        break
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
        <div className="chat-history-list">
          {chatSessions.length === 0 ? (
            <div className="no-chats">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" className="no-chats-icon">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              <p className="no-chats-text">No chat history yet</p>
              <p className="no-chats-subtext">Upload a PDF to start your first conversation</p>
            </div>
          ) : (
            Object.entries(groupSessionsByTime()).map(([timeGroup, sessions]) => (
              <div key={timeGroup} className="time-group">
                <h3 className="time-group-title">{timeGroup}</h3>
                {sessions.map((session) => {
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
                  <div className="session-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                  </div>
                  
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
                      <p className="session-chat-name">{displayName}</p>
                    )}
                  </div>
                  
                  <div className="session-actions" ref={menuOpenSessionId === session.session_id ? menuRef : null}>
                    <motion.button
                      className="menu-button"
                      onClick={(e) => toggleMenu(session.session_id, e)}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                    >
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                        <circle cx="12" cy="5" r="2" />
                        <circle cx="12" cy="12" r="2" />
                        <circle cx="12" cy="19" r="2" />
                      </svg>
                    </motion.button>

                    <AnimatePresence>
                      {menuOpenSessionId === session.session_id && (
                        <motion.div
                          className="context-menu"
                          initial={{ opacity: 0, scale: 0.95, y: -10 }}
                          animate={{ opacity: 1, scale: 1, y: 0 }}
                          exit={{ opacity: 0, scale: 0.95, y: -10 }}
                          transition={{ duration: 0.15 }}
                          onClick={(e) => e.stopPropagation()}
                        >
                        <button
                          className="context-menu-item"
                          onClick={(e) => handleMenuAction('pin', session, e)}
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                          </svg>
                          Pin
                        </button>
                        
                        <button
                          className="context-menu-item"
                          onClick={(e) => handleMenuAction('rename', session, e)}
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                          Rename
                        </button>
                        
                        <div className="context-menu-divider" />
                        
                        <button
                          className="context-menu-item danger"
                          onClick={(e) => handleMenuAction('delete', session, e)}
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                          Delete
                        </button>
                      </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </motion.div>
              )
            })}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default Sidebar

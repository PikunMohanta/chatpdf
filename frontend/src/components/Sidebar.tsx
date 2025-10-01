import { motion } from 'framer-motion'
import { ChatSession } from '../App'
import './Sidebar.css'

interface SidebarProps {
  chatSessions: ChatSession[]
  currentSessionId: string
  onNewChat: () => void
  onSelectSession: (session: ChatSession) => void
  onDeleteSession: (sessionId: string) => void
}

const Sidebar = ({
  chatSessions,
  currentSessionId,
  onNewChat,
  onSelectSession,
  onDeleteSession,
}: SidebarProps) => {
  const formatDate = (isoString: string) => {
    const date = new Date(isoString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))
    
    if (hours < 24) return 'Today'
    if (hours < 48) return 'Yesterday'
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
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
            chatSessions.map((session) => (
              <motion.div
                key={session.session_id}
                className={`chat-session-item ${session.document_id === currentSessionId ? 'active' : ''}`}
                onClick={() => onSelectSession(session)}
                whileHover={{ x: 4, backgroundColor: 'rgba(79, 70, 229, 0.05)' }}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <div className="session-info">
                  <p className="session-name">{session.document_name}</p>
                  <p className="session-date">{formatDate(session.updated_at)}</p>
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
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default Sidebar

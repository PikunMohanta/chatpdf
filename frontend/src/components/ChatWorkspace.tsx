import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Sidebar from './Sidebar.tsx'
import PdfViewer from './PdfViewer.tsx'
import ChatPanel from './ChatPanel.tsx'
import UserProfile from './UserProfile.tsx'
import { DocumentInfo, ChatSession } from '../App'
import './ChatWorkspace.css'

interface ChatWorkspaceProps {
  currentDocument: DocumentInfo | null
  chatSessions: ChatSession[]
  onNewChat: () => void
  onSelectSession: (session: ChatSession) => void
  onDeleteSession: (sessionId: string) => void
}

const ChatWorkspace = ({
  currentDocument,
  chatSessions,
  onNewChat,
  onSelectSession,
  onDeleteSession,
}: ChatWorkspaceProps) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [highlightedPage, setHighlightedPage] = useState<number | null>(null)

  const handleSourceClick = (pageNumber: number) => {
    setHighlightedPage(pageNumber)
    // Reset highlight after 3 seconds
    setTimeout(() => setHighlightedPage(null), 3000)
  }

  if (!currentDocument) {
    return (
      <div className="chat-workspace no-document">
        <p>No document selected. Please upload a PDF to start chatting.</p>
      </div>
    )
  }

  return (
    <div className="chat-workspace">
      {/* Header with User Profile */}
      <div className="workspace-header">
        <motion.button
          className="sidebar-toggle"
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </motion.button>

        <h1 className="workspace-title">PDF Pal</h1>

        <UserProfile />
      </div>

      {/* Main Content Area */}
      <div className="workspace-content">
        {/* Sidebar */}
        <AnimatePresence>
          {!sidebarCollapsed && (
            <motion.div
              initial={{ x: -280, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -280, opacity: 0 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
              className="sidebar-container"
            >
              <Sidebar
                chatSessions={chatSessions}
                currentSessionId={currentDocument.document_id}
                onNewChat={onNewChat}
                onSelectSession={onSelectSession}
                onDeleteSession={onDeleteSession}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Split View: PDF Viewer + Chat Panel */}
        <div className="main-split-view">
          <div className="pdf-viewer-container">
            <PdfViewer
              documentId={currentDocument.document_id}
              filename={currentDocument.filename}
              highlightedPage={highlightedPage}
            />
          </div>

          <div className="chat-panel-container">
            <ChatPanel
              documentId={currentDocument.document_id}
              documentName={currentDocument.filename}
              onSourceClick={handleSourceClick}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatWorkspace

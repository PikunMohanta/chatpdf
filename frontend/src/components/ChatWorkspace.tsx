import { useState, useRef, useEffect } from 'react'
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
  onUpdateChatName?: (sessionId: string, newName: string) => void
}

const ChatWorkspace = ({
  currentDocument,
  chatSessions,
  onNewChat,
  onSelectSession,
  onDeleteSession,
  onUpdateChatName,
}: ChatWorkspaceProps) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [highlightedPage, setHighlightedPage] = useState<number | null>(null)
  const [pdfWidth, setPdfWidth] = useState(40) // Percentage width for PDF viewer
  const [isResizing, setIsResizing] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  const handleSourceClick = (pageNumber: number) => {
    setHighlightedPage(pageNumber)
    // Reset highlight after 3 seconds
    setTimeout(() => setHighlightedPage(null), 3000)
  }

  const handleMouseDown = () => {
    setIsResizing(true)
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (!isResizing || !containerRef.current) return

    const containerRect = containerRef.current.getBoundingClientRect()
    const containerWidth = containerRect.width
    const mouseX = e.clientX - containerRect.left
    const newPdfWidth = ((containerWidth - mouseX) / containerWidth) * 100

    // Limit PDF width between 20% and 60%
    if (newPdfWidth >= 20 && newPdfWidth <= 60) {
      setPdfWidth(newPdfWidth)
    }
  }

  const handleMouseUp = () => {
    setIsResizing(false)
  }

  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = 'col-resize'
      document.body.style.userSelect = 'none'
    } else {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }
  }, [isResizing])

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
      <div className="workspace-content" ref={containerRef}>
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
                onUpdateChatName={onUpdateChatName}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Main Split View: Chat Panel (Middle) + PDF Viewer (Right) */}
        <div className="main-split-view">
          {/* Chat Panel - Now in the middle */}
          <div className="chat-panel-container" style={{ width: `${100 - pdfWidth}%` }}>
            <ChatPanel
              documentId={currentDocument.document_id}
              documentName={currentDocument.filename}
              onSourceClick={handleSourceClick}
            />
          </div>

          {/* Resizable Divider */}
          <div 
            className={`resize-divider ${isResizing ? 'resizing' : ''}`}
            onMouseDown={handleMouseDown}
          >
            <div className="resize-handle">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M8 4L8 20" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <path d="M16 4L16 20" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </div>
          </div>

          {/* PDF Viewer - Now on the right with adjustable width */}
          <div className="pdf-viewer-container" style={{ width: `${pdfWidth}%` }}>
            <PdfViewer
              documentId={currentDocument.document_id}
              filename={currentDocument.filename}
              highlightedPage={highlightedPage}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatWorkspace

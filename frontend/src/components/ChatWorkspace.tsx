import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import Sidebar from './Sidebar.tsx'
import PdfViewer from './PdfViewer.tsx'
import ChatPanel from './ChatPanel.tsx'
import UserProfile from './UserProfile.tsx'
import { DocumentInfo, ChatSession } from '../App'
import './ChatWorkspace.css'

interface ChatWorkspaceProps {
  currentDocument: DocumentInfo
  chatSessions: ChatSession[]
  onNewChat: () => void
  onSelectSession: (session: ChatSession) => void
  onDeleteSession: (sessionId: string) => void
  onUpdateChatName?: (sessionId: string, newName: string) => void
  onUpdateSessionId?: (documentId: string, newSessionId: string) => void
  onUpdatePreviewMessage?: (sessionId: string, previewMessage: string) => void
  onUpdateLastMessage?: (sessionId: string, lastMessage: string) => void
}

const ChatWorkspace = ({
  currentDocument,
  chatSessions,
  onNewChat,
  onSelectSession,
  onDeleteSession,
  onUpdateChatName,
  onUpdateSessionId,
  onUpdatePreviewMessage,
  onUpdateLastMessage,
}: ChatWorkspaceProps) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(true) // Start collapsed by default
  const [highlightedPage, setHighlightedPage] = useState<number | null>(null)
  const [pdfWidth, setPdfWidth] = useState(40) // Percentage width for PDF viewer
  const [pdfHidden, setPdfHidden] = useState(false) // New state for hiding PDF
  const [isResizing, setIsResizing] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()

  const handleSourceClick = (pageNumber: number) => {
    setHighlightedPage(pageNumber)
    // Reset highlight after 3 seconds
    setTimeout(() => setHighlightedPage(null), 3000)
  }

  const generateChatName = (query: string): string => {
    const lowercaseQuery = query.toLowerCase().trim()
    
    // Smart title generation based on query intent
    if (lowercaseQuery.includes('summarize') || lowercaseQuery.includes('summary')) {
      const topic = extractTopicFromQuery(query, ['summarize', 'summary', 'give me a summary of', 'can you summarize'])
      return `Summary: ${topic}`
    }
    
    if (lowercaseQuery.includes('explain') || lowercaseQuery.includes('what is') || lowercaseQuery.includes('what are')) {
      const topic = extractTopicFromQuery(query, ['explain', 'what is', 'what are', 'tell me about'])
      return `Explanation: ${topic}`
    }
    
    if (lowercaseQuery.includes('list') || lowercaseQuery.includes('find') || lowercaseQuery.includes('show me')) {
      const topic = extractTopicFromQuery(query, ['list', 'find', 'show me', 'get me'])
      return `Analysis: ${topic}`
    }
    
    if (lowercaseQuery.includes('how') || lowercaseQuery.includes('process') || lowercaseQuery.includes('method')) {
      const topic = extractTopicFromQuery(query, ['how', 'process', 'method', 'procedure'])
      return `Guide: ${topic}`
    }
    
    if (lowercaseQuery.includes('compare') || lowercaseQuery.includes('difference') || lowercaseQuery.includes('vs')) {
      const topic = extractTopicFromQuery(query, ['compare', 'difference', 'vs', 'versus'])
      return `Comparison: ${topic}`
    }
    
    // Default: Extract key topic and create natural title
    const words = query.trim().split(/\s+/)
    const keyTopic = words.slice(0, 4).join(' ')
    return words.length > 4 ? `${keyTopic}...` : keyTopic
  }

  const extractTopicFromQuery = (query: string, triggers: string[]): string => {
    let cleanQuery = query.trim()
    
    // Remove common trigger words
    triggers.forEach(trigger => {
      const regex = new RegExp(`\\b${trigger}\\b`, 'gi')
      cleanQuery = cleanQuery.replace(regex, '').trim()
    })
    
    // Remove common connecting words
    cleanQuery = cleanQuery.replace(/\b(about|the|of|in|on|for|with|from|to|a|an)\b/gi, ' ')
    cleanQuery = cleanQuery.replace(/\s+/g, ' ').trim()
    
    // Take first 3-4 meaningful words
    const words = cleanQuery.split(/\s+/).filter(word => word.length > 2)
    const topic = words.slice(0, 3).join(' ')
    
    // Capitalize first letter
    return topic.charAt(0).toUpperCase() + topic.slice(1)
  }

  const handleGenerateChatName = (query: string) => {
    if (!currentDocument || !onUpdateChatName) return
    
    const currentSession = chatSessions.find(s => s.document_id === currentDocument.document_id)
    if (!currentSession) return
    
    // Only generate name if it hasn't been set yet
    if (!currentSession.chat_name) {
      const generatedName = generateChatName(query)
      onUpdateChatName(currentSession.session_id, generatedName)
    }
  }

  const handleSessionIdReceived = (newSessionId: string) => {
    if (!currentDocument || !onUpdateSessionId) return
    
    console.log('📌 Updating session ID for document', currentDocument.document_id, 'to', newSessionId)
    onUpdateSessionId(currentDocument.document_id, newSessionId)
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

  // ChatGPT/Grok-style welcome screen
  const [uploadingFile, setUploadingFile] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = async (file: File) => {
    if (file.type !== 'application/pdf') {
      alert('Please upload a PDF file')
      return
    }

    setUploadingFile(true)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer dev-token'
        },
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        const newSession: ChatSession = {
          session_id: `temp_${Date.now()}`,
          document_id: data.document_id,
          document_name: file.name,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        }

        const existingSessions = JSON.parse(localStorage.getItem('chat_sessions') || '[]')
        const updatedSessions = [newSession, ...existingSessions]
        localStorage.setItem('chat_sessions', JSON.stringify(updatedSessions))

        onSelectSession(newSession)
        navigate('/chat')
      } else {
        alert('Upload failed. Please try again.')
      }
    } catch (error) {
      console.error('Upload error:', error)
      alert('Upload failed. Please try again.')
    } finally {
      setUploadingFile(false)
    }
  }

  const handleAttachClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileUpload(file)
    }
  }

  if (!currentDocument) {
    return (
      <div className="chat-workspace empty-state">
        <div className="empty-state-container">
          {/* Sidebar Toggle (top left) */}
          <motion.button
            className="sidebar-toggle-floating"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </motion.button>

          {/* User Profile (top right) */}
          <div className="user-profile-floating">
            <UserProfile />
          </div>

          {/* Sidebar */}
          <AnimatePresence>
            {!sidebarCollapsed && (
              <motion.div
                initial={{ x: -280, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                exit={{ x: -280, opacity: 0 }}
                transition={{ duration: 0.3, ease: 'easeInOut' }}
                className="sidebar-floating"
              >
                <Sidebar
                  chatSessions={chatSessions}
                  currentSessionId=""
                  onSelectSession={onSelectSession}
                  onDeleteSession={onDeleteSession}
                  onUpdateChatName={onUpdateChatName}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Center Content */}
          <div className="empty-state-content">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="welcome-content"
            >
              <motion.h1
                className="welcome-app-name"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{
                  duration: 1,
                  ease: 'easeOut',
                  delay: 0.2,
                }}
              >
                <motion.span
                  className="app-name-pdf"
                  animate={{
                    textShadow: [
                      '0 0 20px rgba(59, 130, 246, 0.5)',
                      '0 0 40px rgba(59, 130, 246, 0.8)',
                      '0 0 20px rgba(59, 130, 246, 0.5)',
                    ],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                >
                  PDF
                </motion.span>
                <motion.span
                  className="app-name-pixie"
                  animate={{
                    color: ['#3B82F6', '#60A5FA', '#3B82F6'],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                >
                  Pixie
                </motion.span>
              </motion.h1>
              <motion.h2
                className="empty-state-title"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.4 }}
              >
                What can I help with?
              </motion.h2>
            </motion.div>

            {/* File Input (hidden) */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />

            {/* Prominent Upload Button */}
            <motion.div
              className="empty-state-input-wrapper"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              <motion.button
                className="attach-pdf-button"
                onClick={handleAttachClick}
                disabled={uploadingFile}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {uploadingFile ? (
                  <>
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      style={{ display: 'inline-flex', marginRight: '8px' }}
                    >
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    </motion.div>
                    Uploading PDF...
                  </>
                ) : (
                  <>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" style={{ marginRight: '8px' }}>
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                    </svg>
                    Upload PDF
                  </>
                )}
              </motion.button>
            </motion.div>
          </div>
        </div>
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

        <h1 className="workspace-title">PDFPixie</h1>

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
          <div className="chat-panel-container" style={{ width: pdfHidden ? '100%' : `${100 - pdfWidth}%` }}>
            <ChatPanel
              key={currentDocument.document_id}
              documentId={currentDocument.document_id}
              documentName={currentDocument.filename}
              chatName={chatSessions.find(s => s.document_id === currentDocument.document_id)?.chat_name}
              sessionId={chatSessions.find(s => s.document_id === currentDocument.document_id)?.session_id}
              onSourceClick={handleSourceClick}
              onGenerateChatName={handleGenerateChatName}
              onSessionIdReceived={handleSessionIdReceived}
              onUploadClick={handleAttachClick}
              onUpdatePreviewMessage={onUpdatePreviewMessage}
              onUpdateLastMessage={onUpdateLastMessage}
              onShowPdf={() => setPdfHidden(false)}
              pdfHidden={pdfHidden}
            />
          </div>

          {/* PDF Toggle Button */}
          {!pdfHidden && (
            <>
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
                  key={currentDocument.document_id}
                  documentId={currentDocument.document_id}
                  filename={currentDocument.filename}
                  highlightedPage={highlightedPage}
                  onHidePdf={() => setPdfHidden(true)}
                />
              </div>
            </>
          )}


        </div>

        {/* Floating New Chat Button */}
        <motion.button
          className="floating-new-chat-button"
          onClick={onNewChat}
          whileHover={{ scale: 1.1, boxShadow: '0 8px 25px rgba(59, 130, 246, 0.3)' }}
          whileTap={{ scale: 0.95 }}
          title="Start New Chat"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5 11h-4v4h-2v-4H7v-2h4V7h2v4h4v2z"/>
          </svg>
        </motion.button>
      </div>
    </div>
  )
}

export default ChatWorkspace

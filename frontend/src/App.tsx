import { useState, useEffect } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import SplashScreen from './components/SplashScreen'
import UploadScreen from './components/UploadScreen'
import ChatWorkspace from './components/ChatWorkspace'
import './App.css'

export interface DocumentInfo {
  document_id: string
  filename: string
  status?: string
  page_count?: number
  text_length?: number
}

export interface ChatSession {
  session_id: string
  document_id: string
  document_name: string
  chat_name?: string
  created_at: string
  updated_at: string
  preview_message?: string
}

function App() {
  const [showSplash, setShowSplash] = useState(true)
  const [currentDocument, setCurrentDocument] = useState<DocumentInfo | null>(null)
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([])
  const navigate = useNavigate()

  useEffect(() => {
    // Load chat sessions from localStorage or API
    const savedSessions = localStorage.getItem('chat_sessions')
    if (savedSessions) {
      try {
        setChatSessions(JSON.parse(savedSessions))
      } catch (e) {
        console.error('Failed to parse chat sessions:', e)
      }
    }
  }, [])

  const handleSplashComplete = () => {
    setShowSplash(false)
    navigate('/upload')
  }

  const handleUploadSuccess = (docInfo: DocumentInfo) => {
    setCurrentDocument(docInfo)
    
    // Create new chat session
    const newSession: ChatSession = {
      session_id: `session_${Date.now()}`,
      document_id: docInfo.document_id,
      document_name: docInfo.filename,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    
    const updatedSessions = [newSession, ...chatSessions]
    setChatSessions(updatedSessions)
    localStorage.setItem('chat_sessions', JSON.stringify(updatedSessions))
    
    navigate('/chat')
  }

  const handleNewChat = () => {
    setCurrentDocument(null)
    navigate('/upload')
  }

  const handleSelectSession = (session: ChatSession) => {
    // Load the document for this session
    setCurrentDocument({
      document_id: session.document_id,
      filename: session.document_name,
      status: 'processed',
    })
    navigate('/chat')
  }

  const handleDeleteSession = (sessionId: string) => {
    const updatedSessions = chatSessions.filter(s => s.session_id !== sessionId)
    setChatSessions(updatedSessions)
    localStorage.setItem('chat_sessions', JSON.stringify(updatedSessions))
  }

  const handleUpdateChatName = (sessionId: string, newName: string) => {
    const updatedSessions = chatSessions.map(session => 
      session.session_id === sessionId 
        ? { ...session, chat_name: newName, updated_at: new Date().toISOString() }
        : session
    )
    setChatSessions(updatedSessions)
    localStorage.setItem('chat_sessions', JSON.stringify(updatedSessions))
  }

  if (showSplash) {
    return <SplashScreen onComplete={handleSplashComplete} />
  }

  return (
    <div className="app-container">
      <Routes>
        <Route path="/" element={<SplashScreen onComplete={handleSplashComplete} />} />
        <Route path="/upload" element={<UploadScreen onUploadSuccess={handleUploadSuccess} />} />
        <Route
          path="/chat"
          element={
            <ChatWorkspace
              currentDocument={currentDocument}
              chatSessions={chatSessions}
              onNewChat={handleNewChat}
              onSelectSession={handleSelectSession}
              onDeleteSession={handleDeleteSession}
              onUpdateChatName={handleUpdateChatName}
            />
          }
        />
      </Routes>
    </div>
  )
}

export default App

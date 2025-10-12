import { useState, useEffect } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
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
  const [currentDocument, setCurrentDocument] = useState<DocumentInfo | null>(null)
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([])
  const navigate = useNavigate()

  useEffect(() => {
    // Load chat sessions from localStorage or API
    const savedSessions = localStorage.getItem('chat_sessions')
    if (savedSessions) {
      try {
        const sessions = JSON.parse(savedSessions)
        setChatSessions(sessions)
      } catch (e) {
        console.error('Failed to parse chat sessions:', e)
      }
    }
    
    // Start at root (empty state)
    if (window.location.pathname === '/chat' || window.location.pathname === '/') {
      // Allow the current route
    } else {
      navigate('/')
    }
  }, [])

  const handleNewChat = () => {
    // Clear current document and navigate to root for empty state
    setCurrentDocument(null)
    navigate('/')
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
    
    // If the deleted session was the current one and there are other sessions, switch to the first one
    if (currentDocument?.document_id === sessionId) {
      if (updatedSessions.length > 0) {
        const nextSession = updatedSessions[0]
        setCurrentDocument({
          document_id: nextSession.document_id,
          filename: nextSession.document_name,
          status: 'processed',
        })
      } else {
        // No more sessions, go back to empty state
        setCurrentDocument(null)
      }
    }
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

  const handleUpdateSessionId = (documentId: string, newSessionId: string) => {
    console.log('📌 App.tsx: Updating session ID for document', documentId, 'to', newSessionId)
    console.log('📋 Current sessions:', chatSessions.map(s => ({ doc: s.document_id, session: s.session_id })))
    
    const updatedSessions = chatSessions.map(session => {
      if (session.document_id === documentId) {
        console.log(`✏️  Updating session ${session.session_id} -> ${newSessionId}`)
        return { ...session, session_id: newSessionId, updated_at: new Date().toISOString() }
      }
      return session
    })
    
    console.log('💾 Saving updated sessions to localStorage')
    setChatSessions(updatedSessions)
    localStorage.setItem('chat_sessions', JSON.stringify(updatedSessions))
    
    // Verify the update
    console.log('✅ Sessions after update:', updatedSessions.map(s => ({ doc: s.document_id, session: s.session_id })))
  }

  return (
    <div className="app-container">
      <Routes>
        <Route path="/" element={
          <ChatWorkspace
            currentDocument={currentDocument}
            chatSessions={chatSessions}
            onNewChat={handleNewChat}
            onSelectSession={handleSelectSession}
            onDeleteSession={handleDeleteSession}
            onUpdateChatName={handleUpdateChatName}
            onUpdateSessionId={handleUpdateSessionId}
          />
        } />
        <Route path="/chat" element={
          <ChatWorkspace
            currentDocument={currentDocument}
            chatSessions={chatSessions}
            onNewChat={handleNewChat}
            onSelectSession={handleSelectSession}
            onDeleteSession={handleDeleteSession}
            onUpdateChatName={handleUpdateChatName}
            onUpdateSessionId={handleUpdateSessionId}
          />
        } />
      </Routes>
    </div>
  )
}

export default App

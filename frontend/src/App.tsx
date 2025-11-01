import { useState, useEffect, Suspense, lazy } from 'react'
import { Routes, Route, useNavigate } from 'react-router-dom'
import './App.css'

// Lazy load heavy components
const ChatWorkspace = lazy(() => import('./components/ChatWorkspace'))

// Loading component
const LoadingFallback = () => (
  <div className="loading-fallback">
    <div className="spinner"></div>
    <p>Loading...</p>
  </div>
)

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
  last_message_preview?: string
}

function App() {
  const [currentDocument, setCurrentDocument] = useState<DocumentInfo | null>(null)
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([])
  const navigate = useNavigate()

  useEffect(() => {
    // Load chat sessions from backend API first, then fallback to localStorage
    const loadChatSessions = async () => {
      try {
        const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
        console.log('🔄 Loading chat sessions from backend...')
        const response = await fetch(`${apiUrl}/api/chat/sessions/all`, {
          headers: {
            'Authorization': 'Bearer dev-token'
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          console.log('✅ Loaded sessions from backend:', data.sessions.length)
          
          // Transform backend sessions to frontend format
          const transformedSessions: ChatSession[] = data.sessions.map((session: any) => ({
            session_id: session.session_id,
            document_id: session.document_id,
            document_name: session.document_name || `Document ${session.document_id.slice(0, 8)}`,
            chat_name: session.chat_name,
            created_at: session.created_at,
            updated_at: session.updated_at,
            preview_message: session.last_message || 'Chat session',
            last_message_preview: session.last_message
          }))
          
          setChatSessions(transformedSessions)
          // Also save to localStorage for offline access
          localStorage.setItem('chat_sessions', JSON.stringify(transformedSessions))
          return
        } else {
          console.warn('⚠️ Failed to load sessions from backend, trying localStorage...')
        }
      } catch (error) {
        console.error('❌ Error loading sessions from backend:', error)
      }
      
      // Fallback to localStorage if backend fails
      const savedSessions = localStorage.getItem('chat_sessions')
      if (savedSessions) {
        try {
          const sessions = JSON.parse(savedSessions)
          setChatSessions(sessions)
          console.log('📱 Loaded sessions from localStorage:', sessions.length)
        } catch (e) {
          console.error('Failed to parse chat sessions from localStorage:', e)
        }
      }
    }
    
    loadChatSessions()
    
    // Auto-load test document if no sessions exist (ONLY IN DEVELOPMENT MODE)
    const checkForTestDocument = () => {
      if (import.meta.env.VITE_ENABLE_TEST_DOCUMENT === 'true') {
        // Check if we have any sessions after loading
        setTimeout(() => {
          if (chatSessions.length === 0) {
            console.log('🔍 No existing sessions found, creating test session...')
            
            // Load test document immediately
            const loadTestDocument = async () => {
              try {
                const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
                const response = await fetch(`${apiUrl}/api/debug/test-document`, {
                  headers: {
                    'Authorization': 'Bearer dev-token'
                  }
                })
                
                if (!response.ok) {
                  throw new Error(`HTTP ${response.status}`)
                }
                
                const data = await response.json()
                console.log('✅ Test document loaded:', data)
                
                const testSession: ChatSession = {
                  session_id: data.document_id,
                  document_id: data.document_id,
                  document_name: data.filename,
                  chat_name: 'Sample Document',
                  created_at: new Date().toISOString(),
                  updated_at: new Date().toISOString(),
                  preview_message: 'Sample PDF loaded for testing'
                }
                
                setChatSessions([testSession])
                localStorage.setItem('chat_sessions', JSON.stringify([testSession]))
                
                setCurrentDocument({
                  document_id: data.document_id,
                  filename: data.filename,
                  status: 'processed'
                })
                
                console.log('📄 Document set:', data.document_id, data.filename)
                navigate('/chat')
                
              } catch (error) {
                console.error('❌ Failed to load test document:', error)
              }
            }
            
            loadTestDocument()
          }
        }, 500) // Small delay to allow sessions to load
      }
    }
    
    checkForTestDocument()
    
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

  const handleUpdatePreviewMessage = (sessionId: string, previewMessage: string) => {
    const updatedSessions = chatSessions.map(session => 
      session.session_id === sessionId 
        ? { ...session, preview_message: previewMessage, updated_at: new Date().toISOString() }
        : session
    )
    setChatSessions(updatedSessions)
    localStorage.setItem('chat_sessions', JSON.stringify(updatedSessions))
  }

  const handleUpdateLastMessage = (sessionId: string, lastMessage: string) => {
    const updatedSessions = chatSessions.map(session => 
      session.session_id === sessionId 
        ? { ...session, last_message_preview: lastMessage, updated_at: new Date().toISOString() }
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
      <Suspense fallback={<LoadingFallback />}>
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
              onUpdatePreviewMessage={handleUpdatePreviewMessage}
              onUpdateLastMessage={handleUpdateLastMessage}
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
              onUpdatePreviewMessage={handleUpdatePreviewMessage}
              onUpdateLastMessage={handleUpdateLastMessage}
            />
          } />
        </Routes>
      </Suspense>
    </div>
  )
}

export default App

import { useState } from 'react'
import UploadComponent from './components/UploadComponent'
import ChatComponent from './components/ChatComponent'
import PreviewComponent from './components/PreviewComponent'
import './App.css'

interface DocumentInfo {
  document_id: string
  filename: string
  status?: string
  page_count?: number
  text_length?: number
}

function App() {
  const [currentDocument, setCurrentDocument] = useState<DocumentInfo | null>(null)
  const [showChat, setShowChat] = useState(false)

  const handleUploadSuccess = (docInfo: DocumentInfo) => {
    console.log('Upload success:', docInfo)
    
    // Validate document info
    if (!docInfo || !docInfo.document_id) {
      console.error('Invalid document info received:', docInfo)
      return
    }
    
    setCurrentDocument(docInfo)
    setShowChat(true)
  }

  const handleNewDocument = () => {
    setCurrentDocument(null)
    setShowChat(false)
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Newchat 📄</h1>
        <p>AI-Powered PDF Chat Assistant</p>
      </header>

      <main className="app-main">
        {!showChat ? (
          <div className="upload-container">
            <UploadComponent onUploadSuccess={handleUploadSuccess} />
          </div>
        ) : (
          <div className="document-view">
            <div className="document-header">
              <div className="document-info">
                <h2>{currentDocument?.filename}</h2>
                <span className="document-id">ID: {currentDocument?.document_id}</span>
              </div>
              <button className="new-document-btn" onClick={handleNewDocument}>
                📤 Upload New Document
              </button>
            </div>

            <div className="document-content">
              <div className="preview-section">
                <PreviewComponent documentId={currentDocument?.document_id || ''} />
              </div>
              <div className="chat-section">
                <ChatComponent documentId={currentDocument?.document_id || ''} />
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>
          Powered by FastAPI, LangChain, OpenRouter &amp; ChromaDB | Built with React &amp; TypeScript
        </p>
      </footer>
    </div>
  )
}

export default App

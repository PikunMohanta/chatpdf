import { useState, useEffect } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import axios from 'axios'
import 'react-pdf/dist/esm/Page/AnnotationLayer.css'
import 'react-pdf/dist/esm/Page/TextLayer.css'
import './PreviewComponent.css'

// Set up PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`

interface PreviewComponentProps {
  documentId: string
}

const PreviewComponent = ({ documentId }: PreviewComponentProps) => {
  const [numPages, setNumPages] = useState<number>(0)
  const [pageNumber, setPageNumber] = useState<number>(1)
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)

  // Fetch PDF with authentication
  useEffect(() => {
    const fetchPDF = async () => {
      if (!documentId) {
        setError('No document ID provided')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        setError(null)
        const token = localStorage.getItem('auth_token') || 'dev-token'
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/document/${documentId}/preview`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
            responseType: 'blob', // Use blob instead of arraybuffer
            timeout: 30000, // 30 second timeout
          }
        )
        
        // Create object URL from blob (prevents detachment issues)
        const url = URL.createObjectURL(response.data)
        setPdfUrl(url)
        setLoading(false)
      } catch (err) {
        console.error('Error fetching PDF:', err)
        if (axios.isAxiosError(err)) {
          if (err.code === 'ECONNABORTED') {
            setError('Request timeout. Please try again.')
          } else if (err.response?.status === 404) {
            setError('PDF not found. Please try uploading again.')
          } else {
            setError(`Failed to load PDF: ${err.response?.data?.detail || err.message}`)
          }
        } else {
          setError('Failed to load PDF. Please try again.')
        }
        setLoading(false)
      }
    }

    if (documentId) {
      fetchPDF()
    }

    // Cleanup: revoke object URL when component unmounts or document changes
    return () => {
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl)
      }
    }
  }, [documentId])

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages)
    setLoading(false)
    setError(null)
  }

  function onDocumentLoadError(error: Error) {
    console.error('Error loading PDF:', error)
    setError('Failed to load PDF. Please try refreshing.')
    setLoading(false)
  }

  function goToPrevPage() {
    setPageNumber((prev) => Math.max(prev - 1, 1))
  }

  function goToNextPage() {
    setPageNumber((prev) => Math.min(prev + 1, numPages))
  }

  return (
    <div className="preview-component">
      <div className="preview-header">
        <h3>📄 Document Preview</h3>
        {numPages > 0 && (
          <div className="page-info">
            Page {pageNumber} of {numPages}
          </div>
        )}
      </div>

      <div className="preview-container">
        {loading && (
          <div className="preview-loading">
            <div className="spinner"></div>
            <p>Loading PDF...</p>
          </div>
        )}

        {error && (
          <div className="preview-error">
            <span className="error-icon">⚠️</span>
            <p>{error}</p>
          </div>
        )}

        {!error && pdfUrl && (
          <div className="pdf-viewer">
            <Document
              file={pdfUrl}
              onLoadSuccess={onDocumentLoadSuccess}
              onLoadError={onDocumentLoadError}
              loading={null}
            >
              <Page
                pageNumber={pageNumber}
                renderTextLayer={true}
                renderAnnotationLayer={true}
                width={Math.min(window.innerWidth * 0.4, 600)}
              />
            </Document>
          </div>
        )}
      </div>

      {numPages > 0 && !error && (
        <div className="preview-controls">
          <button
            className="nav-button"
            onClick={goToPrevPage}
            disabled={pageNumber <= 1}
          >
            ← Previous
          </button>
          
          <div className="page-selector">
            <input
              type="number"
              min={1}
              max={numPages}
              value={pageNumber}
              onChange={(e) => {
                const page = parseInt(e.target.value)
                if (page >= 1 && page <= numPages) {
                  setPageNumber(page)
                }
              }}
              className="page-input"
            />
            <span className="page-total">/ {numPages}</span>
          </div>

          <button
            className="nav-button"
            onClick={goToNextPage}
            disabled={pageNumber >= numPages}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  )
}

export default PreviewComponent

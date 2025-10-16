import { useState, useEffect, useRef } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import { motion } from 'framer-motion'
import axios from 'axios'
import 'react-pdf/dist/esm/Page/AnnotationLayer.css'
import 'react-pdf/dist/esm/Page/TextLayer.css'
import './PdfViewer.css'

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`

interface PdfViewerProps {
  documentId: string
  filename: string
  highlightedPage: number | null
  onHidePdf?: () => void
}

const PdfViewer = ({ documentId, filename, highlightedPage, onHidePdf }: PdfViewerProps) => {
  const [numPages, setNumPages] = useState<number>(0)
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [scale, setScale] = useState(1.0)
  const [pageInputValue, setPageInputValue] = useState<string>('')
  const pageRefs = useRef<{ [key: number]: HTMLDivElement | null }>({})
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const loadPdf = async () => {
      try {
        setLoading(true)
        setError(null)

        const response = await axios.get(
          `http://localhost:8000/api/pdf/${documentId}`,
          {
            headers: {
              Authorization: 'Bearer dev-token',
            },
            responseType: 'blob',
          }
        )

        const url = URL.createObjectURL(response.data)
        setPdfUrl(url)
        setLoading(false)
      } catch (err) {
        console.error('Error loading PDF:', err)
        setError(err instanceof Error ? err.message : 'Failed to load PDF')
        setLoading(false)
      }
    }

    loadPdf()

    return () => {
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl)
      }
    }
  }, [documentId])

  useEffect(() => {
    if (highlightedPage !== null) {
      scrollToPage(highlightedPage)
    }
  }, [highlightedPage])

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages)
  }

  const scrollToPage = (pageNum: number) => {
    const pageElement = pageRefs.current[pageNum]
    if (pageElement && containerRef.current) {
      pageElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  const handlePageInputSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const pageNum = parseInt(pageInputValue, 10)
    if (!isNaN(pageNum) && pageNum >= 1 && pageNum <= numPages) {
      scrollToPage(pageNum)
      setPageInputValue('')
    }
  }

  const zoomIn = () => {
    setScale((prev) => Math.min(2.0, prev + 0.1))
  }

  const zoomOut = () => {
    setScale((prev) => Math.max(0.5, prev - 0.1))
  }

  const resetZoom = () => {
    setScale(1.0)
  }

  if (loading) {
    return (
      <div className="pdf-viewer loading">
        <motion.div
          className="loading-spinner"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        >
          <svg width="40" height="40" viewBox="0 0 60 60">
            <circle
              cx="30"
              cy="30"
              r="25"
              stroke="currentColor"
              strokeWidth="4"
              fill="none"
              strokeDasharray="157"
              strokeDashoffset="40"
            />
          </svg>
        </motion.div>
        <p>Loading PDF...</p>
      </div>
    )
  }

  if (error || !pdfUrl) {
    return (
      <div className="pdf-viewer error">
        <p>⚠️ {error || 'Failed to load PDF'}</p>
      </div>
    )
  }

  return (
    <div className="pdf-viewer">
      <div className="pdf-toolbar">
        <div className="toolbar-group">
          <span className="page-info">
            {numPages} {numPages === 1 ? 'page' : 'pages'}
          </span>
          
          <div className="page-input-container">
            <form onSubmit={handlePageInputSubmit} className="page-input-form">
              <input
                type="number"
                min="1"
                max={numPages}
                placeholder="Go to..."
                value={pageInputValue}
                onChange={(e) => setPageInputValue(e.target.value)}
                className="page-input"
              />
              <motion.button
                type="submit"
                className="page-go-button"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                disabled={!pageInputValue}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </motion.button>
            </form>
          </div>
        </div>

        <div className="toolbar-group">
          <motion.button
            className="toolbar-button"
            onClick={zoomOut}
            disabled={scale <= 0.5}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="11" cy="11" r="8" strokeWidth="2" />
              <path strokeLinecap="round" strokeWidth="2" d="M8 11h6" />
              <path strokeLinecap="round" strokeWidth="2" d="M21 21l-4.35-4.35" />
            </svg>
          </motion.button>

          <span className="zoom-info">{Math.round(scale * 100)}%</span>

          <motion.button
            className="toolbar-button"
            onClick={resetZoom}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </motion.button>

          <motion.button
            className="toolbar-button"
            onClick={zoomIn}
            disabled={scale >= 2.0}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="11" cy="11" r="8" strokeWidth="2" />
              <path strokeLinecap="round" strokeWidth="2" d="M11 8v6M8 11h6" />
              <path strokeLinecap="round" strokeWidth="2" d="M21 21l-4.35-4.35" />
            </svg>
          </motion.button>

          {/* PDF Hide Button */}
          {onHidePdf && (
            <motion.button
              className="toolbar-button hide-pdf-button"
              onClick={onHidePdf}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              title="Hide PDF"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
              </svg>
            </motion.button>
          )}
        </div>
      </div>

      <div className="pdf-document-container" ref={containerRef}>
        <Document file={pdfUrl} onLoadSuccess={onDocumentLoadSuccess} className="pdf-document">
          {Array.from(new Array(numPages), (_, index) => {
            const pageNum = index + 1
            return (
              <div
                key={`page_${pageNum}`}
                ref={(el) => (pageRefs.current[pageNum] = el)}
                className={`page-wrapper ${highlightedPage === pageNum ? 'page-highlighted' : ''}`}
              >
                <Page
                  pageNumber={pageNum}
                  scale={scale}
                  renderTextLayer={true}
                  renderAnnotationLayer={true}
                />
              </div>
            )
          })}
        </Document>
      </div>

      <div className="pdf-filename">{filename}</div>
    </div>
  )
}

export default PdfViewer

import { useState, useEffect } from 'react'
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
}

const PdfViewer = ({ documentId, filename, highlightedPage }: PdfViewerProps) => {
  const [numPages, setNumPages] = useState<number>(0)
  const [pageNumber, setPageNumber] = useState<number>(1)
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [scale, setScale] = useState(1.0)

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
    if (highlightedPage !== null && highlightedPage !== pageNumber) {
      setPageNumber(highlightedPage)
    }
  }, [highlightedPage])

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages)
  }

  const goToPrevPage = () => {
    setPageNumber((prev) => Math.max(1, prev - 1))
  }

  const goToNextPage = () => {
    setPageNumber((prev) => Math.min(numPages, prev + 1))
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
          <motion.button
            className="toolbar-button"
            onClick={goToPrevPage}
            disabled={pageNumber <= 1}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
            </svg>
          </motion.button>

          <span className="page-info">
            Page {pageNumber} of {numPages}
          </span>

          <motion.button
            className="toolbar-button"
            onClick={goToNextPage}
            disabled={pageNumber >= numPages}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
            </svg>
          </motion.button>
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
        </div>
      </div>

      <div className="pdf-document-container">
        <Document file={pdfUrl} onLoadSuccess={onDocumentLoadSuccess} className="pdf-document">
          <Page
            pageNumber={pageNumber}
            scale={scale}
            renderTextLayer={true}
            renderAnnotationLayer={true}
            className={highlightedPage === pageNumber ? 'page-highlighted' : ''}
          />
        </Document>
      </div>

      <div className="pdf-filename">{filename}</div>
    </div>
  )
}

export default PdfViewer

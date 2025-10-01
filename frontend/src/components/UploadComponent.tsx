import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import axios from 'axios'
import './UploadComponent.css'

interface UploadComponentProps {
  onUploadSuccess: (docInfo: {
    document_id: string
    filename: string
    status: string
    page_count: number
    text_length: number
  }) => void
}

const UploadComponent = ({ onUploadSuccess }: UploadComponentProps) => {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [fileName, setFileName] = useState<string>('')

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    setFileName(file.name)
    setUploading(true)
    setProgress(0)
    setError(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      // Get auth token (use dev-token for local development)
      const token = localStorage.getItem('auth_token') || 'dev-token'
      
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${token}`,
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = progressEvent.total
              ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
              : 0
            setProgress(percentCompleted)
          },
        }
      )

      if (response.data) {
        // Small delay to show 100% completion
        setTimeout(() => {
          setUploading(false)
          setProgress(0)
          onUploadSuccess(response.data)
        }, 500)
      }
    } catch (err) {
      console.error('Upload error:', err)
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'Upload failed. Please try again.')
      } else {
        setError('An unexpected error occurred.')
      }
      setUploading(false)
      setProgress(0)
    }
  }, [onUploadSuccess])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxFiles: 1,
    disabled: uploading,
  })

  return (
    <div className="upload-component">
      <div
        {...getRootProps()}
        className={`dropzone ${isDragActive ? 'active' : ''} ${uploading ? 'uploading' : ''}`}
      >
        <input {...getInputProps()} />
        
        {!uploading ? (
          <>
            <div className="upload-icon">📄</div>
            <h3>Upload your PDF</h3>
            <p>
              {isDragActive
                ? 'Drop your PDF here...'
                : 'Drag & drop a PDF file here, or click to select'}
            </p>
            <button className="select-file-btn" type="button">
              Select File
            </button>
          </>
        ) : (
          <div className="upload-progress">
            <div className="spinner"></div>
            <h3>Uploading {fileName}</h3>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progress}%` }}></div>
            </div>
            <p className="progress-text">{progress}%</p>
            {progress === 100 && <p className="processing-text">Processing document...</p>}
          </div>
        )}
      </div>

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      <div className="upload-info">
        <h4>📋 Supported Format</h4>
        <p>PDF files only • Maximum size: 50MB</p>
      </div>
    </div>
  )
}

export default UploadComponent

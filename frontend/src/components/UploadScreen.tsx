import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import axios from 'axios'
import { DocumentInfo } from '../App'
import './UploadScreen.css'

interface UploadScreenProps {
  onUploadSuccess: (docInfo: DocumentInfo) => void
}

const UploadScreen = ({ onUploadSuccess }: UploadScreenProps) => {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [fileName, setFileName] = useState<string | null>(null)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    setFileName(file.name)
    setUploading(true)
    setError(null)
    setProgress(0)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post<DocumentInfo>(
        'http://localhost:8000/api/upload',
        formData,
        {
          headers: {
            'Authorization': 'Bearer dev-token',
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = progressEvent.total
              ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
              : 0
            setProgress(percentCompleted)
          },
        }
      )

      // Validate response
      if (!response.data || !response.data.document_id) {
        throw new Error('Invalid response from server')
      }

      // Small delay to show 100% completion
      setTimeout(() => {
        setUploading(false)
        setProgress(0)
        setFileName(null)
        onUploadSuccess(response.data)
      }, 500)
    } catch (err) {
      console.error('Upload error:', err)
      setError(err instanceof Error ? err.message : 'Upload failed')
      setUploading(false)
      setProgress(0)
    }
  }, [onUploadSuccess])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    multiple: false,
    disabled: uploading,
  })

  return (
    <div className="upload-screen">
      <motion.div
        className="upload-container"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      >
        <motion.h1
          className="upload-title"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.5 }}
        >
          Upload Your PDF
        </motion.h1>

        <motion.p
          className="upload-subtitle"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
        >
          Drop your PDF here or click to browse
        </motion.p>

        <div
          {...getRootProps()}
          className={`dropzone ${isDragActive ? 'dropzone-active' : ''} ${uploading ? 'dropzone-disabled' : ''}`}
        >
          <input {...getInputProps()} />

          <AnimatePresence mode="wait">
            {uploading ? (
              <motion.div
                key="uploading"
                className="upload-progress-container"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <motion.div
                  className="upload-spinner"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                >
                  <svg width="60" height="60" viewBox="0 0 60 60">
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

                <p className="upload-filename">{fileName}</p>
                <div className="progress-bar">
                  <motion.div
                    className="progress-fill"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
                <p className="progress-text">{progress}%</p>
              </motion.div>
            ) : (
              <motion.div
                key="idle"
                className="dropzone-content"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <motion.div
                  className="upload-icon"
                  animate={{
                    y: isDragActive ? [-10, 0] : [0, -10, 0],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                >
                  <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                    />
                  </svg>
                </motion.div>

                <p className="dropzone-text-primary">
                  {isDragActive ? 'Drop your PDF here' : 'Drag & drop your PDF'}
                </p>
                <p className="dropzone-text-secondary">or click to browse</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <AnimatePresence>
          {error && (
            <motion.div
              className="upload-error"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              <span className="error-icon">⚠️</span>
              {error}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  )
}

export default UploadScreen

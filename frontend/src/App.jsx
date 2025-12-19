import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0)

  const loadingMessages = [
    'Processing your PDF',
    'Will take 1-2 minutes',
    'OpenAI translating each section'
  ]

  useEffect(() => {
    if (!loading) {
      setLoadingMessageIndex(0)
      return
    }

    const interval = setInterval(() => {
      setLoadingMessageIndex((prev) => (prev + 1) % loadingMessages.length)
    }, 2000)

    return () => clearInterval(interval)
  }, [loading, loadingMessages.length])

  const validateFile = (selectedFile) => {
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile)
      setError(null)
      setResult(null)
      return true
    } else {
      setError('Please select a PDF file')
      setFile(null)
      return false
    }
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      validateFile(selectedFile)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      validateFile(droppedFile)
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setLoading(true)
    setError(null)
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post('/api/process', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = (type) => {
    if (!result) return

    const url = type === 'extracted' 
      ? result.download_urls.extracted
      : result.download_urls.translated

    window.open(url, '_blank')
  }

  return (
    <div className="app">
      <div className="container">
        <h1 className="title">Bylaw Parser</h1>
        <p className="subtitle">Upload a PDF to extract and translate sections</p>

        <div className="upload-section">
          <label htmlFor="file-input" className="file-label">
            <input
              id="file-input"
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              disabled={loading}
              className="file-input"
            />
            <div
              className={`file-display ${isDragging ? 'dragging' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              {file ? (
                <div className="file-info">
                  <span className="file-icon">📄</span>
                  <span className="file-name">{file.name}</span>
                </div>
              ) : (
                <div className="file-placeholder">
                  <span className="upload-icon">📤</span>
                  <span>{isDragging ? 'Drop PDF file here' : 'Drag & drop PDF file or click to choose'}</span>
                </div>
              )}
            </div>
          </label>

          {file && !loading && !result && (
            <button onClick={handleUpload} className="upload-btn">
              Process PDF
            </button>
          )}

          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              <p className="loading-message">{loadingMessages[loadingMessageIndex]}</p>
            </div>
          )}

          {error && (
            <div className="error">
              <span>⚠️</span>
              <p>{error}</p>
            </div>
          )}

          {result && (
            <div className="result">
              <div className="result-info">
                <p className="success-message">✓ Processing complete!</p>
                <p className="result-stats">
                  {result.sections_count} sections extracted, {result.translated_count} translated
                </p>
              </div>
              <div className="download-buttons">
                <button
                  onClick={() => handleDownload('extracted')}
                  className="download-btn"
                >
                  📥 Download Extracted Sections
                </button>
                <button
                  onClick={() => handleDownload('translated')}
                  className="download-btn"
                >
                  📥 Download Translated Sections
                </button>
              </div>
              <button
                onClick={() => {
                  setFile(null)
                  setResult(null)
                  setError(null)
                  document.getElementById('file-input').value = ''
                }}
                className="reset-btn"
              >
                Upload Another File
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App


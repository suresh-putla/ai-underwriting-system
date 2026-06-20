import React, { useState, useRef } from 'react'

const DocumentUpload = ({ onFileUpload }) => {
  const [isDragging, setIsDragging] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState([])
  const fileInputRef = useRef(null)

  const handleDragEnter = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    const files = Array.from(e.dataTransfer.files)
    handleFiles(files)
  }

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files)
    handleFiles(files)
  }

  const handleFiles = (files) => {
    setSelectedFiles(files)
    if (onFileUpload) {
      onFileUpload(files)
    }
  }

  const handleBrowseClick = () => {
    fileInputRef.current?.click()
  }

  const handleRemoveFile = (index) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index)
    setSelectedFiles(newFiles)
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
          <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>
        <h2 className="text-xl font-bold text-navy-900 tracking-tight">Drop your documents</h2>
      </div>

      {/* Drop Zone */}
      <div
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 ${
          isDragging
            ? 'border-primary-500 bg-primary-50'
            : 'border-navy-200 bg-navy-50 hover:border-primary-400 hover:bg-primary-50/50'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileSelect}
          className="hidden"
          accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
        />

        <div className="flex flex-col items-center">
          <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mb-4 shadow-md">
            <svg className="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>

          <p className="text-lg font-semibold text-navy-900 mb-2">
            {isDragging ? 'Drop files here' : 'Drag and drop your files here'}
          </p>
          <p className="text-sm text-navy-600 mb-4">
            or
          </p>
          <button
            onClick={handleBrowseClick}
            className="btn-primary text-sm px-6 py-2.5"
          >
            Browse Files
          </button>
          <p className="text-xs text-navy-500 mt-4">
            Supported formats: PDF, JPG, PNG, DOC, DOCX (Max 10MB per file)
          </p>
        </div>
      </div>

      {/* Selected Files List */}
      {selectedFiles.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-semibold text-navy-700 mb-3">Selected Files ({selectedFiles.length})</h3>
          <div className="space-y-2">
            {selectedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-navy-50 rounded-lg border border-navy-200"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <div className="w-8 h-8 bg-primary-100 rounded flex items-center justify-center flex-shrink-0">
                    <svg className="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-navy-900 truncate">{file.name}</p>
                    <p className="text-xs text-navy-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleRemoveFile(index)}
                  className="ml-3 p-1.5 hover:bg-red-100 rounded transition-colors flex-shrink-0"
                  title="Remove file"
                >
                  <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
          </div>

          <button className="w-full mt-4 btn-primary py-3 font-semibold">
            Upload {selectedFiles.length} {selectedFiles.length === 1 ? 'File' : 'Files'}
          </button>
        </div>
      )}
    </div>
  )
}

export default DocumentUpload

import React, { useState } from 'react'
import apiClient from '../api/client'

const RAGConfiguration = () => {
  const [config, setConfig] = useState({
    collection_name: 'loan_documents',
    chunk_size: 1000,
    chunk_overlap: 200,
    embedding_model: 'text-embedding-3-small',
    use_local_embeddings: false,
    persist_directory: './chroma_db'
  })

  const [status, setStatus] = useState({ type: '', message: '' })
  const [loading, setLoading] = useState(false)

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setConfig(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleCreateCollection = async () => {
    setLoading(true)
    setStatus({ type: '', message: '' })

    try {
      const response = await apiClient.post('/rag/init', config)
      setStatus({
        type: 'success',
        message: response.data.message || 'RAG system initialized successfully!'
      })
    } catch (error) {
      setStatus({
        type: 'error',
        message: error.response?.data?.detail || 'Failed to initialize RAG system'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl p-6 shadow-lg border-2 border-navy-100 hover:border-primary-200 transition-all duration-300 hover:shadow-xl h-fit">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
          <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <div>
          <h2 className="text-xl font-semibold text-navy-900">RAG Configuration</h2>
          <p className="text-sm text-navy-600">Configure and initialize RAG system</p>
        </div>
      </div>

      <div className="space-y-4">
        {/* Collection Name */}
        <div>
          <label htmlFor="collection_name" className="block text-sm font-medium mb-2 text-navy-900">
            Collection Name
          </label>
          <input
            id="collection_name"
            name="collection_name"
            type="text"
            value={config.collection_name}
            onChange={handleInputChange}
            className="input-field"
            placeholder="loan_documents"
            disabled={loading}
          />
        </div>

        {/* Chunk Size */}
        <div>
          <label htmlFor="chunk_size" className="block text-sm font-medium mb-2 text-navy-900">
            Chunk Size
          </label>
          <input
            id="chunk_size"
            name="chunk_size"
            type="number"
            value={config.chunk_size}
            onChange={handleInputChange}
            className="input-field"
            min="100"
            max="5000"
            disabled={loading}
          />
          <p className="text-xs text-navy-500 mt-1">Size of text chunks (100-5000)</p>
        </div>

        {/* Chunk Overlap */}
        <div>
          <label htmlFor="chunk_overlap" className="block text-sm font-medium mb-2 text-navy-900">
            Chunk Overlap
          </label>
          <input
            id="chunk_overlap"
            name="chunk_overlap"
            type="number"
            value={config.chunk_overlap}
            onChange={handleInputChange}
            className="input-field"
            min="0"
            max="1000"
            disabled={loading}
          />
          <p className="text-xs text-navy-500 mt-1">Overlap between chunks (0-1000)</p>
        </div>

        {/* Embedding Model */}
        <div>
          <label htmlFor="embedding_model" className="block text-sm font-medium mb-2 text-navy-900">
            Embedding Model
          </label>
          <select
            id="embedding_model"
            name="embedding_model"
            value={config.embedding_model}
            onChange={handleInputChange}
            className="input-field"
            disabled={loading}
          >
            <option value="text-embedding-3-small">text-embedding-3-small</option>
            <option value="text-embedding-3-large">text-embedding-3-large</option>
            <option value="text-embedding-ada-002">text-embedding-ada-002</option>
          </select>
        </div>

        {/* Use Local Embeddings */}
        <div className="flex items-center gap-3">
          <input
            id="use_local_embeddings"
            name="use_local_embeddings"
            type="checkbox"
            checked={config.use_local_embeddings}
            onChange={handleInputChange}
            className="w-4 h-4 text-primary-600 border-navy-300 rounded focus:ring-primary-500"
            disabled={loading}
          />
          <label htmlFor="use_local_embeddings" className="text-sm font-medium text-navy-900">
            Use Local Embeddings (for testing)
          </label>
        </div>

        {/* Status Message */}
        {status.message && (
          <div
            className={`p-3 rounded-lg text-sm ${
              status.type === 'success'
                ? 'bg-green-50 border border-green-200 text-green-700'
                : 'bg-red-50 border border-red-200 text-red-700'
            }`}
          >
            {status.message}
          </div>
        )}

        {/* Create Collection Button */}
        <button
          onClick={handleCreateCollection}
          disabled={loading}
          className="btn-primary w-full py-3 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Initializing...
            </span>
          ) : (
            'Create Collection'
          )}
        </button>
      </div>
    </div>
  )
}

export default RAGConfiguration

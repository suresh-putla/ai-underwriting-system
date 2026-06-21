import React, { useState, useRef, useEffect } from 'react'
import apiClient from '../api/client'

const RAGChat = () => {
  const [messages, setMessages] = useState([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim() || loading) return

    const userQuery = query.trim()
    setQuery('')

    // Add user message
    const userMessage = { type: 'user', content: userQuery, timestamp: new Date() }
    setMessages(prev => [...prev, userMessage])

    setLoading(true)

    try {
      const response = await apiClient.post('/rag/search', {
        query: userQuery,
        k: 4
      })

      // Add bot response
      const botMessage = {
        type: 'bot',
        content: response.data.results,
        query: userQuery,
        count: response.data.count,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, botMessage])

    } catch (error) {
      const errorMessage = {
        type: 'error',
        content: error.response?.data?.detail || 'Failed to search. Make sure RAG system is initialized.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([])
  }

  return (
    <div className="bg-white rounded-xl shadow-lg border-2 border-navy-100 hover:border-primary-200 transition-all duration-300 hover:shadow-xl flex flex-col h-[600px]">
      {/* Header */}
      <div className="p-6 border-b border-navy-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-navy-900">RAG Search</h2>
              <p className="text-sm text-navy-600">Query your document collection</p>
            </div>
          </div>
          {messages.length > 0 && (
            <button
              onClick={clearChat}
              className="text-sm text-navy-600 hover:text-navy-900 font-medium"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-navy-50 rounded-full flex items-center justify-center mb-4">
              <svg className="w-8 h-8 text-navy-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-navy-900 mb-2">Start Searching</h3>
            <p className="text-sm text-navy-600 max-w-sm">
              Enter a query below to search through your document collection using RAG
            </p>
          </div>
        ) : (
          messages.map((message, idx) => (
            <div key={idx} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              {message.type === 'user' ? (
                <div className="bg-gray-200 text-gray-900 rounded-lg px-4 py-3 max-w-[80%]">
                  <p className="text-sm">{message.content}</p>
                </div>
              ) : message.type === 'error' ? (
                <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 max-w-[80%]">
                  <p className="text-sm text-red-700">{message.content}</p>
                </div>
              ) : (
                <div className="bg-navy-50 rounded-lg px-4 py-3 max-w-[80%]">
                  <p className="text-xs font-medium text-navy-600 mb-2">
                    Found {message.count} results for: "{message.query}"
                  </p>
                  <div className="space-y-3">
                    {message.content.map((doc, docIdx) => (
                      <div key={docIdx} className="bg-white rounded-lg p-3 border border-navy-100">
                        <p className="text-sm text-navy-900 mb-2">{doc.page_content}</p>
                        {doc.metadata && (
                          <div className="text-xs text-navy-500">
                            {doc.metadata.source && (
                              <span className="inline-block bg-navy-100 rounded px-2 py-0.5 mr-2">
                                {doc.metadata.source.split('/').pop()}
                              </span>
                            )}
                            {doc.metadata.page !== undefined && (
                              <span className="inline-block bg-navy-100 rounded px-2 py-0.5">
                                Page {doc.metadata.page}
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-navy-50 rounded-lg px-4 py-3">
              <div className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4 text-navy-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span className="text-sm text-navy-600">Searching...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSearch} className="p-4 border-t border-navy-100">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your search query..."
            className="input-field flex-1"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="btn-primary px-6 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </button>
        </div>
      </form>
    </div>
  )
}

export default RAGChat

import React, { useState, useRef, useEffect } from 'react'
import apiClient from '../api/client'

const RAGLLMChat = () => {
  const [messages, setMessages] = useState([])
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [streaming, setStreaming] = useState(false)
  const messagesEndRef = useRef(null)
  const currentStreamRef = useRef('')

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
    setStreaming(true)
    currentStreamRef.current = ''

    // Add placeholder bot message for streaming
    const botMessageIndex = messages.length + 1
    setMessages(prev => [...prev, {
      type: 'bot',
      content: '',
      streaming: true,
      timestamp: new Date()
    }])

    try {
      const response = await fetch(`${apiClient.defaults.baseURL}/rag/llm-search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userQuery,
          k: 4
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          setStreaming(false)
          // Update final message to mark streaming complete
          setMessages(prev => prev.map((msg, idx) =>
            idx === botMessageIndex ? { ...msg, streaming: false } : msg
          ))
          break
        }

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)

            if (data === '[DONE]') {
              setStreaming(false)
              setMessages(prev => prev.map((msg, idx) =>
                idx === botMessageIndex ? { ...msg, streaming: false } : msg
              ))
              continue
            }

            try {
              const parsed = JSON.parse(data)
              if (parsed.content) {
                currentStreamRef.current += parsed.content
                // Update the streaming message with accumulated content
                setMessages(prev => prev.map((msg, idx) =>
                  idx === botMessageIndex
                    ? { ...msg, content: currentStreamRef.current }
                    : msg
                ))
              }
            } catch (e) {
              // Skip invalid JSON chunks
              console.debug('Skipping non-JSON chunk:', data)
            }
          }
        }
      }

    } catch (error) {
      console.error('Stream error:', error)
      const errorMessage = {
        type: 'error',
        content: error.message || 'Failed to get response. Make sure RAG system is initialized.',
        timestamp: new Date()
      }
      // Replace streaming message with error
      setMessages(prev => [...prev.slice(0, botMessageIndex), errorMessage])
    } finally {
      setLoading(false)
      setStreaming(false)
      currentStreamRef.current = ''
    }
  }

  const clearChat = () => {
    setMessages([])
    currentStreamRef.current = ''
  }

  return (
    <div className="bg-white rounded-xl shadow-lg border-2 border-navy-100 hover:border-primary-200 transition-all duration-300 hover:shadow-xl flex flex-col h-[600px]">
      {/* Header */}
      <div className="p-6 border-b border-navy-100">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-navy-900">RAG Search + LLM</h2>
              <p className="text-sm text-navy-600">Chat with your documents using AI</p>
            </div>
          </div>
          {messages.length > 0 && (
            <button
              onClick={clearChat}
              className="text-sm text-navy-600 hover:text-navy-900 font-medium"
              disabled={streaming}
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
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-navy-900 mb-2">Start a Conversation</h3>
            <p className="text-sm text-navy-600 max-w-sm">
              Ask questions about your documents. I'll search relevant content and provide AI-powered answers.
            </p>
          </div>
        ) : (
          messages.map((message, idx) => (
            <div key={idx} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              {message.type === 'user' ? (
                <div className="bg-gray-200 text-gray-900 rounded-lg px-4 py-3 max-w-[80%]">
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                </div>
              ) : message.type === 'error' ? (
                <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 max-w-[80%]">
                  <p className="text-sm text-red-700">{message.content}</p>
                </div>
              ) : (
                <div className="bg-navy-50 rounded-lg px-4 py-3 max-w-[85%]">
                  <div className="text-sm text-navy-900 whitespace-pre-wrap">
                    {message.content || (message.streaming ? '...' : '')}
                    {message.streaming && (
                      <span className="inline-block w-2 h-4 bg-primary-600 ml-1 animate-pulse"></span>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
        {loading && messages.length > 0 && !streaming && (
          <div className="flex justify-start">
            <div className="bg-navy-50 rounded-lg px-4 py-3">
              <div className="flex items-center gap-2">
                <svg className="animate-spin h-4 w-4 text-navy-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span className="text-sm text-navy-600">Thinking...</span>
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
            placeholder="Ask a question about your documents..."
            className="input-field flex-1"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="btn-primary px-6 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            )}
          </button>
        </div>
      </form>
    </div>
  )
}

export default RAGLLMChat

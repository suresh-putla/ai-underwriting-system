import React, { useState } from 'react'

const FloatingChatButton = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [chatMessages, setChatMessages] = useState([
    {
      id: 1,
      type: 'bot',
      text: 'Hello! How can I help you with your loan application today?',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ])

  const toggleChat = () => {
    setIsOpen(!isOpen)
  }

  const handleSendMessage = (e) => {
    e.preventDefault()
    if (message.trim()) {
      const newMessage = {
        id: chatMessages.length + 1,
        type: 'user',
        text: message,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
      setChatMessages([...chatMessages, newMessage])
      setMessage('')

      // Simulate bot response after a delay
      setTimeout(() => {
        const botResponse = {
          id: chatMessages.length + 2,
          type: 'bot',
          text: 'Thank you for your message. A loan specialist will respond shortly.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
        setChatMessages(prev => [...prev, botResponse])
      }, 1000)
    }
  }

  return (
    <>
      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-96 h-[500px] bg-white rounded-2xl shadow-2xl border-2 border-navy-100 flex flex-col z-50 animate-slide-up">
          {/* Chat Header */}
          <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white p-4 rounded-t-2xl flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <div>
                <h3 className="font-bold text-lg">LOUS Support</h3>
                <p className="text-xs text-primary-100">We're here to help</p>
              </div>
            </div>
            <button
              onClick={toggleChat}
              className="p-1 hover:bg-white/20 rounded-lg transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
            {chatMessages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[75%] ${msg.type === 'user' ? 'order-2' : 'order-1'}`}>
                  <div
                    className={`rounded-2xl px-4 py-3 ${
                      msg.type === 'user'
                        ? 'bg-primary-600 text-white rounded-br-sm'
                        : 'bg-white text-navy-900 border border-navy-200 rounded-bl-sm shadow-sm'
                    }`}
                  >
                    <p className="text-sm">{msg.text}</p>
                  </div>
                  <p className={`text-xs text-navy-500 mt-1 ${msg.type === 'user' ? 'text-right' : 'text-left'}`}>
                    {msg.timestamp}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Chat Input */}
          <form onSubmit={handleSendMessage} className="p-4 border-t border-navy-200 bg-white rounded-b-2xl">
            <div className="flex gap-2">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 px-4 py-2.5 rounded-lg border border-navy-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none text-sm"
              />
              <button
                type="submit"
                className="bg-primary-600 text-white p-2.5 rounded-lg hover:bg-primary-700 transition-colors flex-shrink-0"
                disabled={!message.trim()}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Floating Button */}
      <button
        onClick={toggleChat}
        className="fixed bottom-6 right-6 w-16 h-16 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-full shadow-2xl hover:shadow-3xl hover:scale-110 transition-all duration-300 flex items-center justify-center z-40 ring-4 ring-primary-100"
        aria-label="Open chat"
      >
        {isOpen ? (
          <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <>
            <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            {/* Notification Badge */}
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center ring-2 ring-white">
              1
            </span>
          </>
        )}
      </button>

      {/* Pulsing Ring Animation */}
      {!isOpen && (
        <div className="fixed bottom-6 right-6 w-16 h-16 z-30 pointer-events-none">
          <span className="absolute inset-0 rounded-full bg-primary-400 animate-ping opacity-75"></span>
        </div>
      )}
    </>
  )
}

export default FloatingChatButton

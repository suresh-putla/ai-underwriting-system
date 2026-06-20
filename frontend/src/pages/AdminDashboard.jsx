import React, { useState } from 'react'
import RAGSetup from '../components/RAGSetup'
import UserSetup from '../components/UserSetup'

const AdminDashboard = ({ onLogout }) => {
  const [activeTab, setActiveTab] = useState('rag-setup')

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="border-b border-navy-100 sticky top-0 bg-white/80 backdrop-blur-lg z-50 shadow-sm">
        <div className="container-custom">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">L</span>
              </div>
              <span className="text-xl font-semibold text-navy-900">LOUS Admin</span>
            </div>

            <div className="flex items-center gap-4">
              <button className="relative p-2 hover:bg-navy-50 rounded-lg transition-colors">
                <svg className="w-5 h-5 text-navy-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
              </button>
              <button
                onClick={onLogout}
                className="btn-secondary text-sm px-4 py-2"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="container-custom py-8">
        {/* Welcome Section */}
        <div className="mb-10">
          <h1 className="text-4xl font-bold text-navy-900 mb-3 tracking-tight">Admin Dashboard</h1>
          <p className="text-lg text-navy-600 font-medium">Manage RAG system and user configurations</p>
        </div>

        {/* Tabs */}
        <div className="border-b-2 border-navy-100 mb-8">
          <nav className="flex gap-8">
            <button
              onClick={() => setActiveTab('rag-setup')}
              className={`pb-4 px-1 text-sm font-semibold border-b-2 transition-colors ${
                activeTab === 'rag-setup'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-navy-600 hover:text-navy-900 hover:border-navy-300'
              }`}
            >
              RAG Setup
            </button>
            <button
              onClick={() => setActiveTab('user-setup')}
              className={`pb-4 px-1 text-sm font-semibold border-b-2 transition-colors ${
                activeTab === 'user-setup'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-navy-600 hover:text-navy-900 hover:border-navy-300'
              }`}
            >
              User Setup
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        <div className="mt-6">
          {activeTab === 'rag-setup' && <RAGSetup />}
          {activeTab === 'user-setup' && <UserSetup />}
        </div>
      </div>
    </div>
  )
}

export default AdminDashboard

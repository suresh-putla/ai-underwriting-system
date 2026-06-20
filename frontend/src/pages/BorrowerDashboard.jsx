import React, { useState, useEffect } from 'react'
import DocumentUpload from '../components/DocumentUpload'
import SubmittedDocuments from '../components/SubmittedDocuments'
import ApplicationTracker from '../components/ApplicationTracker'
import CommentsTimeline from '../components/CommentsTimeline'
import FloatingChatButton from '../components/FloatingChatButton'
import { getSubmittedDocs } from '../api/client'

const BorrowerDashboard = ({ username, onLogout }) => {
  const [documents, setDocuments] = useState([])
  const [documentsLoading, setDocumentsLoading] = useState(true)
  const [documentsError, setDocumentsError] = useState(null)

  const [applicationStage, setApplicationStage] = useState(1) // 0-3 for the 4 stages

  // Fetch submitted documents from API
  useEffect(() => {
    const fetchSubmittedDocs = async () => {
      if (!username) return

      try {
        setDocumentsLoading(true)
        setDocumentsError(null)
        const response = await getSubmittedDocs(username)

        // Transform API response to match component format
        // API returns {user_id, documents, count}
        const transformedDocs = (response.documents || []).map((doc, index) => ({
          id: index + 1,
          type: doc.DOC_TYPE,
          filename: doc.DOC_TYPE,
          status: doc.STATUS,
          uploadedAt: new Date().toISOString().split('T')[0] // Use current date as placeholder
        }))

        setDocuments(transformedDocs)
      } catch (err) {
        console.error('Error fetching submitted documents:', err)
        setDocumentsError(err.message || 'Failed to load documents')
      } finally {
        setDocumentsLoading(false)
      }
    }

    fetchSubmittedDocs()
  }, [username])

  const [comments, setComments] = useState([
    {
      id: 1,
      title: 'Application Submitted',
      description: 'Your loan application has been successfully received.',
      timestamp: '2024-06-10 09:30 AM',
      status: 'completed'
    },
    {
      id: 2,
      title: 'Documents Under Review',
      description: 'Our team is reviewing your submitted documents.',
      timestamp: '2024-06-15 02:15 PM',
      status: 'completed'
    },
    {
      id: 3,
      title: 'ID Proof Issue',
      description: 'Your ID proof document was rejected. Please upload a clearer image.',
      timestamp: '2024-06-18 11:45 AM',
      status: 'alert'
    },
    {
      id: 4,
      title: 'Awaiting Additional Documents',
      description: 'Please upload a recent utility bill for address verification.',
      timestamp: '2024-06-19 03:20 PM',
      status: 'pending'
    }
  ])

  const handleFileUpload = (files) => {
    // Handle file upload logic
    console.log('Files uploaded:', files)
    // In a real app, you would upload to server and update documents state
  }

  const handleRemoveDocument = (documentId) => {
    setDocuments(documents.filter(doc => doc.id !== documentId))
  }

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
              <span className="text-xl font-semibold text-navy-900">LOUS</span>
            </div>

            <div className="flex items-center gap-4">
              <button className="relative p-2 hover:bg-navy-50 rounded-lg transition-colors">
                <svg className="w-5 h-5 text-navy-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-primary-500 rounded-full"></span>
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
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-navy-900 mb-3 tracking-tight">My Loan Application</h1>
          <p className="text-lg text-navy-600 font-medium">Track your application progress and manage documents</p>
        </div>

        {/* 2x2 Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Row 1, Column 1 - Document Upload */}
          <div className="bg-white rounded-xl border-2 border-navy-100 shadow-lg overflow-hidden">
            <DocumentUpload onFileUpload={handleFileUpload} />
          </div>

          {/* Row 1, Column 2 - Application Tracker */}
          <div className="bg-white rounded-xl border-2 border-navy-100 shadow-lg overflow-hidden">
            <ApplicationTracker currentStage={applicationStage} />
          </div>

          {/* Row 2, Column 1 - Submitted Documents */}
          <div className="bg-white rounded-xl border-2 border-navy-100 shadow-lg overflow-hidden">
            <SubmittedDocuments
              documents={documents}
              loading={documentsLoading}
              error={documentsError}
              onRemoveDocument={handleRemoveDocument}
            />
          </div>

          {/* Row 2, Column 2 - Comments Timeline */}
          <div className="bg-white rounded-xl border-2 border-navy-100 shadow-lg overflow-hidden">
            <CommentsTimeline comments={comments} />
          </div>
        </div>
      </div>

      {/* Floating Chat Button */}
      <FloatingChatButton />
    </div>
  )
}

export default BorrowerDashboard

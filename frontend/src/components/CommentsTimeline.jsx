import React from 'react'

const CommentsTimeline = ({ comments }) => {
  const getStatusColors = (status) => {
    switch (status) {
      case 'completed':
        return {
          bg: 'bg-green-500',
          text: 'text-green-700',
          iconBg: 'bg-green-100'
        }
      case 'pending':
        return {
          bg: 'bg-yellow-500',
          text: 'text-yellow-700',
          iconBg: 'bg-yellow-100'
        }
      case 'alert':
        return {
          bg: 'bg-red-500',
          text: 'text-red-700',
          iconBg: 'bg-red-100'
        }
      default:
        return {
          bg: 'bg-navy-500',
          text: 'text-navy-700',
          iconBg: 'bg-navy-100'
        }
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        )
      case 'pending':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
          </svg>
        )
      case 'alert':
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        )
      default:
        return (
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
        )
    }
  }

  return (
    <div className="p-6 flex flex-col h-full">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
          <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </div>
        <h2 className="text-xl font-bold text-navy-900 tracking-tight">Comments</h2>
      </div>

      {comments.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-center py-12">
          <div>
            <div className="w-16 h-16 bg-navy-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-navy-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
            </div>
            <p className="text-navy-600 font-medium">No updates yet</p>
            <p className="text-sm text-navy-500 mt-1">Updates will appear here</p>
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto">
          <div className="relative">
            {/* Vertical Timeline Line */}
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-navy-200" />

            {/* Timeline Items */}
            <div className="space-y-6">
              {comments.map((comment, index) => {
                const colors = getStatusColors(comment.status)
                const isLast = index === comments.length - 1

                return (
                  <div key={comment.id} className="relative pl-12">
                    {/* Metro Stop Circle */}
                    <div className={`absolute left-0 w-8 h-8 rounded-full ${colors.bg} flex items-center justify-center text-white shadow-lg ring-4 ring-white z-10`}>
                      {getStatusIcon(comment.status)}
                    </div>

                    {/* Content Card */}
                    <div className={`bg-navy-50 rounded-lg p-4 border-l-4 ${
                      comment.status === 'completed' ? 'border-green-500' :
                      comment.status === 'pending' ? 'border-yellow-500' :
                      comment.status === 'alert' ? 'border-red-500' :
                      'border-navy-500'
                    } hover:shadow-md transition-shadow`}>
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <h3 className={`font-bold text-sm ${colors.text}`}>
                          {comment.title}
                        </h3>
                        {!isLast && (
                          <span className={`inline-flex px-2 py-1 rounded text-xs font-semibold ${colors.iconBg} ${colors.text} whitespace-nowrap`}>
                            {comment.status.charAt(0).toUpperCase() + comment.status.slice(1)}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-navy-700 mb-2">
                        {comment.description}
                      </p>
                      <div className="flex items-center gap-2 text-xs text-navy-500">
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className="font-medium">{comment.timestamp}</span>
                      </div>
                    </div>

                    {/* Latest Indicator */}
                    {isLast && (
                      <div className="absolute -left-1 top-0">
                        <span className="flex h-3 w-3">
                          <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${colors.bg} opacity-75`}></span>
                          <span className={`relative inline-flex rounded-full h-3 w-3 ${colors.bg}`}></span>
                        </span>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* Add New Comment Button */}
      <div className="mt-4 pt-4 border-t border-navy-200">
        <button className="w-full btn-outline py-2.5 text-sm font-semibold flex items-center justify-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
          </svg>
          View All Updates
        </button>
      </div>
    </div>
  )
}

export default CommentsTimeline

import React from 'react'

const UserSetup = () => {
  return (
    <div className="bg-white rounded-lg p-6 card-clean border border-navy-100">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
          <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </div>
        <div>
          <h2 className="text-xl font-semibold text-navy-900">User Setup</h2>
          <p className="text-sm text-navy-600">Manage user accounts and permissions</p>
        </div>
      </div>

      <div className="text-center py-12">
        <p className="text-navy-600">User management interface coming soon...</p>
      </div>
    </div>
  )
}

export default UserSetup

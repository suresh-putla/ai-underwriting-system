import React, { useState } from 'react'

const Dashboard = ({ onLogout }) => {
  const [activeTab, setActiveTab] = useState('overview')

  const stats = [
    { label: 'Active Loans', value: '247', change: '+12%', trend: 'up' },
    { label: 'Processing Time', value: '2.3h', change: '-18%', trend: 'down' },
    { label: 'Approval Rate', value: '87%', change: '+5%', trend: 'up' },
    { label: 'Total Volume', value: '$12.4M', change: '+23%', trend: 'up' },
  ]

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
        <div className="mb-10">
          <h1 className="text-4xl font-bold text-navy-900 mb-3 tracking-tight">Dashboard</h1>
          <p className="text-lg text-navy-600 font-medium">Welcome back, here's your loan portfolio overview</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
          {stats.map((stat, idx) => (
            <div
              key={idx}
              className="stat-card"
            >
              <div className="flex justify-between items-start mb-4">
                <span className="text-sm font-semibold text-navy-600 uppercase tracking-wider">{stat.label}</span>
                <span className={`badge text-xs font-bold ${
                  stat.trend === 'up' ? 'badge-primary' : 'badge-accent'
                }`}>
                  {stat.change}
                </span>
              </div>
              <div className="text-4xl font-bold text-navy-900 mb-2 tracking-tight">{stat.value}</div>
              <div className="flex items-center gap-1.5 text-sm text-navy-600 font-medium">
                {stat.trend === 'up' ? (
                  <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 7.414V15a1 1 0 11-2 0V7.414L6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L9 12.586V5a1 1 0 012 0v7.586l2.293-2.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
                <span>vs last month</span>
              </div>
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div className="border-b border-navy-100 mb-6">
          <nav className="flex gap-6">
            {['Overview', 'Applications', 'Underwriting', 'Reports'].map((tab) => (
              <button
                key={tab.toLowerCase()}
                onClick={() => setActiveTab(tab.toLowerCase())}
                className={`pb-3 px-1 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.toLowerCase()
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-navy-600 hover:text-navy-900 hover:border-navy-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </nav>
        </div>

        {/* Main Content Area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Applications */}
          <div className="lg:col-span-2 space-y-5">
            <div className="flex justify-between items-center mb-5">
              <h2 className="text-2xl font-bold text-navy-900 tracking-tight">Recent Applications</h2>
              <button className="text-sm text-primary-600 hover:text-primary-700 font-semibold flex items-center gap-1.5">
                View all
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>

            {[
              { id: 'LN-2024-1247', borrower: 'John Smith', amount: '$450,000', status: 'Under Review', progress: 65, statusColor: 'yellow' },
              { id: 'LN-2024-1246', borrower: 'Sarah Johnson', amount: '$325,000', status: 'Documents Required', progress: 40, statusColor: 'orange' },
              { id: 'LN-2024-1245', borrower: 'Michael Brown', amount: '$580,000', status: 'Approved', progress: 100, statusColor: 'green' },
            ].map((loan) => (
              <div key={loan.id} className="case-card">
                <div className="p-6">
                  <div className="flex justify-between items-start mb-5">
                    <div>
                      <h3 className="font-bold text-lg text-navy-900 mb-1.5 tracking-tight">{loan.borrower}</h3>
                      <p className="text-sm text-navy-500 font-medium">{loan.id}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-lg text-navy-900 tracking-tight">{loan.amount}</p>
                      <span className={`inline-block mt-2 px-3 py-1.5 rounded-full text-xs font-bold ${
                        loan.statusColor === 'green' ? 'bg-green-100 text-green-700' :
                        loan.statusColor === 'yellow' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-orange-100 text-orange-700'
                      }`}>
                        {loan.status}
                      </span>
                    </div>
                  </div>
                  <div className="w-full bg-navy-100 rounded-full h-2.5">
                    <div
                      className="bg-primary-600 h-full rounded-full transition-all duration-500"
                      style={{ width: `${loan.progress}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="bg-white rounded-xl p-6 border-2 border-navy-100 shadow-lg">
              <h3 className="font-bold text-lg text-navy-900 mb-5 tracking-tight">Quick Actions</h3>
              <div className="space-y-3">
                <button className="w-full btn-primary py-3 text-sm font-semibold justify-center flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                  </svg>
                  New Application
                </button>
                <button className="w-full btn-secondary py-3 text-sm font-semibold justify-center flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  Upload Documents
                </button>
                <button className="w-full btn-outline py-3 text-sm font-semibold justify-center flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  View Reports
                </button>
              </div>
            </div>

            {/* AI Feature */}
            <div className="bg-gradient-to-br from-primary-600 to-primary-700 rounded-xl p-6 text-white shadow-xl border-2 border-primary-500">
              <h4 className="font-bold text-lg mb-2 tracking-tight">AI Underwriting</h4>
              <p className="text-sm text-primary-100 mb-5 font-medium">Automate loan decisions with intelligent AI processing</p>
              <button className="bg-white text-primary-600 font-bold px-5 py-2.5 rounded-lg hover:bg-primary-50 transition-colors text-sm shadow-md">
                Learn more →
              </button>
            </div>

            {/* System Status */}
            <div className="bg-white rounded-xl p-6 border-2 border-navy-100 shadow-lg">
              <h4 className="text-sm font-bold text-navy-700 mb-4 uppercase tracking-wider">System Status</h4>
              <div className="space-y-3">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-navy-600 font-semibold">AI Engine</span>
                  <span className="flex items-center gap-2 text-green-600 font-bold">
                    <span className="w-2.5 h-2.5 bg-green-500 rounded-full"></span>
                    Online
                  </span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-navy-600 font-semibold">Database</span>
                  <span className="flex items-center gap-2 text-green-600 font-bold">
                    <span className="w-2.5 h-2.5 bg-green-500 rounded-full"></span>
                    Healthy
                  </span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-navy-600 font-semibold">API Status</span>
                  <span className="flex items-center gap-2 text-green-600 font-bold">
                    <span className="w-2.5 h-2.5 bg-green-500 rounded-full"></span>
                    99.9%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

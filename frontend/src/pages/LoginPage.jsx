import React, { useState } from 'react'
import { authenticateUser } from '../api/client'

const LoginPage = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await authenticateUser(username, password)
      if (response.success) {
        // Pass user role to parent component
        const role = response.role || (username.toLowerCase() === 'admin' ? 'admin' : 'user')
        onLoginSuccess(role)
      } else {
        setError('Invalid credentials')
      }
    } catch (err) {
      setError(err.message || 'Authentication failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Top Navigation */}
      <nav className="border-b border-navy-100 sticky top-0 bg-white z-50">
        <div className="container-custom">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">L</span>
              </div>
              <span className="text-xl font-semibold text-navy-900">LOUS</span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <a href="#" className="nav-link">Solutions</a>
              <a href="#" className="nav-link">How it Works</a>
              <a href="#" className="nav-link">About</a>
              <button className="btn-primary px-5 py-2 text-sm">Get Started</button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="container-custom py-20">
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-16 items-center">
          {/* Left side - Hero content */}
          <div className="space-y-8">
            <div className="space-y-6">
              <div className="inline-block">
                <span className="badge badge-primary text-xs font-semibold">
                  AI-Powered Loan Platform
                </span>
              </div>
              <h1 className="text-5xl md:text-6xl font-semibold text-navy-900 leading-tight tracking-tight">
                Streamline your
                <br />
                loan operations
              </h1>
              <p className="text-xl text-navy-600 leading-relaxed">
                Intelligent loan origination and underwriting platform built for modern financial institutions.
              </p>
            </div>

            {/* Feature List */}
            <div className="space-y-4 pt-4">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg className="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-navy-900">AI-Powered Decisions</h3>
                  <p className="text-navy-600 text-sm">Automated underwriting with machine learning</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg className="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-navy-900">Enterprise Security</h3>
                  <p className="text-navy-600 text-sm">Bank-grade encryption and compliance</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg className="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-navy-900">Real-Time Analytics</h3>
                  <p className="text-navy-600 text-sm">Track performance across your portfolio</p>
                </div>
              </div>
            </div>

            {/* Trust Indicators */}
            <div className="flex items-center gap-6 pt-6 border-t border-navy-100">
              <div>
                <div className="text-2xl font-semibold text-navy-900">$2.4B+</div>
                <div className="text-sm text-navy-600">Loans processed</div>
              </div>
              <div className="w-px h-12 bg-navy-200"></div>
              <div>
                <div className="text-2xl font-semibold text-navy-900">15K+</div>
                <div className="text-sm text-navy-600">Active users</div>
              </div>
              <div className="w-px h-12 bg-navy-200"></div>
              <div>
                <div className="text-2xl font-semibold text-navy-900">99.9%</div>
                <div className="text-sm text-navy-600">Uptime SLA</div>
              </div>
            </div>
          </div>

          {/* Right side - Login form */}
          <div>
            <div className="bg-white rounded-xl p-8 card-clean border border-navy-100">
              <div className="mb-6">
                <h2 className="text-2xl font-semibold text-navy-900 mb-2">Sign in</h2>
                <p className="text-navy-600">Access your loan dashboard</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label htmlFor="username" className="block text-sm font-medium mb-2 text-navy-900">
                    Username
                  </label>
                  <input
                    id="username"
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="input-field"
                    placeholder="Enter your username"
                    required
                    disabled={loading}
                  />
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-medium mb-2 text-navy-900">
                    Password
                  </label>
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="input-field"
                    placeholder="Enter your password"
                    required
                    disabled={loading}
                  />
                  <div className="text-right mt-2">
                    <a href="#" className="text-sm text-primary-600 hover:text-primary-700 font-medium">
                      Forgot password?
                    </a>
                  </div>
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary w-full py-3 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Signing in...
                    </span>
                  ) : (
                    'Sign in'
                  )}
                </button>
              </form>

              <div className="mt-6 pt-6 border-t border-navy-100">
                <p className="text-center text-sm text-navy-600">
                  Don't have an account?{' '}
                  <a href="#" className="text-primary-600 hover:text-primary-700 font-medium">
                    Request access
                  </a>
                </p>
              </div>
            </div>

            <div className="mt-4 text-center text-xs text-navy-500">
              Protected by enterprise-grade security
            </div>
          </div>
        </div>
      </div>

      {/* Trust Logos */}
      <div className="border-t border-navy-100 py-12">
        <div className="container-custom">
          <p className="text-center text-sm text-navy-500 font-medium mb-8 uppercase tracking-wider">
            Trusted by leading financial institutions
          </p>
          <div className="flex flex-wrap items-center justify-center gap-12 opacity-30">
            <div className="text-xl font-semibold text-navy-900">BANK OF AMERICA</div>
            <div className="text-xl font-semibold text-navy-900">WELLS FARGO</div>
            <div className="text-xl font-semibold text-navy-900">CHASE</div>
            <div className="text-xl font-semibold text-navy-900">CITI</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginPage

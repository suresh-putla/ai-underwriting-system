import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import AdminDashboard from './pages/AdminDashboard'
import BorrowerDashboard from './pages/BorrowerDashboard'

function App() {
  // Check for demo mode via URL parameter
  const urlParams = new URLSearchParams(window.location.search);
  const isDemoMode = urlParams.get('demo') === 'true';
  const demoRole = urlParams.get('role') || 'borrower';

  const [isAuthenticated, setIsAuthenticated] = useState(isDemoMode)
  const [userRole, setUserRole] = useState(isDemoMode ? demoRole : null)
  const [username, setUsername] = useState(null)

  const handleLoginSuccess = (role = 'user', userName = null) => {
    setIsAuthenticated(true)
    setUserRole(role)
    setUsername(userName)
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
    setUserRole(null)
    setUsername(null)
  }

  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={
            isAuthenticated ?
            <Navigate to={
              userRole === 'admin' ? '/admin' :
              userRole === 'borrower' ? '/borrower' :
              '/dashboard'
            } replace /> :
            <LoginPage onLoginSuccess={handleLoginSuccess} />
          }
        />
        <Route
          path="/dashboard"
          element={
            isAuthenticated && userRole !== 'admin' && userRole !== 'borrower' ?
            <Dashboard onLogout={handleLogout} /> :
            isAuthenticated && userRole === 'admin' ?
            <Navigate to="/admin" replace /> :
            isAuthenticated && userRole === 'borrower' ?
            <Navigate to="/borrower" replace /> :
            <Navigate to="/login" replace />
          }
        />
        <Route
          path="/borrower"
          element={
            isAuthenticated && userRole === 'borrower' ?
            <BorrowerDashboard username={username} onLogout={handleLogout} /> :
            isAuthenticated && userRole === 'admin' ?
            <Navigate to="/admin" replace /> :
            isAuthenticated ?
            <Navigate to="/dashboard" replace /> :
            <Navigate to="/login" replace />
          }
        />
        <Route
          path="/admin"
          element={
            isAuthenticated && userRole === 'admin' ?
            <AdminDashboard onLogout={handleLogout} /> :
            isAuthenticated && userRole === 'borrower' ?
            <Navigate to="/borrower" replace /> :
            isAuthenticated ?
            <Navigate to="/dashboard" replace /> :
            <Navigate to="/login" replace />
          }
        />
        <Route path="/" element={<Navigate to="/login" replace />} />
      </Routes>
    </Router>
  )
}

export default App

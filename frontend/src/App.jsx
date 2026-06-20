import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import AdminDashboard from './pages/AdminDashboard'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [userRole, setUserRole] = useState(null)

  const handleLoginSuccess = (role = 'user') => {
    setIsAuthenticated(true)
    setUserRole(role)
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
    setUserRole(null)
  }

  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={
            isAuthenticated ?
            <Navigate to={userRole === 'admin' ? '/admin' : '/dashboard'} replace /> :
            <LoginPage onLoginSuccess={handleLoginSuccess} />
          }
        />
        <Route
          path="/dashboard"
          element={
            isAuthenticated && userRole !== 'admin' ?
            <Dashboard onLogout={handleLogout} /> :
            isAuthenticated ?
            <Navigate to="/admin" replace /> :
            <Navigate to="/login" replace />
          }
        />
        <Route
          path="/admin"
          element={
            isAuthenticated && userRole === 'admin' ?
            <AdminDashboard onLogout={handleLogout} /> :
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

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import Welcome from './pages/Welcome'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Admin from './pages/Admin'
import BuyTokens from './pages/BuyTokens'

function ProtectedRoute({ children, adminOnly = false }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>
  }
  
  if (!user) {
    return <Navigate to="/accounts/login/" />
  }
  
  if (adminOnly && !user.is_staff) {
    return <Navigate to="/dashboard/" />
  }
  
  return children
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="app">
          <Routes>
            <Route path="/" element={<Welcome />} />
            <Route path="/accounts/login/" element={<Login />} />
            <Route path="/accounts/register/" element={<Register />} />
            <Route path="/dashboard/" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/admin/" element={
              <ProtectedRoute adminOnly>
                <Admin />
              </ProtectedRoute>
            } />
            <Route path="/tokens/buy/" element={
              <ProtectedRoute>
                <BuyTokens />
              </ProtectedRoute>
            } />
          </Routes>
        </div>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
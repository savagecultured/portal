import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [password2, setPassword2] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { register } = useAuth()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    
    if (password !== password2) {
      setError('Passwords do not match')
      return
    }
    
    if (password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }
    
    setLoading(true)

    try {
      await register({ email, password })
      navigate('/dashboard/')
    } catch (err) {
      setError(err.response?.data?.email?.[0] || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h2>Create Account</h2>
        
        {error && <div className="alert alert-error">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              type="email"
              className="form-input"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">Confirm Password</label>
            <input
              type="password"
              className="form-input"
              value={password2}
              onChange={e => setPassword2(e.target.value)}
              required
            />
          </div>
          
          <button type="submit" className="btn btn-primary w-full" disabled={loading}>
            {loading ? 'Creating account...' : 'Register'}
          </button>
        </form>
        
        <p style={{ textAlign: 'center', marginTop: '1rem', color: '#64748b' }}>
          Already have an account? <Link to="/accounts/login/">Login</Link>
        </p>
        
        <p style={{ textAlign: 'center', marginTop: '1rem', color: '#64748b', fontSize: '0.875rem' }}>
          Register now and get <strong>5 free tokens</strong>
        </p>
      </div>
    </div>
  )
}
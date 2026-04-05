import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import axios from 'axios'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const [tokens, setTokens] = useState([])
  const [sessions, setSessions] = useState([])
  const [available, setAvailable] = useState(0)
  const [loading, setLoading] = useState(true)

  const mediaServices = [
    { name: 'Movies', url: '', icon: '🎬' },
    { name: 'Music', url: '', icon: '🎵' },
    { name: 'Photos', url: '', icon: '📸' },
  ]

  useEffect(() => {
    fetchData()
  }, [])

  async function fetchData() {
    try {
      const [tokensRes, sessionsRes] = await Promise.all([
        axios.get('/tokens/api/'),
        axios.get('/analytics/api/'),
      ])
      setTokens(tokensRes.data)
      setSessions(sessionsRes.data.slice(0, 10))
      setAvailable(tokensRes.data.filter(t => !t.used).length)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function activateToken(tokenId) {
    try {
      await axios.post(`/tokens/api/${tokenId}/activate/`)
      fetchData()
    } catch (err) {
      alert('Failed to activate token')
    }
  }

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>
  }

  return (
    <div className="app">
      <nav className="navbar">
        <span className="navbar-brand">📡 WebMART</span>
        <div className="navbar-links">
          {user?.is_staff && (
            <Link to="/admin/" className="nav-link">Admin</Link>
          )}
          <Link to="/dashboard/" className="nav-link">Dashboard</Link>
          <button onClick={logout} className="btn btn-outline">Logout</button>
        </div>
      </nav>

      <div className="hero">
        <h1>Welcome back!</h1>
        <p>{user?.email}</p>
      </div>

      <div className="cards-grid">
        <div className="stat-card">
          <span className="stat-number">{available}</span>
          <span className="stat-label">Available Tokens</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">{tokens.filter(t => t.used && !t.expired).length}</span>
          <span className="stat-label">Active Now</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">{tokens.length}</span>
          <span className="stat-label">Total Tokens</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">{sessions.length}</span>
          <span className="stat-label">Sessions</span>
        </div>
      </div>

      <div className="card">
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Quick Actions</span>
          <Link to="/tokens/buy/" className="btn btn-primary" style={{ padding: '0.5rem 1rem' }}>Buy Tokens</Link>
        </div>
        <div className="card-body">
          <p style={{ color: '#94a3b8' }}>Purchase more tokens to extend your access</p>
        </div>
      </div>

      <div className="card">
        <div className="card-header">Media Services</div>
        <div className="card-body">
          <div className="media-grid">
            {mediaServices.map(svc => (
              <div key={svc.name} className="media-card">
                <span className="media-icon">{svc.icon}</span>
                <div className="service-name">{svc.name}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">Your Tokens</div>
        <div className="card-body" style={{ padding: 0 }}>
          <table className="table">
            <thead>
              <tr>
                <th>Token</th>
                <th>Source</th>
                <th>Status</th>
                <th>Created</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {tokens.slice(0, 5).map(token => (
                <tr key={token.id}>
                  <td><code>{token.id.slice(0, 8)}</code></td>
                  <td>
                    <span className="badge badge-info">
                      {token.source === 'registration' ? '🎁 Gift' : '💳 Purchased'}
                    </span>
                  </td>
                  <td>
                    {token.is_active ? (
                      <span className="badge badge-success">Active</span>
                    ) : token.used ? (
                      <span className="badge badge-warning">Used</span>
                    ) : (
                      <span className="badge badge-primary">Available</span>
                    )}
                  </td>
                  <td>{new Date(token.created_at).toLocaleDateString()}</td>
                  <td>
                    {!token.used && available > 0 && (
                      <button 
                        onClick={() => activateToken(token.id)}
                        className="btn btn-primary"
                        style={{ padding: '0.25rem 0.75rem', fontSize: '0.875rem' }}
                      >
                        Activate
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {tokens.length === 0 && (
                <tr>
                  <td colSpan="5" style={{ textAlign: 'center' }}>No tokens yet</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '2rem' }}>
        <div className="card-header">Recent Sessions</div>
        <div className="card-body" style={{ padding: 0 }}>
          <table className="table">
            <thead>
              <tr>
                <th>Start</th>
                <th>End</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
              {sessions.slice(0, 5).map(session => (
                <tr key={session.id}>
                  <td>{new Date(session.start_time).toLocaleString()}</td>
                  <td>{session.end_time ? new Date(session.end_time).toLocaleString() : 'Active'}</td>
                  <td>{session.duration_seconds ? `${Math.floor(session.duration_seconds / 60)}m` : '-'}</td>
                </tr>
              ))}
              {sessions.length === 0 && (
                <tr>
                  <td colSpan="3" style={{ textAlign: 'center' }}>No sessions yet</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <footer className="footer">
        📡 WebMART — Guest WiFi Portal
      </footer>
    </div>
  )
}
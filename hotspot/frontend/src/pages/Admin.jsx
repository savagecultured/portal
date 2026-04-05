import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import axios from 'axios'

export default function Admin() {
  const { user, logout } = useAuth()
  const [stats, setStats] = useState(null)
  const [recentUsers, setRecentUsers] = useState([])
  const [recentSessions, setRecentSessions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  async function fetchData() {
    try {
      // Fetch all needed data
      const [usersRes, tokensRes, sessionsRes, purchasesRes] = await Promise.all([
        axios.get('/accounts/api/'),
        axios.get('/tokens/api/'),
        axios.get('/analytics/api/'),
        axios.get('/tokens/purchase/api/'),
      ])
      
      const users = usersRes.data
      const tokens = tokensRes.data
      const sessions = sessionsRes.data
      const purchases = purchasesRes.data
      
      const activeTokens = tokens.filter(t => t.used && !t.expired)
      const purchasedTokens = tokens.filter(t => t.source === 'purchase')
      const revenue = purchases
        .filter(p => p.status === 'completed')
        .reduce((sum, p) => sum + parseFloat(p.amount), 0)
      
      setStats({
        total_users: users.length,
        active_users: users.filter(u => u.is_active).length,
        total_tokens: tokens.length,
        available_tokens: tokens.filter(t => !t.used).length,
        active_tokens: activeTokens.length,
        purchased_tokens: purchasedTokens.length,
        total_sessions: sessions.length,
        active_sessions: sessions.filter(s => !s.end_time).length,
        revenue: revenue.toFixed(2),
      })
      
      setRecentUsers(users.slice(0, 5))
      setRecentSessions(sessions.slice(0, 5))
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
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
          <Link to="/admin/" className="nav-link">Admin</Link>
          <Link to="/dashboard/" className="nav-link">Dashboard</Link>
          <Link to="/admin/" className="btn btn-outline">Django Admin</Link>
          <button onClick={logout} className="btn btn-outline">Logout</button>
        </div>
      </nav>

      <div style={{ padding: '2rem' }}>
        <h2 style={{ marginBottom: '1.5rem' }}>Admin Dashboard</h2>
        
        <div className="cards-grid">
          <div className="stat-card">
            <span className="stat-number">{stats?.total_users || 0}</span>
            <span className="stat-label">Total Users</span>
          </div>
          <div className="stat-card">
            <span className="stat-number">{stats?.active_users || 0}</span>
            <span className="stat-label">Active Users</span>
          </div>
          <div className="stat-card">
            <span className="stat-number">{stats?.total_tokens || 0}</span>
            <span className="stat-label">Total Tokens</span>
          </div>
          <div className="stat-card">
            <span className="stat-number">${stats?.revenue || 0}</span>
            <span className="stat-label">Revenue</span>
          </div>
        </div>

        <div className="card">
          <div className="card-header">Token Overview</div>
          <div className="card-body">
            <div className="cards-grid">
              <div className="stat-card">
                <span className="stat-number">{stats?.available_tokens || 0}</span>
                <span className="stat-label">Available</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">{stats?.active_tokens || 0}</span>
                <span className="stat-label">Active Now</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">{stats?.purchased_tokens || 0}</span>
                <span className="stat-label">Purchased</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">{stats?.active_sessions || 0}</span>
                <span className="stat-label">Active Sessions</span>
              </div>
            </div>
          </div>
        </div>

        <div className="cards-grid" style={{ marginBottom: '2rem' }}>
          <div className="stat-card" style={{ cursor: 'pointer' }}>
            <Link to="/admin/auth/user/add/" style={{ color: 'inherit', textDecoration: 'none' }}>
              <span className="stat-number" style={{ fontSize: '2rem' }}>➕</span>
              <span className="stat-label">Add User</span>
            </Link>
          </div>
          <div className="stat-card" style={{ cursor: 'pointer' }}>
            <Link to="/admin/apps/tokens/token/add/" style={{ color: 'inherit', textDecoration: 'none' }}>
              <span className="stat-number" style={{ fontSize: '2rem' }}>🎫</span>
              <span className="stat-label">Add Token</span>
            </Link>
          </div>
          <div className="stat-card" style={{ cursor: 'pointer' }}>
            <Link to="/admin/" style={{ color: 'inherit', textDecoration: 'none' }}>
              <span className="stat-number" style={{ fontSize: '2rem' }}>⚙️</span>
              <span className="stat-label">Django Admin</span>
            </Link>
          </div>
          <div className="stat-card" style={{ cursor: 'pointer' }}>
            <Link to="/" style={{ color: 'inherit', textDecoration: 'none' }}>
              <span className="stat-number" style={{ fontSize: '2rem' }}>🏠</span>
              <span className="stat-label">View Site</span>
            </Link>
          </div>
        </div>

        <div className="card">
          <div className="card-header">Recent Users</div>
          <div className="card-body" style={{ padding: 0 }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Email</th>
                  <th>Joined</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recentUsers.map(u => (
                  <tr key={u.id}>
                    <td>{u.email}</td>
                    <td>{new Date(u.date_joined).toLocaleDateString()}</td>
                    <td>
                      {u.is_active ? (
                        <span className="badge badge-success">Active</span>
                      ) : (
                        <span className="badge badge-warning">Inactive</span>
                      )}
                    </td>
                  </tr>
                ))}
                {recentUsers.length === 0 && (
                  <tr><td colSpan="3" style={{ textAlign: 'center' }}>No users yet</td></tr>
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
                  <th>User</th>
                  <th>Start</th>
                  <th>Duration</th>
                  <th>Data</th>
                </tr>
              </thead>
              <tbody>
                {recentSessions.map(s => (
                  <tr key={s.id}>
                    <td>{s.user?.email || 'Unknown'}</td>
                    <td>{new Date(s.start_time).toLocaleString()}</td>
                    <td>{s.duration_seconds ? `${Math.floor(s.duration_seconds / 60)}m` : '-'}</td>
                    <td>{s.total_bytes ? `${(s.total_bytes / 1024 / 1024).toFixed(2)} MB` : '-'}</td>
                  </tr>
                ))}
                {recentSessions.length === 0 && (
                  <tr><td colSpan="4" style={{ textAlign: 'center' }}>No sessions yet</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <footer className="footer">
        📡 WebMART — Guest WiFi Portal
      </footer>
    </div>
  )
}
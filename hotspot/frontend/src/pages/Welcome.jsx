import { useState } from 'react'
import { Link } from 'react-router-dom'

export default function Welcome() {
  const services = [
    { name: 'Movies', url: '', icon: '🎬', desc: 'Movies & TV' },
    { name: 'Music', url: '', icon: '🎵', desc: 'Streaming' },
    { name: 'Photos', url: '', icon: '📸', desc: 'Library' },
  ]

  return (
    <div className="app">
      <nav className="navbar">
        <span className="navbar-brand">📡 WebMART</span>
        <div className="navbar-links">
          <Link to="/accounts/login/" className="nav-link">Login</Link>
          <Link to="/accounts/register/" className="btn btn-primary">Get Started</Link>
        </div>
      </nav>

      <div className="hero">
        <h1>Welcome to WebMART Guest WiFi</h1>
        <p>Free premium access to media services while you wait</p>
      </div>

      <div className="cards-grid" style={{ padding: '0 2rem' }}>
        <div className="stat-card">
          <span className="stat-number">📝</span>
          <span className="stat-label">Register Free</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">⏱️</span>
          <span className="stat-label">5 Hours per Token</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">🎬</span>
          <span className="stat-label">Media Access</span>
        </div>
      </div>

      <div className="card" style={{ margin: '2rem' }}>
        <div className="card-header">What's Available</div>
        <div className="card-body">
          <div className="media-grid">
            {services.map(svc => (
              <div key={svc.name} className="media-card">
                <span className="media-icon">{svc.icon}</span>
                <div className="service-name">{svc.name}</div>
                <div style={{ color: '#64748b', fontSize: '0.875rem' }}>{svc.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <Link to="/accounts/register/" className="btn btn-primary" style={{ marginRight: '1rem' }}>
          Register Free
        </Link>
        <Link to="/accounts/login/" className="btn btn-outline">
          Login
        </Link>
        <p style={{ marginTop: '1rem', color: '#64748b' }}>
          Register now and get <strong>5 free tokens</strong> (5 hours each)
        </p>
      </div>

      <footer className="footer">
        📡 WebMART — Guest WiFi Portal
      </footer>
    </div>
  )
}
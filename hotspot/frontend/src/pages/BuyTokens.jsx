import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios from 'axios'

export default function BuyTokens() {
  const [quantity, setQuantity] = useState(1)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const navigate = useNavigate()
  const price = 0.50

  async function handleBuy(e) {
    e.preventDefault()
    setLoading(true)

    try {
      await axios.post('/tokens/buy/', { quantity })
      setSuccess(true)
      setTimeout(() => navigate('/dashboard/'), 1500)
    } catch (err) {
      alert('Purchase failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="app">
        <nav className="navbar">
          <Link to="/dashboard/" className="navbar-brand">📡 WebMART</Link>
        </nav>
        <div className="hero" style={{ margin: '4rem 2rem' }}>
          <h1>Purchase Successful!</h1>
          <p>{quantity} tokens added to your account</p>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <nav className="navbar">
        <Link to="/dashboard/" className="navbar-brand">📡 WebMART</Link>
      </nav>

      <div className="auth-page">
        <div className="auth-card">
          <h2>Buy Tokens</h2>
          
          <form onSubmit={handleBuy}>
            <div className="form-group">
              <label className="form-label">Quantity</label>
              <input
                type="number"
                className="form-input"
                min="1"
                max="100"
                value={quantity}
                onChange={e => setQuantity(parseInt(e.target.value) || 1)}
              />
            </div>
            
            <div className="alert alert-success" style={{ marginBottom: '1rem' }}>
              <strong>Price:</strong> ${price} per token<br />
              <strong>Duration:</strong> 5 hours per token<br />
              <strong>Total:</strong> ${(quantity * price).toFixed(2)}
            </div>
            
            <button type="submit" className="btn btn-primary w-full" disabled={loading}>
              {loading ? 'Processing...' : `Buy ${quantity} Token${quantity > 1 ? 's' : ''}`}
            </button>
          </form>
          
          <Link to="/dashboard/" className="btn btn-outline w-full" style={{ display: 'block', textAlign: 'center', marginTop: '1rem' }}>
            Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}
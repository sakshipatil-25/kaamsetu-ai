import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { API_URL, saveAuth } from './auth'
import './Auth.css'

export default function Login() {
  const [email, setEmail] = useState('employer@demo.com')
  const [password, setPassword] = useState('demo123')
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Login failed')
      }
      const data = await res.json()
      saveAuth(data.token, data.user)
      navigate('/app')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const fillDemo = (role) => {
    setEmail(`${role}@demo.com`)
    setPassword('demo123')
  }

  return (
    <div className="auth-page">
      <div className="auth-left">
        <div className="auth-brand">
          <div className="brand-mark-lg">K</div>
          <h1>KaamSetu AI</h1>
          <p>Distributed Rural Workforce Matching</p>
          <div className="brand-features">
            <div className="brand-feature">Real-time AI matching</div>
            <div className="brand-feature">XGBoost + OR-Tools</div>
            <div className="brand-feature">Adaptive distributed scheduling</div>
          </div>
        </div>
      </div>

      <div className="auth-right">
          <div className="auth-card">
          <Link to="/" style={{ fontSize: '12px', color: '#9a9a9a', display: 'block', marginBottom: '16px', textDecoration: 'none' }}>
            ← Back to home
          </Link>
          <h2>Sign in</h2>
          <p className="auth-subtitle">Welcome back. Sign in to continue.</p>

          <form onSubmit={handleSubmit}>
            <label className="field-label">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />

            <label className="field-label">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />

            {error && <div className="auth-error">{error}</div>}

            <button className="primary-btn" disabled={loading}>
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <div className="demo-hint">
            <div className="demo-label">Quick demo access:</div>
            <div className="demo-buttons">
              <button onClick={() => fillDemo('employer')} type="button">Employer</button>
              <button onClick={() => fillDemo('worker')} type="button">Worker</button>
              <button onClick={() => fillDemo('admin')} type="button">Admin</button>
            </div>
            <div className="demo-note">All demo accounts use password: <code>demo123</code></div>
          </div>

          <p className="auth-footer">
            Don't have an account? <Link to="/signup">Create one</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { API_URL, saveAuth } from './auth'
import './Auth.css'

const ROLES = [
  { value: 'employer', label: 'Employer', desc: 'Post jobs, find workers' },
  { value: 'worker',   label: 'Worker',   desc: 'Find jobs, accept work' },
  { value: 'admin',    label: 'Admin',    desc: 'System oversight' },
]

const WORKER_SKILLS = [
  'farming_seeds', 'farming_pruning', 'farming_weeding',
  'farming_thinning', 'farming_harvesting', 'soil_preparation',
  'plumbing', 'electrical', 'carpentry', 'painting',
  'masonry', 'welding', 'cleaning',
]

export default function Signup() {
  const [form, setForm] = useState({
    email: '', password: '', full_name: '', role: 'employer',
    phone: '', location: '', skill: 'farming_seeds',
  })
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const update = (k, v) => setForm({ ...form, [k]: v })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const payload = { ...form }
      if (payload.role !== 'worker') delete payload.skill
      const res = await fetch(`${API_URL}/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Signup failed')
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
          <h2>Create account</h2>
          <p className="auth-subtitle">Join KaamSetu AI in a few seconds.</p>

          <form onSubmit={handleSubmit}>
            <label className="field-label">I am a…</label>
            <div className="role-grid">
              {ROLES.map(r => (
                <button
                  type="button"
                  key={r.value}
                  className={`role-tile ${form.role === r.value ? 'selected' : ''}`}
                  onClick={() => update('role', r.value)}
                >
                  <strong>{r.label}</strong>
                  <span>{r.desc}</span>
                </button>
              ))}
            </div>

            <label className="field-label">Full name</label>
            <input
              type="text"
              value={form.full_name}
              onChange={(e) => update('full_name', e.target.value)}
              placeholder="Your name"
              required
            />

            <label className="field-label">Email</label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => update('email', e.target.value)}
              placeholder="you@example.com"
              required
            />

            <label className="field-label">Password</label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => update('password', e.target.value)}
              placeholder="At least 6 characters"
              required
              minLength={6}
            />

            <div className="form-row">
              <div>
                <label className="field-label">Phone</label>
                <input
                  type="text"
                  value={form.phone}
                  onChange={(e) => update('phone', e.target.value)}
                  placeholder="Optional"
                />
              </div>
              <div>
                <label className="field-label">Location</label>
                <input
                  type="text"
                  value={form.location}
                  onChange={(e) => update('location', e.target.value)}
                  placeholder="City, State"
                />
              </div>
            </div>

            {form.role === 'worker' && (
              <>
                <label className="field-label">Primary skill</label>
                <select
                  value={form.skill}
                  onChange={(e) => update('skill', e.target.value)}
                >
                  {WORKER_SKILLS.map(s => (
                    <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>
                  ))}
                </select>
              </>
            )}

            {error && <div className="auth-error">{error}</div>}

            <button className="primary-btn" disabled={loading}>
              {loading ? 'Creating account…' : 'Create account'}
            </button>
          </form>

          <p className="auth-footer">
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
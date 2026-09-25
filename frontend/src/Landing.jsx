import { Link, useNavigate } from 'react-router-dom'
import { isLoggedIn } from './auth'
import './Landing.css'

const FEATURES = [
  {
    title: 'AI-Powered Matching',
    desc: 'XGBoost + OR-Tools CP-SAT selects the optimal group of workers based on skill, distance, wage, experience, and rating.',
  },
  {
    title: 'Real-Time Distribution',
    desc: 'Apache Kafka streams job requests across multiple worker nodes with adaptive load balancing.',
  },
  {
    title: 'Wage Estimation',
    desc: 'Predicts market-fair wages based on work type, season, and duration — with automatic fair-wage warnings.',
  },
  {
    title: 'Travel Planning',
    desc: 'Groups workers by proximity into shared vehicles and estimates transportation cost per job.',
  },
  {
    title: 'Multi-Constraint Optimization',
    desc: 'Solves for exactly N workers within budget, maximizing group suitability while respecting gender and distance constraints.',
  },
  {
    title: 'Demand Forecasting',
    desc: 'Analyzes seasonal patterns to predict labour demand for the coming week across skill categories.',
  },
]

const PERSONAS = [
  {
    role: 'Employer',
    desc: 'Post jobs, see AI-matched workers, generate digital work orders, and forecast labour demand.',
    features: ['Post jobs with constraints', 'View AI-matched workers', 'Generate work orders', 'Track posting history'],
  },
  {
    role: 'Worker',
    desc: 'Browse open jobs, accept work, and mark your availability with a single tap.',
    features: ['Find jobs by skill', 'Accept jobs instantly', 'Update availability', 'See your profile'],
  },
  {
    role: 'Admin',
    desc: 'Oversee platform activity, manage users, and monitor system metrics.',
    features: ['System statistics', 'User management', 'Simulation runner', 'Research results'],
  },
]

export default function Landing() {
  const navigate = useNavigate()

  const handleGetStarted = () => {
    if (isLoggedIn()) {
      navigate('/app')
    } else {
      navigate('/login')
    }
  }

  return (
    <div className="landing">
      {/* Header */}
      <header className="landing-header">
        <div className="landing-brand">
          <div className="landing-logo">K</div>
          <div>
            <div className="landing-brand-name">KaamSetu AI</div>
            <div className="landing-brand-tag">Distributed Workforce Matching</div>
          </div>
        </div>
        <div className="landing-actions">
          <Link to="/login" className="landing-link">Sign in</Link>
          <Link to="/signup" className="landing-cta">Get Started</Link>
        </div>
      </header>

      {/* Hero */}
      <section className="landing-hero">
        <div className="hero-content">
          <h1 className="hero-title">
            Intelligent, real-time matching for rural workforce
          </h1>
          <p className="hero-subtitle">
            KaamSetu AI connects employers with skilled rural workers through a
            distributed AI platform. Multi-constraint optimization, adaptive scheduling,
            and real-time processing — all in one place.
          </p>
          <div className="hero-actions">
            <button className="hero-btn-primary" onClick={handleGetStarted}>
              Find Workers →
            </button>
            <Link to="/signup" className="hero-btn-secondary">
              Create Account
            </Link>
          </div>
          <div className="hero-stats">
            <div className="hero-stat">
              <span className="hero-stat-value">1,000</span>
              <span className="hero-stat-label">Workers</span>
            </div>
            <div className="hero-stat">
              <span className="hero-stat-value">92%</span>
              <span className="hero-stat-label">Avg Match</span>
            </div>
            <div className="hero-stat">
              <span className="hero-stat-value">&lt;25ms</span>
              <span className="hero-stat-label">Latency</span>
            </div>
            <div className="hero-stat">
              <span className="hero-stat-value">13</span>
              <span className="hero-stat-label">Skills</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="landing-section">
        <div className="section-head">
          <h2>Built for real rural workforce problems</h2>
          <p>Every feature solves a specific constraint your current hiring process ignores.</p>
        </div>
        <div className="feature-grid">
          {FEATURES.map((f) => (
            <div key={f.title} className="feature-card">
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Personas */}
      <section className="landing-section landing-section-alt">
        <div className="section-head">
          <h2>One platform, three perspectives</h2>
          <p>Each role gets its own purpose-built interface.</p>
        </div>
        <div className="persona-grid">
          {PERSONAS.map((p) => (
            <div key={p.role} className="persona-card">
              <div className="persona-role">{p.role}</div>
              <p className="persona-desc">{p.desc}</p>
              <ul className="persona-features">
                {p.features.map((f) => (
                  <li key={f}>{f}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="landing-cta-section">
        <h2>Try the live demo</h2>
        <p>Use any of these demo accounts — password is <code>demo123</code> for all.</p>
        <div className="demo-accounts">
          <div className="demo-account">employer@demo.com</div>
          <div className="demo-account">worker@demo.com</div>
          <div className="demo-account">admin@demo.com</div>
        </div>
        <button className="hero-btn-primary" onClick={() => navigate('/login')}>
          Sign In Now →
        </button>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
                <div>KaamSetu AI</div>
        <div>XGBoost · OR-Tools · Apache Kafka · Adaptive Scheduling</div>
      </footer>
    </div>
  )
}
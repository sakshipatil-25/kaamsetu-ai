import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getUser, clearAuth, apiFetch, API_URL } from './auth'
import './App.css'

const SKILLS = [
  { value: 'farming_seeds',      label: 'Hand-planting Seeds' },
  { value: 'farming_pruning',    label: 'Pruning Plants' },
  { value: 'farming_weeding',    label: 'Weeding' },
  { value: 'farming_thinning',   label: 'Thinning' },
  { value: 'farming_harvesting', label: 'Hand-harvesting Delicate Crops' },
  { value: 'soil_preparation',   label: 'Soil Preparation' },
  { value: 'plumbing',           label: 'Plumbing' },
  { value: 'electrical',         label: 'Electrical' },
  { value: 'carpentry',          label: 'Carpentry' },
  { value: 'painting',           label: 'Painting' },
  { value: 'masonry',            label: 'Masonry' },
  { value: 'welding',            label: 'Welding' },
  { value: 'cleaning',           label: 'Cleaning' },
]

const SETUP_COLORS = {
  centralized: '#4f46e5',
  static: '#d97706',
  adaptive: '#059669',
}

// ============================================================
// Navigation config per role
// ============================================================
const NAV_CONFIG = {
  employer: [
    { section: 'Employer', items: [
      { id: 'match',    label: 'Match Workers' },
      { id: 'myjobs',   label: 'My Posted Jobs' },
    ]},
    { section: 'Research', items: [
      { id: 'simulate', label: 'Live Simulation' },
      { id: 'compare',  label: 'Research Results' },
    ]},
    { section: 'Documentation', items: [
      { id: 'arch', label: 'Architecture' },
      { id: 'how',  label: 'How It Works' },
    ]},
  ],
  worker: [
    { section: 'Worker', items: [
      { id: 'jobs',     label: 'Available Jobs' },
      { id: 'avail',    label: 'My Availability' },
      { id: 'profile',  label: 'My Profile' },
    ]},
    { section: 'Documentation', items: [
      { id: 'how',  label: 'How It Works' },
    ]},
  ],
  admin: [
    { section: 'Admin', items: [
      { id: 'overview', label: 'System Overview' },
      { id: 'users',    label: 'User Management' },
    ]},
    { section: 'Research', items: [
      { id: 'match',    label: 'Match Workers' },
      { id: 'simulate', label: 'Live Simulation' },
      { id: 'compare',  label: 'Research Results' },
    ]},
    { section: 'Documentation', items: [
      { id: 'arch', label: 'Architecture' },
      { id: 'how',  label: 'How It Works' },
    ]},
  ],
}

const DEFAULT_TAB = {
  employer: 'match',
  worker: 'jobs',
  admin: 'overview',
}


function App() {
  const navigate = useNavigate()
  const user = getUser()
  const role = user?.role || 'employer'

  const handleLogout = () => {
    clearAuth()
    navigate('/login')
  }

  const [tab, setTab] = useState(DEFAULT_TAB[role] || 'match')

  // Employer state
  const [form, setForm] = useState({
    required_skill: 'farming_seeds',
    latitude: 28.6139,
    longitude: 77.2090,
    num_workers_needed: 2,
    budget: 5000,
    duration_hours: 4,
  })
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [simResults, setSimResults] = useState(null)
  const [simLoading, setSimLoading] = useState(false)
  const [history, setHistory] = useState(null)
  const [myJobs, setMyJobs] = useState([])

  // Admin state
  const [adminUsers, setAdminUsers] = useState([])
  const [adminStats, setAdminStats] = useState(null)

  // Worker state
  const [availableJobs, setAvailableJobs] = useState([])
  const [toast, setToast] = useState(null)

  useEffect(() => {
    fetch(`${API_URL}/experiments`)
      .then((r) => r.json())
      .then(setHistory)
      .catch(() => {})
  }, [])

  // Load employer's own jobs on mount
  useEffect(() => {
    if (role === 'employer') {
      loadMyJobs()
    }
  }, [role])

  // Load worker's available jobs when worker views jobs tab
  useEffect(() => {
    if (role === 'worker' && tab === 'jobs') {
      loadAvailableJobs()
    }
  }, [role, tab])

  // Load admin data when admin views those tabs
  useEffect(() => {
    if (role !== 'admin') return
    if (tab === 'users' || tab === 'overview') {
      apiFetch('/admin/users').then(r => r.json()).then(d => setAdminUsers(d.users || [])).catch(() => {})
      apiFetch('/admin/stats').then(r => r.json()).then(setAdminStats).catch(() => {})
    }
  }, [tab, role])

  const submitMatch = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResults(null)
    try {
      const res = await apiFetch('/jobs', {
        method: 'POST',
        body: JSON.stringify(form),
      })
      if (!res.ok) throw new Error(`Server responded with status ${res.status}`)
      const data = await res.json()
      setResults({
        matched_workers: data.matched_workers || [],
        count: (data.matched_workers || []).length,
      })
      loadMyJobs()
    } catch (err) {
      setError(err.message)
    }
    setLoading(false)
  }

  const loadMyJobs = async () => {
    try {
      const res = await apiFetch('/jobs?mine=true')
      if (res.ok) {
        const data = await res.json()
        setMyJobs(data.jobs || [])
      }
    } catch (err) {
      // silent
    }
  }

  const loadAvailableJobs = async () => {
    try {
      const res = await apiFetch('/jobs')
      if (res.ok) {
        const data = await res.json()
        setAvailableJobs(data.jobs || [])
      }
    } catch (err) {
      // silent
    }
  }

    const acceptJob = async (jobId) => {
    try {
      const res = await apiFetch(`/jobs/${jobId}/accept`, { method: 'POST' })
      if (res.ok) {
        await loadAvailableJobs()
        setToast('✓ Job accepted successfully')
        setTimeout(() => setToast(null), 3000)
      } else {
        const err = await res.json()
        setToast(err.detail || 'Failed to accept job')
        setTimeout(() => setToast(null), 3000)
      }
    } catch (err) {
      setToast('Failed to accept job')
      setTimeout(() => setToast(null), 3000)
    }
  }

  const runSimulation = async () => {
    setSimLoading(true)
    setError(null)
    setSimResults(null)
    try {
      const res = await fetch(`${API_URL}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ n_jobs: 50 }),
      })
      if (!res.ok) throw new Error(`Server responded with status ${res.status}`)
      setSimResults(await res.json())
    } catch (err) {
      setError(err.message)
    }
    setSimLoading(false)
  }

  const navGroups = NAV_CONFIG[role] || NAV_CONFIG.employer

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">K</div>
          <div className="brand-text">
            <h1>KaamSetu AI</h1>
            <span>Distributed Workforce Matching</span>
          </div>
        </div>

        <nav className="nav">
          {navGroups.map(group => (
            <div key={group.section}>
              <div className="nav-section">{group.section}</div>
              {group.items.map(item => (
                <a
                  key={item.id}
                  className={`nav-item ${tab === item.id ? 'active' : ''}`}
                  onClick={() => setTab(item.id)}
                >
                  <span className="nav-dot" /> {item.label}
                </a>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          {user && (
            <div className="user-block">
              <div className="user-avatar">
                {user.full_name?.charAt(0)?.toUpperCase() || '?'}
              </div>
              <div className="user-info">
                <div className="user-name">{user.full_name}</div>
                <div className="user-role">{user.role}</div>
              </div>
            </div>
          )}
          <button className="logout-btn" onClick={handleLogout}>
            Sign out
          </button>
        </div>
      </aside>

      <main className="main">
        {/* ============ EMPLOYER / ADMIN: Match ============ */}
        {tab === 'match' && (
          <>
            <header className="page-head">
              <div>
                <h2>Worker Matching</h2>
                <p>Submit a job request and receive AI-matched workers in real time</p>
              </div>
              <div className="stat-pills">
                <div className="pill"><span className="pill-label">Workers</span><span className="pill-value">1,000</span></div>
                <div className="pill"><span className="pill-label">Avg Match</span><span className="pill-value">92%</span></div>
                <div className="pill"><span className="pill-label">Latency</span><span className="pill-value">25 ms</span></div>
              </div>
            </header>

            <div className="grid">
              <section className="card">
                <div className="card-head">
                  <h3>Job Requirements</h3>
                  <span className="badge">New Request</span>
                </div>
                <form onSubmit={submitMatch}>
                  <label className="field-label">Required Skill</label>
                  <div className="skill-grid">
                    {SKILLS.map(s => (
                      <button
                        type="button"
                        key={s.value}
                        className={`skill-tile ${form.required_skill === s.value ? 'selected' : ''}`}
                        onClick={() => setForm({ ...form, required_skill: s.value })}
                      >
                        {s.label}
                      </button>
                    ))}
                  </div>
                  <div className="row">
                    <div className="field">
                      <label className="field-label">Workers Needed</label>
                      <input type="number" min="1" value={form.num_workers_needed}
                        onChange={e => setForm({ ...form, num_workers_needed: +e.target.value })} />
                    </div>
                    <div className="field">
                      <label className="field-label">Budget (₹)</label>
                      <input type="number" min="100" step="100" value={form.budget}
                        onChange={e => setForm({ ...form, budget: +e.target.value })} />
                    </div>
                    <div className="field">
                      <label className="field-label">Duration (hrs)</label>
                      <input type="number" min="1" value={form.duration_hours}
                        onChange={e => setForm({ ...form, duration_hours: +e.target.value })} />
                    </div>
                  </div>
                  <button className="primary-btn" disabled={loading}>
                    {loading ? <><span className="spinner" /> Matching…</> : <>Find Best Workers →</>}
                  </button>
                </form>
              </section>

              <section className="card">
                <div className="card-head">
                  <h3>Matched Workers</h3>
                  {results && <span className="badge success">{results.count} found</span>}
                </div>
                {error && <div className="error"><strong>Error:</strong> {error}</div>}
                {!results && !loading && (
                  <div className="empty">
                    <div className="empty-title">No results yet</div>
                    <p>Submit a job request to view matched workers</p>
                  </div>
                )}
                {loading && (
                  <div className="empty">
                    <div className="spinner large" />
                    <p>Running AI matching…</p>
                  </div>
                )}
                {results && (
                  <ul className="worker-list">
                    {results.matched_workers.map((w, i) => (
                      <li key={w.worker_id} className="worker-item">
                        <div className="worker-rank">{String(i + 1).padStart(2, '0')}</div>
                        <div className="worker-info">
                          <strong>{w.worker_id}</strong>
                          <span>Verified Worker</span>
                        </div>
                        <div className="worker-score">
                          <span className="score-value">{(w.suitability_score * 100).toFixed(1)}%</span>
                          <span className="score-label">match</span>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </section>
            </div>
          </>
        )}

        {/* ============ EMPLOYER: My Jobs ============ */}
        {tab === 'myjobs' && (
          <>
            <header className="page-head">
              <div>
                <h2>My Posted Jobs</h2>
                <p>History of jobs you've posted and their matched workers</p>
              </div>
            </header>
            <div className="card">
              {myJobs.length === 0 ? (
                <div className="empty">
                  <div className="empty-title">No jobs posted yet</div>
                  <p>Go to "Match Workers" to post your first job</p>
                </div>
              ) : (
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Skill</th>
                      <th>Workers</th>
                      <th>Budget</th>
                      <th>Matched</th>
                      <th>Status</th>
                      <th>Posted</th>
                    </tr>
                  </thead>
                  <tbody>
                    {myJobs.map((j) => (
                      <tr key={j.id}>
                        <td>{j.required_skill.replace(/_/g, ' ')}</td>
                        <td>{j.num_workers_needed}</td>
                        <td>₹{j.budget}</td>
                        <td><span className="badge success">{j.matched_count}</span></td>
                        <td>{j.status}</td>
                        <td>{j.created_at}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </>
        )}

        {/* ============ WORKER: Available Jobs ============ */}
                {tab === 'jobs' && (
          <>
            <header className="page-head">
              <div>
                <h2>Available Jobs</h2>
                <p>
                  All open jobs — your skill matches ({user?.skill?.replace(/_/g, ' ') || 'none'}) appear first
                </p>
              </div>
              <button className="primary-btn compact" onClick={loadAvailableJobs}>
                Refresh
              </button>
            </header>
            <div className="card">
              {availableJobs.length === 0 ? (
                <div className="empty">
                  <div className="empty-title">No open jobs yet</div>
                  <p>New jobs will appear here when employers post them</p>
                </div>
              ) : (
                <ul className="job-list">
                  {availableJobs.map((j) => (
                    <li
                      key={j.id}
                      className={`job-item ${j.accepted_by_me ? 'job-accepted' : ''}`}
                    >
                      <div className="job-main">
                        <strong>{j.required_skill.replace(/_/g, ' ')}</strong>
                        <span>Posted by {j.employer_name}</span>
                      </div>
                      <div className="job-meta">
                        <span>{j.num_workers_needed} workers</span>
                        <span>₹{j.budget}</span>
                        <span>{j.duration_hours} hrs</span>
                        {j.accepted_count > 0 && (
                          <span className="accepted-count">
                            {j.accepted_count}/{j.num_workers_needed} accepted
                          </span>
                        )}
                      </div>
                      {j.accepted_by_me ? (
                        <span className="accepted-badge">✓ Accepted</span>
                      ) : (
                        <button
                          className="accept-btn"
                          onClick={() => acceptJob(j.id)}
                          disabled={j.status === 'filled'}
                        >
                          {j.status === 'filled' ? 'Filled' : 'Accept'}
                        </button>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </>
        )}

        {/* ============ WORKER: Availability ============ */}
        {tab === 'avail' && (
          <>
            <header className="page-head">
              <div>
                <h2>My Availability</h2>
                <p>Mark the days you're available to work</p>
              </div>
            </header>
            <div className="card">
              <div className="avail-grid">
                {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].map(day => (
                  <button key={day} className="avail-tile">
                    <span className="avail-day">{day}</span>
                    <span className="avail-status">Available</span>
                  </button>
                ))}
              </div>
            </div>
          </>
        )}

        {/* ============ WORKER: Profile ============ */}
        {tab === 'profile' && (
          <>
            <header className="page-head">
              <div>
                <h2>My Profile</h2>
                <p>Your worker details visible to employers</p>
              </div>
            </header>
            <div className="card">
              <div className="profile-grid">
                <div className="profile-item"><span>Name</span><strong>{user?.full_name}</strong></div>
                <div className="profile-item"><span>Email</span><strong>{user?.email}</strong></div>
                <div className="profile-item"><span>Role</span><strong>{user?.role}</strong></div>
                <div className="profile-item"><span>Phone</span><strong>{user?.phone || '—'}</strong></div>
                <div className="profile-item"><span>Location</span><strong>{user?.location || '—'}</strong></div>
                <div className="profile-item"><span>Primary Skill</span><strong>{user?.skill?.replace(/_/g, ' ') || '—'}</strong></div>
              </div>
            </div>
          </>
        )}

        {/* ============ ADMIN: Overview ============ */}
        {tab === 'overview' && (
          <>
            <header className="page-head">
              <div>
                <h2>System Overview</h2>
                <p>Platform statistics and system health</p>
              </div>
            </header>
            <div className="setup-grid">
              <div className="card">
                <div className="card-head"><h3>Total Users</h3></div>
                <div className="metric">
                  <span className="metric-value">{adminStats?.total_users || 0}</span>
                  <span className="metric-label">Registered accounts</span>
                </div>
              </div>
              <div className="card">
                <div className="card-head"><h3>Employers</h3></div>
                <div className="metric">
                  <span className="metric-value">{adminStats?.employers || 0}</span>
                  <span className="metric-label">Posting jobs</span>
                </div>
              </div>
              <div className="card">
                <div className="card-head"><h3>Workers</h3></div>
                <div className="metric">
                  <span className="metric-value">{adminStats?.workers || 0}</span>
                  <span className="metric-label">Available for work</span>
                </div>
              </div>
            </div>
          </>
        )}

        {/* ============ ADMIN: Users ============ */}
        {tab === 'users' && (
          <>
            <header className="page-head">
              <div>
                <h2>User Management</h2>
                <p>All registered users on the platform</p>
              </div>
            </header>
            <div className="card">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Location</th>
                    <th>Skill</th>
                  </tr>
                </thead>
                <tbody>
                  {adminUsers.map(u => (
                    <tr key={u.id}>
                      <td>{u.id}</td>
                      <td><strong>{u.full_name}</strong></td>
                      <td>{u.email}</td>
                      <td><span className={`role-badge role-${u.role}`}>{u.role}</span></td>
                      <td>{u.location || '—'}</td>
                      <td>{u.skill?.replace(/_/g, ' ') || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}

        {/* ============ SHARED: Simulation ============ */}
        {tab === 'simulate' && (
          <>
            <header className="page-head">
              <div>
                <h2>Live Scheduling Simulation</h2>
                <p>Run all three scheduling strategies side-by-side using the identical AI matcher</p>
              </div>
              <button className="primary-btn compact" onClick={runSimulation} disabled={simLoading}>
                {simLoading ? <><span className="spinner" /> Running…</> : <>Run Simulation →</>}
              </button>
            </header>

            {error && <div className="error"><strong>Error:</strong> {error}</div>}

            {!simResults && !simLoading && (
              <div className="card center-card">
                <div className="empty-title">Ready to simulate</div>
                <p className="center-text">
                  Click <strong>Run Simulation</strong> to process 50 jobs through each scheduling strategy.
                </p>
              </div>
            )}

            {simLoading && (
              <div className="card center-card">
                <div className="spinner large" />
                <div className="empty-title">Running experiments</div>
                <p className="center-text">Processing jobs through all three setups</p>
              </div>
            )}

            {simResults && (
              <div className="setup-grid">
                {['centralized', 'static', 'adaptive'].map(name => {
                  const r = simResults[name]
                  return (
                    <div key={name} className="card setup-card" style={{ borderTop: `3px solid ${SETUP_COLORS[name]}` }}>
                      <div className="card-head">
                        <h3 style={{ textTransform: 'capitalize' }}>{name}</h3>
                        <span className="badge" style={{ background: `${SETUP_COLORS[name]}15`, color: SETUP_COLORS[name] }}>
                          {r.workers.length} {r.workers.length === 1 ? 'node' : 'nodes'}
                        </span>
                      </div>
                      <div className="metric-row">
                        <div className="metric">
                          <span className="metric-label">Avg Latency</span>
                          <span className="metric-value">{r.avg_latency} <small>ms</small></span>
                        </div>
                        <div className="metric">
                          <span className="metric-label">Max Latency</span>
                          <span className="metric-value">{r.max_latency} <small>ms</small></span>
                        </div>
                      </div>
                      <div className="metric-row">
                        <div className="metric">
                          <span className="metric-label">Throughput</span>
                          <span className="metric-value">{r.throughput} <small>jobs/s</small></span>
                        </div>
                        <div className="metric">
                          <span className="metric-label">Imbalance</span>
                          <span className="metric-value">{r.load_imbalance}<small>%</small></span>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </>
        )}

        {/* ============ SHARED: Compare ============ */}
        {tab === 'compare' && history && (
          <>
            <header className="page-head">
              <div>
                <h2>Research Results</h2>
                <p>Aggregated performance data from the distributed Kafka experiments</p>
              </div>
            </header>

            <div className="setup-grid">
              {['centralized', 'static', 'adaptive'].map(name => {
                const r = history[name]
                return (
                  <div key={name} className="card setup-card" style={{ borderTop: `3px solid ${SETUP_COLORS[name]}` }}>
                    <div className="card-head">
                      <h3 style={{ textTransform: 'capitalize' }}>{name}</h3>
                      <span className="badge" style={{ background: `${SETUP_COLORS[name]}15`, color: SETUP_COLORS[name] }}>
                        {r.nodes} {r.nodes === 1 ? 'node' : 'nodes'}
                      </span>
                    </div>
                    <div className="metric-row">
                      <div className="metric">
                        <span className="metric-label">Avg Latency</span>
                        <span className="metric-value">{r.avg_latency} <small>ms</small></span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Max Latency</span>
                        <span className="metric-value">{r.max_latency} <small>ms</small></span>
                      </div>
                    </div>
                    <div className="metric-row">
                      <div className="metric">
                        <span className="metric-label">Avg CPU</span>
                        <span className="metric-value">{r.avg_cpu}<small>%</small></span>
                      </div>
                      <div className="metric">
                        <span className="metric-label">Imbalance</span>
                        <span className="metric-value">{r.load_imbalance}<small>%</small></span>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>

            <div className="card">
              <div className="card-head"><h3>Load Imbalance Comparison</h3></div>
              <div className="chart-bars">
                {['static', 'adaptive'].map(name => {
                  const r = history[name]
                  const pct = (r.load_imbalance / 5) * 100
                  return (
                    <div key={name} className="chart-row">
                      <span className="chart-label">{name}</span>
                      <div className="chart-track">
                        <div className="chart-fill" style={{ width: `${Math.min(pct, 100)}%`, background: SETUP_COLORS[name] }} />
                      </div>
                      <span className="chart-value">{r.load_imbalance}%</span>
                    </div>
                  )
                })}
              </div>
            </div>
          </>
        )}

        {/* ============ SHARED: Architecture ============ */}
        {tab === 'arch' && (
          <>
            <header className="page-head">
              <div>
                <h2>System Architecture</h2>
                <p>Research design: identical AI, varying scheduling strategies</p>
              </div>
            </header>

            <div className="card">
              <div className="card-head"><h3>Research Question</h3></div>
              <p className="research-q">
                Can adaptive distributed workload management improve the performance of real-time
                AI-based rural workforce matching compared with centralized and static distributed processing?
              </p>
            </div>

            <div className="card">
              <div className="card-head"><h3>Frozen Components</h3></div>
              <p className="card-subtitle">These components are identical across all three experimental setups.</p>
              <div className="frozen-grid">
                <div className="frozen-item">
                  <div className="frozen-tag">ML</div>
                  <div>
                    <strong>XGBoost Classifier</strong>
                    <span>Predicts worker-job suitability score (0–1)</span>
                  </div>
                </div>
                <div className="frozen-item">
                  <div className="frozen-tag">OPT</div>
                  <div>
                    <strong>OR-Tools CP-SAT</strong>
                    <span>Selects optimal workers under skill and budget constraints</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-head"><h3>Three Scheduling Strategies</h3></div>
              <div className="arch-grid">
                {[
                  { name: 'Centralized', nodes: 1, sched: 'No distribution — a single worker processes all jobs', color: SETUP_COLORS.centralized },
                  { name: 'Static Distributed', nodes: 3, sched: 'Hash-based Kafka partitioning (job_id mod 3)', color: SETUP_COLORS.static },
                  { name: 'Adaptive Distributed', nodes: 3, sched: 'Weighted scoring: 0.5×CPU + 0.3×queue + 0.2×latency', color: SETUP_COLORS.adaptive },
                ].map(s => (
                  <div key={s.name} className="arch-item" style={{ borderLeft: `3px solid ${s.color}` }}>
                    <div className="arch-head">
                      <strong>{s.name}</strong>
                      <span className="badge" style={{ background: `${s.color}15`, color: s.color }}>
                        {s.nodes} node{s.nodes > 1 ? 's' : ''}
                      </span>
                    </div>
                    <p className="arch-sched">{s.sched}</p>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* ============ SHARED: How It Works ============ */}
        {tab === 'how' && (
          <>
            <header className="page-head">
              <div>
                <h2>How It Works</h2>
                <p>From job submission to matched workers — the complete pipeline</p>
              </div>
            </header>

            <div className="card">
              <div className="card-head"><h3>Real-Time Matching Pipeline</h3></div>
              <div className="flow-steps">
                {[
                  { n: '01', title: 'Employer submits a job request', desc: 'Skill, location, required worker count, budget, and duration are captured through the web form.' },
                  { n: '02', title: 'Event enters the streaming pipeline', desc: 'The request is published as a real-time event to Apache Kafka (3 partitions, parallel processing).' },
                  { n: '03', title: 'AI predicts worker suitability', desc: 'XGBoost scores every candidate (0–1) across six attributes: skill match, distance, wage fit, experience, rating, and transport availability.' },
                  { n: '04', title: 'Optimizer selects the best group', desc: 'OR-Tools CP-SAT solves a constrained optimization: exactly N workers, within budget, maximizing aggregate suitability.' },
                  { n: '05', title: 'Adaptive scheduler routes the work', desc: 'The dispatcher selects the least-loaded node using a weighted score: 0.5×CPU + 0.3×queue + 0.2×latency.' },
                  { n: '06', title: 'Result returned to the employer', desc: 'Matched workers with individual suitability scores arrive typically within 15–25 milliseconds.' },
                ].map(s => (
                  <div key={s.n} className="flow-step">
                    <div className="flow-num">{s.n}</div>
                    <div className="flow-body">
                      <strong>{s.title}</strong>
                      <p>{s.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        <footer className="footer">
          <span>KaamSetu AI — M.Tech Research Prototype</span>
          <span>XGBoost · OR-Tools · Adaptive Distributed Matching</span>
        {toast && (
          <div className="toast">{toast}</div>
        )}
        </footer>
      </main>
    </div>
  )
}

export default App
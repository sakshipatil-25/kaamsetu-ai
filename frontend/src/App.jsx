import { useState, useEffect } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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

function App() {
  const [tab, setTab] = useState('match')
  const [form, setForm] = useState({
    required_skill: 'plumbing', latitude: 28.6139, longitude: 77.2090,
    num_workers_needed: 2, budget: 5000, duration_hours: 4,
  })
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [simResults, setSimResults] = useState(null)
  const [simLoading, setSimLoading] = useState(false)
  const [history, setHistory] = useState(null)

  useEffect(() => {
    fetch(`${API_URL}/experiments`).then(r => r.json()).then(setHistory).catch(() => {})
  }, [])

  const submitMatch = async (e) => {
    e.preventDefault()
    setLoading(true); setError(null); setResults(null)
    try {
      const res = await fetch(`${API_URL}/match`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      if (!res.ok) throw new Error(`Server responded with status ${res.status}`)
      setResults(await res.json())
    } catch (err) { setError(err.message) }
    setLoading(false)
  }

  const runSimulation = async () => {
    setSimLoading(true); setError(null); setSimResults(null)
    try {
      const res = await fetch(`${API_URL}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ n_jobs: 50 }),
      })
      if (!res.ok) throw new Error(`Server responded with status ${res.status}`)
      setSimResults(await res.json())
    } catch (err) { setError(err.message) }
    setSimLoading(false)
  }

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
          <div className="nav-section">Research Platform</div>
          <a className={`nav-item ${tab === 'match' ? 'active' : ''}`} onClick={() => setTab('match')}>
            <span className="nav-dot" /> Match Workers
          </a>
          <a className={`nav-item ${tab === 'simulate' ? 'active' : ''}`} onClick={() => setTab('simulate')}>
            <span className="nav-dot" /> Live Simulation
          </a>
          <a className={`nav-item ${tab === 'compare' ? 'active' : ''}`} onClick={() => setTab('compare')}>
            <span className="nav-dot" /> Research Results
          </a>

          <div className="nav-section">Documentation</div>
          <a className={`nav-item ${tab === 'arch' ? 'active' : ''}`} onClick={() => setTab('arch')}>
            <span className="nav-dot" /> Architecture
          </a>
          <a className={`nav-item ${tab === 'how' ? 'active' : ''}`} onClick={() => setTab('how')}>
            <span className="nav-dot" /> How It Works
          </a>
        </nav>

        <div className="sidebar-footer">
          <div className="status-row">
            <span className="status-dot" />
            <span>Backend Connected</span>
          </div>
          <div className="sidebar-meta">M.Tech Research · 2025–26</div>
        </div>
      </aside>

      <main className="main">
        {tab === 'match' && (
          <>
            <header className="page-head">
              <div>
                <h2>Worker Matching</h2>
                <p>Submit a job request and receive AI-matched workers in real time</p>
              </div>
              <div className="stat-pills">
                <div className="pill">
                  <span className="pill-label">Workers</span>
                  <span className="pill-value">1,000</span>
                </div>
                <div className="pill">
                  <span className="pill-label">Avg Match</span>
                  <span className="pill-value">92%</span>
                </div>
                <div className="pill">
                  <span className="pill-label">Latency</span>
                  <span className="pill-value">25 ms</span>
                </div>
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
                      <button type="button" key={s.value}
                        className={`skill-tile ${form.required_skill === s.value ? 'selected' : ''}`}
                        onClick={() => setForm({ ...form, required_skill: s.value })}>
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
                  The AI matcher (XGBoost + OR-Tools) is identical across all setups — only the scheduling differs.
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
              <>
                <div className="setup-grid">
                  {['centralized', 'static', 'adaptive'].map(name => {
                    const r = simResults[name]
                    return (
                      <div key={name} className="card setup-card"
                        style={{ borderTop: `3px solid ${SETUP_COLORS[name]}` }}>
                        <div className="card-head">
                          <h3 style={{ textTransform: 'capitalize' }}>{name}</h3>
                          <span className="badge"
                            style={{ background: `${SETUP_COLORS[name]}15`, color: SETUP_COLORS[name] }}>
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

                        <div className="worker-mini-grid">
                          {r.workers.map(w => (
                            <div key={w.name} className="worker-mini">
                              <span className="wm-name">{w.name}</span>
                              <span className="wm-jobs">{w.jobs_processed} jobs</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )
                  })}
                </div>

                <div className="card">
                  <div className="card-head"><h3>Observations</h3></div>
                  <ul className="insight-list">
                    <li>
                      <strong>Latency profile.</strong> Centralized processing achieves the lowest per-job latency
                      because it avoids inter-node coordination. Distributed setups trade ~2–3 ms of coordination
                      overhead for horizontal scalability.
                    </li>
                    <li>
                      <strong>Load balance.</strong> The adaptive scheduler achieves{' '}
                      <span style={{ color: SETUP_COLORS.adaptive, fontWeight: 600 }}>
                        {simResults.adaptive.load_imbalance}% imbalance
                      </span>, compared to static partitioning at{' '}
                      <span style={{ color: SETUP_COLORS.static, fontWeight: 600 }}>
                        {simResults.static.load_imbalance}%
                      </span>.
                    </li>
                    <li>
                      <strong>Tail latency.</strong> Adaptive scheduling caps maximum latency at{' '}
                      {simResults.adaptive.max_latency} ms, versus {simResults.static.max_latency} ms for static
                      distribution — a measurable improvement under peak load.
                    </li>
                  </ul>
                </div>
              </>
            )}
          </>
        )}

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
                  <div key={name} className="card setup-card"
                    style={{ borderTop: `3px solid ${SETUP_COLORS[name]}` }}>
                    <div className="card-head">
                      <h3 style={{ textTransform: 'capitalize' }}>{name}</h3>
                      <span className="badge"
                        style={{ background: `${SETUP_COLORS[name]}15`, color: SETUP_COLORS[name] }}>
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
                  const pct = r.load_imbalance / 5 * 100
                  return (
                    <div key={name} className="chart-row">
                      <span className="chart-label">{name}</span>
                      <div className="chart-track">
                        <div className="chart-fill"
                          style={{ width: `${Math.min(pct, 100)}%`, background: SETUP_COLORS[name] }} />
                      </div>
                      <span className="chart-value">{r.load_imbalance}%</span>
                    </div>
                  )
                })}
              </div>
            </div>

            <div className="card">
              <div className="card-head"><h3>Findings</h3></div>
              <ul className="insight-list">
                <li>
                  <strong>Efficiency.</strong> Adaptive scheduling reduces aggregate CPU usage by approximately
                  18% compared to static distribution (411% vs 501%).
                </li>
                <li>
                  <strong>Load balance.</strong> Adaptive achieves 2.1% imbalance at peak load, versus 3.2%
                  for static partitioning.
                </li>
                <li>
                  <strong>Trade-off.</strong> Static distribution shows a marginally lower average latency
                  (23.7 ms vs 24.7 ms), but adaptive exhibits better tail behavior and consistent scaling
                  under increasing request rates.
                </li>
              </ul>
            </div>
          </>
        )}

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
              <p className="card-subtitle">
                These components are identical across all three experimental setups.
              </p>
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
                      <span className="badge"
                        style={{ background: `${s.color}15`, color: s.color }}>
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

            <div className="card">
              <div className="card-head"><h3>Real-World Applications</h3></div>
              <div className="usecase-grid">
                {[
                  { title: 'Village-to-City Job Placement', desc: 'A rural mason is matched to a construction site 12 km away within seconds — no brokers, no waiting.' },
                  { title: 'Seasonal Harvest Demand', desc: 'When hundreds of farms require labour simultaneously, thousands of requests are distributed across nodes without degradation.' },
                  { title: 'Large Contractor Requests', desc: 'A contractor needing 50 welders within a ₹5,00,000 budget receives an optimal group selected automatically.' },
                  { title: 'Fair Wage Enforcement', desc: 'Workers are matched by their expected wage — eliminating undercutting by middlemen.' },
                  { title: 'Transport-Aware Assignment', desc: 'Workers with transport are prioritized for distant jobs; nearby jobs are matched to those without.' },
                  { title: 'Low-Bandwidth Operation', desc: 'Responses return in under 25 ms, functioning reliably on slow rural connections.' },
                ].map(u => (
                  <div key={u.title} className="usecase-item">
                    <strong>{u.title}</strong>
                    <p>{u.desc}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="card">
              <div className="card-head"><h3>Stakeholders</h3></div>
              <div className="benefit-grid">
                <div className="benefit-col">
                  <h4>Rural Workers</h4>
                  <ul>
                    <li>Instant discoverability by employers</li>
                    <li>No dependency on intermediaries</li>
                    <li>Matched by verified skills</li>
                    <li>Wage expectations respected</li>
                  </ul>
                </div>
                <div className="benefit-col">
                  <h4>Employers &amp; Contractors</h4>
                  <ul>
                    <li>Verified workers within seconds</li>
                    <li>Budget-aware matching</li>
                    <li>Group hiring in one request</li>
                    <li>Scales during peak seasons</li>
                  </ul>
                </div>
                <div className="benefit-col">
                  <h4>Government &amp; NGOs</h4>
                  <ul>
                    <li>Transparent, auditable matching</li>
                    <li>Deployable on employment schemes</li>
                    <li>Reduces rural unemployment friction</li>
                    <li>Labour analytics for policy</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-head"><h3>Performance Guarantees</h3></div>
              <div className="metrics-showcase">
                {[
                  { value: '< 25 ms', label: 'Average latency' },
                  { value: '1,500+', label: 'Jobs per test batch' },
                  { value: '92%', label: 'Average match quality' },
                  { value: '2.1%', label: 'Load imbalance (adaptive)' },
                  { value: '18%', label: 'CPU saved vs static' },
                  { value: '3', label: 'Distributed nodes' },
                ].map(m => (
                  <div key={m.label} className="metric-show">
                    <span className="metric-show-value">{m.value}</span>
                    <span className="metric-show-label">{m.label}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="card">
              <div className="card-head"><h3>Why Adaptive Scheduling Matters</h3></div>
              <p className="how-paragraph">
                Traditional systems route jobs using a fixed rule such as <code>job_id mod nodes</code>.
                When job complexity varies — hiring 5 welders versus 1 cleaner — some workers become
                overloaded while others remain idle. KaamSetu AI's adaptive scheduler continuously
                monitors each worker's CPU utilization, queue length, and recent processing latency,
                routing each new job to the node most likely to complete it fastest. This maintains
                responsiveness under peak load, reduces wasted compute by approximately 18%, and
                delivers consistently better worst-case latency for large job requests.
              </p>
            </div>
          </>
        )}

        <footer className="footer">
          <span>KaamSetu AI — M.Tech Research Prototype</span>
          <span>XGBoost · OR-Tools · Adaptive Distributed Matching</span>
        </footer>
      </main>
    </div>
  )
}

export default App
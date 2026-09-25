import { useState, useEffect } from 'react'
import { apiFetch } from './auth'
import './App.css'

export default function DemandForecast() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    apiFetch('/research/forecast')
      .then(r => r.json())
      .then(setData)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="panel-placeholder">Loading forecast…</div>
  }

  if (error) {
    return <div className="error"><strong>Error:</strong> {error}</div>
  }

  if (!data) return null

  return (
    <>
      <header className="page-head">
        <div>
          <h2>Demand Forecast</h2>
          <p>AI-predicted labour demand for the next 7 days</p>
        </div>
      </header>

      <div className="card forecast-summary">
        <div className="summary-grid">
          <div className="summary-item">
            <span className="summary-label">Top Skill</span>
            <span className="summary-value" style={{ textTransform: 'capitalize' }}>
              {data.summary.top_skill}
            </span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Predicted Jobs</span>
            <span className="summary-value">{data.summary.total_predicted_jobs}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Rising Categories</span>
            <span className="summary-value">{data.summary.rising_skills}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Forecast Date</span>
            <span className="summary-value">{data.forecast_date}</span>
          </div>
        </div>
        <div className="insight-banner">
          <strong>Insight:</strong> {data.insight}
        </div>
      </div>

      <div className="card">
        <div className="card-head">
          <h3>Skill-wise Demand Forecast</h3>
          <span className="badge">Next 7 Days</span>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Skill</th>
              <th>Historical Jobs</th>
              <th>Predicted Next Week</th>
              <th>Season Factor</th>
              <th>Trend</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody>
            {data.skills.map(f => (
              <tr key={f.skill}>
                <td style={{ textTransform: 'capitalize' }}>{f.skill_label}</td>
                <td>{f.historical_jobs}</td>
                <td><strong>{f.predicted_next_week}</strong></td>
                <td>×{f.season_factor}</td>
                <td>
                  <span className={`trend-badge trend-${f.trend}`}>
                    {f.trend === 'rising' ? '↑' : f.trend === 'falling' ? '↓' : '—'} {f.trend}
                  </span>
                </td>
                <td>
                  <span className={`conf-badge conf-${f.confidence}`}>{f.confidence}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  )
}
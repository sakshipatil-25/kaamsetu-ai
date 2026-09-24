import { useState, useEffect } from 'react'
import { apiFetch } from './auth'
import './App.css'

export function WagePanel({ skill, numWorkers, durationHours }) {
  const [wage, setWage] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!skill || !numWorkers) return
    setLoading(true)
    apiFetch('/research/wage', {
      method: 'POST',
      body: JSON.stringify({
        required_skill: skill,
        duration_hours: durationHours || 8,
        num_workers: numWorkers,
      }),
    })
      .then(r => r.json())
      .then(setWage)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [skill, numWorkers, durationHours])

  if (loading) return <div className="panel-placeholder">Calculating wage…</div>
  if (!wage) return null

  return (
    <div className="research-panel wage-panel">
      <div className="panel-head">
        <h4>Wage Estimate</h4>
        <span className="badge">AI</span>
      </div>
      <div className="wage-hero">
        <div className="wage-item">
          <span className="wage-label">Per Worker</span>
          <span className="wage-value">₹{wage.per_worker}</span>
        </div>
        <div className="wage-item">
          <span className="wage-label">Total Labour Cost</span>
          <span className="wage-value">₹{wage.total.toLocaleString()}</span>
        </div>
      </div>
      <div className="wage-notes">
        {wage.notes.map((n, i) => (
          <div key={i} className="wage-note">— {n}</div>
        ))}
      </div>
    </div>
  )
}

export function GroupMatchPanel({ skill, numWorkers, budget }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!skill || !numWorkers) return
    setLoading(true)
    apiFetch('/research/group', {
      method: 'POST',
      body: JSON.stringify({
        required_skill: skill,
        num_workers_needed: numWorkers,
        budget: budget || 5000,
        job_latitude: 28.6139,
        job_longitude: 77.2090,
      }),
    })
      .then(r => r.json())
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [skill, numWorkers, budget])

  if (loading) return <div className="panel-placeholder">Running multi-constraint optimizer…</div>
  if (!data) return null

  const p = data.proposed
  const bn = data.baseline_nearest
  const bs = data.baseline_skill

  return (
    <div className="research-panel">
      <div className="panel-head">
        <h4>Strategy Comparison</h4>
        <span className="badge">Research</span>
      </div>

      <div className="compare-table">
        <div className="compare-row compare-head">
          <div>Strategy</div>
          <div>Workers</div>
          <div>Total Wage</div>
          <div>Avg Distance</div>
        </div>

        <div className="compare-row proposed-row">
          <div><strong>Multi-Constraint AI</strong><br/><span className="tag-proposed">Proposed</span></div>
          <div>{p.selected.length}</div>
          <div>₹{p.total_wage.toLocaleString()}</div>
          <div>{p.total_travel > 0 ? `${(p.total_travel / p.selected.length).toFixed(2)} km` : '—'}</div>
        </div>

        <div className="compare-row">
          <div><strong>Nearest Worker</strong><br/><span className="tag-baseline">Baseline 1</span></div>
          <div>{bn.selected.length}</div>
          <div>₹{bn.total_wage.toLocaleString()}</div>
          <div>{bn.avg_distance_km} km</div>
        </div>

        <div className="compare-row">
          <div><strong>Skill-Based</strong><br/><span className="tag-baseline">Baseline 2</span></div>
          <div>{bs.selected.length}</div>
          <div>₹{bs.total_wage.toLocaleString()}</div>
          <div>—</div>
        </div>
      </div>

      {!p.satisfied && (
        <div className="constraint-warning">
          <strong>Constraint:</strong> {p.reason}
        </div>
      )}

      <div className="selected-workers">
        <h5>Proposed Group ({p.selected.length} workers)</h5>
        <div className="selected-grid">
          {p.selected_details.map(w => (
            <div key={w.worker_id} className="selected-chip">
              <div className="chip-id">{w.worker_id}</div>
              <div className="chip-meta">
                <span>{w.gender}</span>
                <span>₹{w.expected_wage}</span>
                <span>{w.distance_km} km</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export function TravelPanel({ skill, numWorkers }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!skill || !numWorkers) return
    setLoading(true)

    // First, get the group match to know who's selected
    apiFetch('/research/group', {
      method: 'POST',
      body: JSON.stringify({
        required_skill: skill,
        num_workers_needed: numWorkers,
        budget: 10000,
        job_latitude: 28.6139,
        job_longitude: 77.2090,
      }),
    })
      .then(r => r.json())
      .then(groupData => {
        const workerIds = groupData.proposed.selected || []
        return apiFetch('/research/travel', {
          method: 'POST',
          body: JSON.stringify({
            job_latitude: 28.6139,
            job_longitude: 77.2090,
            worker_ids: workerIds,
          }),
        }).then(r => r.json())
      })
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [skill, numWorkers])

  if (loading) return <div className="panel-placeholder">Planning travel…</div>
  if (!data) return null

  return (
    <div className="research-panel">
      <div className="panel-head">
        <h4>Travel Plan</h4>
        <span className="badge">Optimization</span>
      </div>

      <div className="travel-hero">
        <div className="travel-item">
          <span className="travel-label">Total Distance</span>
          <span className="travel-value">{data.total_distance_km} km</span>
        </div>
        <div className="travel-item">
          <span className="travel-label">Avg Distance</span>
          <span className="travel-value">{data.avg_distance_km} km</span>
        </div>
        <div className="travel-item">
          <span className="travel-label">Vehicles</span>
          <span className="travel-value">{data.vehicles_needed}</span>
        </div>
        <div className="travel-item">
          <span className="travel-label">Est. Cost</span>
          <span className="travel-value">₹{data.total_cost}</span>
        </div>
      </div>

      <div className="vehicle-groups">
        {data.groups.map(g => (
          <div key={g.vehicle} className="vehicle-card">
            <div className="vehicle-head">
              <strong>Vehicle #{g.vehicle}</strong>
              <span>{g.workers.length} workers · ₹{g.cost}</span>
            </div>
            <div className="vehicle-workers">
              {g.workers.map(w => (
                <span key={w} className="worker-tag">{w}</span>
              ))}
            </div>
            <div className="vehicle-meta">
              Pickup at ({g.pickup_point.lat}, {g.pickup_point.lon}) — {g.distance_to_job_km} km to job
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
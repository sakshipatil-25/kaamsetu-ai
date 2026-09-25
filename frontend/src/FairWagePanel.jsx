import { useState, useEffect } from 'react'
import { apiFetch } from './auth'
import './App.css'

export default function FairWagePanel({ skill, numWorkers, budget, durationHours }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!skill || !numWorkers || !budget) return

    // Debounce so we don't spam the backend while typing
    const timer = setTimeout(() => {
      setLoading(true)
      apiFetch('/research/fair-wage', {
        method: 'POST',
        body: JSON.stringify({
          required_skill: skill,
          num_workers_needed: numWorkers,
          budget: budget,
          duration_hours: durationHours || 8,
        }),
      })
        .then(r => r.json())
        .then(setData)
        .catch(() => {})
        .finally(() => setLoading(false))
    }, 400)

    return () => clearTimeout(timer)
  }, [skill, numWorkers, budget, durationHours])

  if (loading || !data) return null

  if (data.status === 'fair') {
    return (
      <div className="fair-wage fair-wage-ok">
        <div className="fw-head">
          <span className="fw-badge fw-badge-ok">✓ Fair Wage</span>
          <span className="fw-compare">₹{data.offered_per_worker} offered · ₹{data.market_per_worker} market</span>
        </div>
        <p className="fw-message">{data.message}</p>
      </div>
    )
  }

  const isVeryLow = data.status === 'very_low'

  return (
    <div className={`fair-wage ${isVeryLow ? 'fair-wage-red' : 'fair-wage-yellow'}`}>
      <div className="fw-head">
        <span className={`fw-badge ${isVeryLow ? 'fw-badge-red' : 'fw-badge-yellow'}`}>
          {isVeryLow ? '⚠ Very Low Offer' : '⚠ Below Market'}
        </span>
        <span className="fw-compare">
          ₹{data.offered_per_worker} offered · ₹{data.market_per_worker} market
        </span>
      </div>
      <p className="fw-message">{data.message}</p>
      <div className="fw-suggest">
        <strong>Suggested budget:</strong> ₹{data.market_total.toLocaleString()} ({data.ratio < 0.75 ? '75%+ below' : '10%+ below'} market)
      </div>
    </div>
  )
}
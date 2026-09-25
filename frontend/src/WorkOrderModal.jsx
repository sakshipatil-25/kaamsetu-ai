import { useState, useEffect } from 'react'
import { apiFetch } from './auth'
import './App.css'

export default function WorkOrderModal({ jobId, onClose }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    apiFetch('/research/work-order', {
      method: 'POST',
      body: JSON.stringify({ job_id: jobId }),
    })
      .then(r => {
        if (!r.ok) throw new Error(`Failed with status ${r.status}`)
        return r.json()
      })
      .then(setData)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [jobId])

  const handlePrint = () => {
    window.print()
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-head">
          <h3>Digital Work Order</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        {loading && (
          <div className="modal-loading">
            <div className="spinner large" />
            <p>Generating work order…</p>
          </div>
        )}

        {error && (
          <div className="error"><strong>Error:</strong> {error}</div>
        )}

        {data && (
          <div className="work-order">
            {/* Header */}
            <div className="wo-header">
              <div>
                <div className="wo-brand">KaamSetu AI</div>
                <div className="wo-sub">Distributed Workforce Matching</div>
              </div>
              <div className="wo-meta">
                <div className="wo-id">{data.work_order_id}</div>
                <div className="wo-date">{data.generated_at?.split('T')[0]}</div>
              </div>
            </div>

            <div className="wo-section">
              <div className="wo-field">
                <span>Issued To</span>
                <strong>{data.issued_to}</strong>
              </div>
              <div className="wo-field">
                <span>Status</span>
                <strong style={{ textTransform: 'capitalize' }}>{data.job.status}</strong>
              </div>
            </div>

            <div className="wo-section wo-job">
              <div className="wo-field">
                <span>Skill</span>
                <strong style={{ textTransform: 'capitalize' }}>
                  {data.job.skill.replace(/_/g, ' ')}
                </strong>
              </div>
              <div className="wo-field">
                <span>Workers</span>
                <strong>{data.job.num_workers}</strong>
              </div>
              <div className="wo-field">
                <span>Duration</span>
                <strong>{data.job.duration_hours} hrs</strong>
              </div>
              <div className="wo-field">
                <span>Budget</span>
                <strong>₹{data.job.budget.toLocaleString()}</strong>
              </div>
            </div>

            <table className="wo-table">
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Amount</th>
                </tr>
              </thead>
              <tbody>
                {data.line_items.map((item, i) => (
                  <tr key={i}>
                    <td>
                      <strong>{item.label}</strong>
                      <div className="wo-detail">{item.detail}</div>
                    </td>
                    <td className="wo-amount">₹{item.amount.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="wo-total">
              <div className="wo-total-row">
                <span>Subtotal</span>
                <strong>₹{data.subtotal.toLocaleString()}</strong>
              </div>
              <div className="wo-total-row wo-total-final">
                <span>Total</span>
                <strong className={data.within_budget ? 'in-budget' : 'over-budget'}>
                  ₹{data.subtotal.toLocaleString()}
                </strong>
              </div>
              <div className={`wo-budget-note ${data.within_budget ? 'ok' : 'warn'}`}>
                {data.within_budget
                  ? `✓ Within budget (₹${(data.budget - data.subtotal).toLocaleString()} remaining)`
                  : `⚠ Exceeds budget by ₹${(data.subtotal - data.budget).toLocaleString()}`}
              </div>
            </div>

            <div className="wo-notes">
              {data.notes.map((n, i) => (
                <div key={i}>— {n}</div>
              ))}
            </div>

            <div className="wo-actions">
              <button className="wo-btn-secondary" onClick={onClose}>Close</button>
              <button className="wo-btn-primary" onClick={handlePrint}>Print / Save PDF</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
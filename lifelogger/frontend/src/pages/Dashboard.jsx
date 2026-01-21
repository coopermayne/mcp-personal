import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.getStats()
      .then(setStats)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading">Loading...</div>
  if (error) return <div className="error">Error: {error}</div>

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.total_entries}</div>
          <div className="stat-label">Total Entries</div>
        </div>

        <div className="stat-card">
          <div className="stat-value">{stats.total_cards}</div>
          <div className="stat-label">Total Cards</div>
        </div>

        <div className="stat-card highlight">
          <div className="stat-value">{stats.due_today}</div>
          <div className="stat-label">Due Today</div>
          {stats.due_today > 0 && (
            <Link to="/review" className="stat-action">Start Review</Link>
          )}
        </div>

        <div className="stat-card">
          <div className="stat-value">{stats.reviews_this_week}</div>
          <div className="stat-label">Reviews This Week</div>
        </div>
      </div>

      <div className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="action-buttons">
          <Link to="/entries" className="btn btn-primary">Add Entry</Link>
          <Link to="/cards" className="btn btn-secondary">Browse Cards</Link>
          {stats.due_today > 0 && (
            <Link to="/review" className="btn btn-success">
              Review {stats.due_today} Card{stats.due_today !== 1 ? 's' : ''}
            </Link>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard

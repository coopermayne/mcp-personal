import { useState, useEffect } from 'react'
import { api } from '../api/client'

function Entries() {
  const [entries, setEntries] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // New entry form
  const [content, setContent] = useState('')
  const [tags, setTags] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const loadEntries = () => {
    setLoading(true)
    api.getEntries({ limit: 50 })
      .then(data => {
        setEntries(data.entries)
        setTotal(data.total)
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadEntries()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!content.trim()) return

    setSubmitting(true)
    setError(null)

    try {
      const tagList = tags.split(',').map(t => t.trim()).filter(Boolean)
      await api.createEntry({ content: content.trim(), tags: tagList })
      setContent('')
      setTags('')
      loadEntries()
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="entries-page">
      <h1>Knowledge Entries</h1>

      <form className="entry-form" onSubmit={handleSubmit}>
        <h2>Add New Entry</h2>
        <div className="form-group">
          <label htmlFor="content">Content</label>
          <textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Enter your knowledge entry..."
            rows={4}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="tags">Tags (comma-separated)</label>
          <input
            type="text"
            id="tags"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            placeholder="e.g., biology, science, cells"
          />
        </div>
        <button type="submit" className="btn btn-primary" disabled={submitting}>
          {submitting ? 'Adding...' : 'Add Entry'}
        </button>
      </form>

      {error && <div className="error">Error: {error}</div>}

      <div className="entries-list">
        <h2>All Entries ({total})</h2>
        {loading ? (
          <div className="loading">Loading...</div>
        ) : entries.length === 0 ? (
          <p className="empty-state">No entries yet. Add your first entry above!</p>
        ) : (
          <div className="entry-cards">
            {entries.map(entry => (
              <div key={entry.id} className="entry-card">
                <div className="entry-content">{entry.content}</div>
                <div className="entry-meta">
                  <div className="entry-tags">
                    {entry.tags.map(tag => (
                      <span key={tag} className="tag">{tag}</span>
                    ))}
                  </div>
                  <div className="entry-date">{formatDate(entry.created_at)}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Entries

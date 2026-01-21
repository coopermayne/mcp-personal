import { useState, useEffect } from 'react'
import { api } from '../api/client'

function Cards() {
  const [cards, setCards] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('')

  const loadCards = () => {
    setLoading(true)
    const params = { limit: 50 }
    if (filter) params.card_type = filter

    api.getCards(params)
      .then(data => {
        setCards(data.cards)
        setTotal(data.total)
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadCards()
  }, [filter])

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    })
  }

  const isDue = (dueAt) => {
    return new Date(dueAt) <= new Date()
  }

  return (
    <div className="cards-page">
      <h1>Flashcards</h1>

      <div className="cards-toolbar">
        <div className="filter-group">
          <label htmlFor="type-filter">Filter by type:</label>
          <select
            id="type-filter"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="">All types</option>
            <option value="basic">Basic</option>
            <option value="reversible">Reversible</option>
            <option value="cloze">Cloze</option>
          </select>
        </div>
        <div className="cards-count">
          Showing {cards.length} of {total} cards
        </div>
      </div>

      {error && <div className="error">Error: {error}</div>}

      {loading ? (
        <div className="loading">Loading...</div>
      ) : cards.length === 0 ? (
        <p className="empty-state">
          No cards yet. Use Claude with MCP to create flashcards from your entries!
        </p>
      ) : (
        <div className="flashcard-grid">
          {cards.map(card => (
            <div
              key={card.id}
              className={`flashcard ${isDue(card.due_at) ? 'due' : ''}`}
            >
              <div className="flashcard-header">
                <span className={`card-type type-${card.card_type}`}>
                  {card.card_type}
                </span>
                {isDue(card.due_at) && <span className="due-badge">Due</span>}
              </div>

              <div className="flashcard-front">
                <label>Front</label>
                <p>{card.front}</p>
              </div>

              {card.back && (
                <div className="flashcard-back">
                  <label>Back</label>
                  <p>{card.back}</p>
                </div>
              )}

              <div className="flashcard-meta">
                <div className="card-tags">
                  {card.tags.map(tag => (
                    <span key={tag} className="tag">{tag}</span>
                  ))}
                </div>
                <div className="card-stats">
                  <span title="Ease factor">EF: {card.ease_factor.toFixed(2)}</span>
                  <span title="Interval">Int: {card.interval_days}d</span>
                  <span title="Due date">Due: {formatDate(card.due_at)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Cards

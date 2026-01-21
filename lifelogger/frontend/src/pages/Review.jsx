import { useState, useEffect } from 'react'
import { api } from '../api/client'

function Review() {
  const [cards, setCards] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [showAnswer, setShowAnswer] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [sessionStats, setSessionStats] = useState({ reviewed: 0, ratings: { 0: 0, 1: 0, 2: 0, 3: 0 } })
  const [lastResult, setLastResult] = useState(null)

  const loadDueCards = () => {
    setLoading(true)
    api.getDueCards(50)
      .then(data => {
        setCards(data.cards)
        setCurrentIndex(0)
        setShowAnswer(false)
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadDueCards()
  }, [])

  const currentCard = cards[currentIndex]

  const handleReveal = () => {
    setShowAnswer(true)
  }

  const handleRate = async (rating) => {
    if (!currentCard || submitting) return

    setSubmitting(true)
    setError(null)

    try {
      const result = await api.reviewCard(currentCard.id, rating)
      setLastResult(result)

      // Update session stats
      setSessionStats(prev => ({
        reviewed: prev.reviewed + 1,
        ratings: { ...prev.ratings, [rating]: prev.ratings[rating] + 1 }
      }))

      // Move to next card
      if (currentIndex < cards.length - 1) {
        setCurrentIndex(currentIndex + 1)
        setShowAnswer(false)
      } else {
        // Session complete - reload to check for more
        loadDueCards()
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  const ratingButtons = [
    { rating: 0, label: 'Again', desc: 'Forgot completely', color: 'red' },
    { rating: 1, label: 'Hard', desc: 'Barely remembered', color: 'orange' },
    { rating: 2, label: 'Good', desc: 'Remembered with effort', color: 'blue' },
    { rating: 3, label: 'Easy', desc: 'Perfect recall', color: 'green' },
  ]

  if (loading) return <div className="loading">Loading due cards...</div>

  if (error) return (
    <div className="review-page">
      <div className="error">Error: {error}</div>
      <button className="btn btn-primary" onClick={loadDueCards}>Retry</button>
    </div>
  )

  if (cards.length === 0) {
    return (
      <div className="review-page">
        <div className="review-complete">
          <h1>All caught up!</h1>
          {sessionStats.reviewed > 0 ? (
            <div className="session-summary">
              <p>Session complete! You reviewed {sessionStats.reviewed} card{sessionStats.reviewed !== 1 ? 's' : ''}.</p>
              <div className="rating-summary">
                <span className="rating-stat again">{sessionStats.ratings[0]} Again</span>
                <span className="rating-stat hard">{sessionStats.ratings[1]} Hard</span>
                <span className="rating-stat good">{sessionStats.ratings[2]} Good</span>
                <span className="rating-stat easy">{sessionStats.ratings[3]} Easy</span>
              </div>
            </div>
          ) : (
            <p>No cards are due for review right now. Check back later!</p>
          )}
          <button className="btn btn-primary" onClick={loadDueCards}>
            Check for more cards
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="review-page">
      <div className="review-header">
        <h1>Review Session</h1>
        <div className="review-progress">
          Card {currentIndex + 1} of {cards.length}
          {sessionStats.reviewed > 0 && (
            <span className="session-count"> | {sessionStats.reviewed} reviewed</span>
          )}
        </div>
      </div>

      <div className="review-card">
        <div className="card-type-badge">{currentCard.card_type}</div>

        <div className="review-front">
          <h2>{currentCard.front}</h2>
        </div>

        {showAnswer ? (
          <>
            <div className="review-divider" />
            <div className="review-back">
              <p>{currentCard.back || '(No answer - cloze deletion)'}</p>
            </div>

            <div className="rating-buttons">
              {ratingButtons.map(({ rating, label, desc, color }) => (
                <button
                  key={rating}
                  className={`btn-rate btn-${color}`}
                  onClick={() => handleRate(rating)}
                  disabled={submitting}
                >
                  <span className="rate-label">{label}</span>
                  <span className="rate-desc">{desc}</span>
                </button>
              ))}
            </div>

            {lastResult && (
              <div className="last-result">
                {lastResult.message}
              </div>
            )}
          </>
        ) : (
          <button
            className="btn btn-primary btn-reveal"
            onClick={handleReveal}
          >
            Show Answer
          </button>
        )}
      </div>

      {currentCard.tags.length > 0 && (
        <div className="review-tags">
          {currentCard.tags.map(tag => (
            <span key={tag} className="tag">{tag}</span>
          ))}
        </div>
      )}
    </div>
  )
}

export default Review

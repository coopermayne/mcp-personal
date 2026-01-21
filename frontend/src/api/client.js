const API_BASE = '/api'

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`
  const config = {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  }

  const response = await fetch(url, config)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || 'Request failed')
  }

  return response.json()
}

export const api = {
  // Entries
  getEntries: (params = {}) => {
    const query = new URLSearchParams()
    if (params.limit) query.set('limit', params.limit)
    if (params.offset) query.set('offset', params.offset)
    if (params.tags) params.tags.forEach(t => query.append('tags', t))
    const qs = query.toString()
    return request(`/entries${qs ? `?${qs}` : ''}`)
  },

  getEntry: (id) => request(`/entries/${id}`),

  createEntry: (data) => request('/entries', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  // Cards
  getCards: (params = {}) => {
    const query = new URLSearchParams()
    if (params.limit) query.set('limit', params.limit)
    if (params.offset) query.set('offset', params.offset)
    if (params.card_type) query.set('card_type', params.card_type)
    if (params.tags) params.tags.forEach(t => query.append('tags', t))
    const qs = query.toString()
    return request(`/cards${qs ? `?${qs}` : ''}`)
  },

  getDueCards: (limit = 10) => request(`/cards/due?limit=${limit}`),

  reviewCard: (cardId, rating) => request(`/cards/${cardId}/review`, {
    method: 'POST',
    body: JSON.stringify({ rating }),
  }),

  // Stats
  getStats: () => request('/stats'),
}

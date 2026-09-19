const API_BASE_URL = 'http://127.0.0.1:8000'

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`)

  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`)
  }

  return response.json()
}

export function getRecommendations() {
  return request('/api/recommendations')
}

export function getRecommendation(recommendationId) {
  return request(`/api/recommendations/${recommendationId}`)
}

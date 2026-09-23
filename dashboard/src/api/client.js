const API_BASE_URL = 'http://127.0.0.1:8000'

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`)

  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`)
  }

  return response.json()
}

export function getOverview() {
  return request('/api/overview')
}

export function getWorkloads() {
  return request('/api/workloads')
}

export function getCostBenefits() {
  return request('/api/cost-benefit')
}

export function getCompositeIndexes() {
  return request('/api/composite-indexes')
}

export async function getProductionDecisions() {
  return request("/api/decisions");
}

export async function getProductionDecision(recommendationId) {
  return request(`/api/decisions/${recommendationId}`);
}

export async function getQueries() {
  return request("/api/queries");
}

export async function getBenchmarks() {
  return request("/api/benchmarks");
}

export async function getBenchmark(benchmarkId) {
  return request(`/api/benchmarks/${benchmarkId}`);
}

export async function getProvenance() {
  return request('/api/provenance')
}


export async function postOptimizationBlueprint(payload) {
  const response = await fetch(
    `${API_BASE_URL}/api/v2/optimization/studio/blueprint`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    },
  )

  let data = null

  try {
    data = await response.json()
  } catch {
    // Keep the initial null value when the response has no JSON body.
  }

  if (!response.ok) {
    const detail =
      data?.detail?.message ||
      data?.detail ||
      `API request failed with status ${response.status}`

    const error = new Error(
      typeof detail === 'string' ? detail : JSON.stringify(detail),
    )

    error.status = response.status
    error.detail = data?.detail ?? null

    throw error
  }

  return data
}

export async function getProvenanceRecord(recommendationId) {
  return request(`/api/provenance/${recommendationId}`)
}

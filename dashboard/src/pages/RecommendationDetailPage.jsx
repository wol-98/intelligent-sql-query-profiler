import { useEffect, useState } from 'react'

import { getRecommendation } from '../api/recommendations'
import CostEvidence from '../components/recommendations/detail/CostEvidence'
import DecisionEvidence from '../components/recommendations/detail/DecisionEvidence'
import QueryEvidence from '../components/recommendations/detail/QueryEvidence'
import RecommendationIdentity from '../components/recommendations/detail/RecommendationIdentity'
import ValidationEvidence from '../components/recommendations/detail/ValidationEvidence'

function RecommendationDetailPage({
  recommendationId,
  sourcePage,
  onBack,
}) {
  const [recommendation, setRecommendation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const backLabel =
    sourcePage === 'workloads'
      ? '← Back to workloads'
      : '← Back to recommendations'

  useEffect(() => {
    let mounted = true

    async function loadRecommendation() {
      try {
        setLoading(true)
        setError(null)

        const data = await getRecommendation(recommendationId)

        if (mounted) {
          setRecommendation(data)
        }
      } catch (requestError) {
        if (mounted) {
          setError(requestError.message)
        }
      } finally {
        if (mounted) {
          setLoading(false)
        }
      }
    }

    loadRecommendation()

    return () => {
      mounted = false
    }
  }, [recommendationId])

  if (loading) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm text-slate-500">
          Loading recommendation evidence...
        </p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-white p-8 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">
          Unable to load recommendation
        </h3>

        <p className="mt-2 text-sm text-slate-500">
          The recommendation evidence could not be retrieved.
        </p>

        <p className="mt-3 text-xs text-red-600">
          {error}
        </p>

        <button
          type="button"
          onClick={onBack}
          className="mt-5 rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
        >
          {backLabel}
        </button>
      </div>
    )
  }

  if (!recommendation) {
    return null
  }

  return (
    <div className="space-y-6">
      <div>
        <button
          type="button"
          onClick={onBack}
          className="text-sm font-medium text-slate-500 hover:text-slate-900"
        >
          {backLabel}
        </button>

        <div className="mt-4">
          <h3 className="text-lg font-semibold text-slate-900">
            Recommendation Evidence
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Detailed evidence chain for recommendation #
            {recommendation.recommendation_id}.
          </p>
        </div>
      </div>

      <RecommendationIdentity recommendation={recommendation} />

      <QueryEvidence recommendation={recommendation} />

      <ValidationEvidence recommendation={recommendation} />

      <CostEvidence recommendation={recommendation} />

      <DecisionEvidence recommendation={recommendation} />
    </div>
  )
}


export default RecommendationDetailPage

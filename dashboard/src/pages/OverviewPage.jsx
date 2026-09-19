import { useEffect, useState } from 'react'

import { getOverview } from '../api/client'
import EvidenceSummary from '../components/overview/EvidenceSummary'
import MetricCard from '../components/overview/MetricCard'
import PerformanceSummary from '../components/overview/PerformanceSummary'

function OverviewPage() {
  const [overview, setOverview] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true

    async function loadOverview() {
      try {
        setLoading(true)
        setError(null)

        const data = await getOverview()

        if (mounted) {
          setOverview(data)
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

    loadOverview()

    return () => {
      mounted = false
    }
  }, [])

  if (loading) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm text-slate-500">Loading overview...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-white p-8 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">
          Unable to load dashboard data
        </h3>

        <p className="mt-2 text-sm text-slate-500">
          The reporting API could not be reached.
        </p>

        <p className="mt-3 text-xs text-red-600">{error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <section>
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-slate-900">
            Recommendation overview
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Current recommendation and validation activity reported by the
            optimization engine.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
          <MetricCard
            label="Recommendations"
            value={overview.counts.recommendations}
          />

          <MetricCard
            label="Evaluated"
            value={overview.counts.evaluated_recommendations}
          />

          <MetricCard
            label="Benchmarks"
            value={overview.counts.benchmark_evaluations}
          />

          <MetricCard
            label="Successful"
            value={overview.counts.successful_recommendations}
          />

          <MetricCard
            label="Neutral"
            value={overview.counts.neutral_recommendations}
          />

          <MetricCard
            label="Unsuccessful"
            value={overview.counts.unsuccessful_recommendations}
          />
        </div>
      </section>

      <PerformanceSummary performance={overview.performance} />

      <EvidenceSummary evidence={overview.evidence} />
    </div>
  )
}

export default OverviewPage

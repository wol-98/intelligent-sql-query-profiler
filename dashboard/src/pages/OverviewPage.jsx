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
      <div className="dashboard-card p-8">
        <div className="flex items-center gap-3">
          <span className="h-2 w-2 animate-pulse rounded-full bg-blue-500" />

          <p className="text-sm font-medium text-slate-500">
            Loading overview...
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-rose-200 bg-white p-8 shadow-sm">
        <div className="flex items-start gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-rose-50 text-rose-600">
            !
          </div>

          <div>
            <h3 className="text-lg font-bold text-slate-900">
              Unable to load dashboard data
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              The reporting API could not be reached.
            </p>

            <p className="mt-3 rounded-lg bg-rose-50 px-3 py-2 text-xs text-rose-700">
              {error}
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-7">
      <section className="dashboard-page-header mb-0">
        <div className="relative z-10">
          <div className="flex flex-wrap items-start justify-between gap-5">
            <div>
              <div className="mb-2 flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-blue-500 shadow-[0_0_0_4px_rgba(59,130,246,0.10)]" />

                <span className="text-[0.68rem] font-bold uppercase tracking-[0.12em] text-blue-600">
                  Optimization Intelligence
                </span>
              </div>

              <h2 className="text-[1.7rem] font-bold tracking-[-0.03em] text-slate-950">
                Recommendation overview
              </h2>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                Current recommendation and validation activity reported by the
                optimization engine.
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white/80 px-4 py-3 shadow-sm backdrop-blur">
              <p className="text-[0.62rem] font-bold uppercase tracking-[0.1em] text-slate-400">
                Reporting mode
              </p>

              <div className="mt-1 flex items-center gap-2">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />

                <span className="text-xs font-semibold text-slate-700">
                  Read-only
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section>
        <div className="mb-3 flex items-end justify-between gap-4">
          <div>
            <h3 className="dashboard-section-title">
              Recommendation activity
            </h3>

            <p className="dashboard-section-description">
              Current recommendation and validation counts.
            </p>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
          <MetricCard
            label="Recommendations"
            value={overview.counts.recommendations}
            variant="blue"
          />

          <MetricCard
            label="Evaluated"
            value={overview.counts.evaluated_recommendations}
            variant="violet"
          />

          <MetricCard
            label="Benchmarks"
            value={overview.counts.benchmark_evaluations}
            variant="cyan"
          />

          <MetricCard
            label="Successful"
            value={overview.counts.successful_recommendations}
            variant="emerald"
          />

          <MetricCard
            label="Neutral"
            value={overview.counts.neutral_recommendations}
            variant="slate"
          />

          <MetricCard
            label="Unsuccessful"
            value={overview.counts.unsuccessful_recommendations}
            variant="rose"
          />
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[1.55fr_1fr]">
        <PerformanceSummary performance={overview.performance} />

        <EvidenceSummary evidence={overview.evidence} />
      </div>
    </div>
  )
}

export default OverviewPage

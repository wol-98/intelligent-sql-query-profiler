import { useEffect, useState } from 'react'

import { getRecommendation } from '../api/recommendations'
import CostEvidence from '../components/recommendations/detail/CostEvidence'
import DecisionEvidence from '../components/recommendations/detail/DecisionEvidence'
import QueryEvidence from '../components/recommendations/detail/QueryEvidence'
import RecommendationIdentity from '../components/recommendations/detail/RecommendationIdentity'
import ValidationEvidence from '../components/recommendations/detail/ValidationEvidence'
import BenchmarkEvidence from '../components/recommendations/detail/BenchmarkEvidence'

function EvidenceStage({ number, label, children, last = false }) {
  return (
    <div className="relative lg:pl-16">
      <div className="hidden lg:flex absolute left-0 top-0 bottom-0 w-12 flex-col items-center">
        <div className="relative z-10 flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-blue-200 bg-white text-xs font-bold text-blue-600 shadow-sm">
          {number}
        </div>

        {!last && (
          <div className="mt-2 w-px flex-1 bg-gradient-to-b from-blue-200 via-slate-200 to-slate-200" />
        )}
      </div>

      <div className="mb-2 flex items-center gap-2 lg:hidden">
        <span className="flex h-7 w-7 items-center justify-center rounded-full bg-blue-50 text-[0.65rem] font-bold text-blue-600">
          {number}
        </span>

        <span className="text-[0.65rem] font-bold uppercase tracking-[0.1em] text-slate-400">
          {label}
        </span>
      </div>

      {children}
    </div>
  )
}

function RecommendationDetailPage({
  recommendationId,
  sourcePage,
  onBack,
  onViewBenchmark,
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
      <div className="dashboard-card p-8">
        <div className="flex items-center gap-3">
          <span className="h-2 w-2 animate-pulse rounded-full bg-blue-500" />

          <div>
            <p className="text-[0.65rem] font-bold uppercase tracking-[0.1em] text-blue-600">
              Recommendation intelligence
            </p>

            <p className="mt-1 text-sm font-medium text-slate-500">
              Loading recommendation evidence...
            </p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-rose-200 bg-white p-8 shadow-sm">
        <div className="flex items-start gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-rose-50 font-bold text-rose-600">
            !
          </div>

          <div className="min-w-0">
            <p className="text-[0.65rem] font-bold uppercase tracking-[0.1em] text-rose-600">
              Recommendation intelligence
            </p>

            <h3 className="mt-1 text-lg font-bold text-slate-950">
              Unable to load recommendation
            </h3>

            <p className="mt-1 text-sm leading-6 text-slate-500">
              The recommendation evidence could not be retrieved.
            </p>

            <p className="mt-3 rounded-lg bg-rose-50 px-3 py-2 text-xs text-rose-700">
              {error}
            </p>

            <button
              type="button"
              onClick={onBack}
              className="dashboard-focus mt-5 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-xs font-bold text-slate-600 transition hover:border-slate-300 hover:bg-slate-50 hover:text-slate-900"
            >
              {backLabel}
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (!recommendation) {
    return null
  }

  return (
    <div className="space-y-6">
      <section className="dashboard-page-header mb-0">
        <div className="relative z-10">
          <button
            type="button"
            onClick={onBack}
            className="dashboard-focus inline-flex items-center rounded-lg text-xs font-bold text-slate-500 transition hover:text-blue-600"
          >
            {backLabel}
          </button>

          <div className="mt-5 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <div className="mb-2 flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-blue-500 shadow-[0_0_0_4px_rgba(59,130,246,0.10)]" />

                <span className="text-[0.68rem] font-bold uppercase tracking-[0.12em] text-blue-600">
                  Evidence-driven analysis
                </span>
              </div>

              <h1 className="text-[1.7rem] font-bold tracking-[-0.03em] text-slate-950">
                Recommendation Evidence
              </h1>

              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
                Detailed evidence chain for recommendation #
                {recommendation.recommendation_id}.
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white/85 px-4 py-3 shadow-sm backdrop-blur">
              <p className="text-[0.62rem] font-bold uppercase tracking-[0.1em] text-slate-400">
                Evidence stages
              </p>

              <p className="mt-1 text-xl font-bold tracking-tight text-slate-900">
                06
              </p>

              <p className="text-[0.68rem] text-slate-400">
                traceable stages
              </p>
            </div>
          </div>
        </div>
      </section>

      <RecommendationIdentity recommendation={recommendation} />

      <section className="rounded-2xl border border-slate-200 bg-white/60 p-4 shadow-sm lg:p-5">
        <div className="mb-5 hidden items-center justify-between gap-4 lg:flex">
          <div>
            <p className="text-[0.65rem] font-bold uppercase tracking-[0.1em] text-slate-400">
              Evidence progression
            </p>

            <p className="mt-1 text-xs text-slate-500">
              From query context through validation, cost, decision, and
              traceability.
            </p>
          </div>

          <div className="flex items-center gap-2 text-[0.62rem] font-semibold text-slate-400">
            <span className="h-2 w-2 rounded-full bg-blue-500" />
            <span>Evidence trail</span>
          </div>
        </div>

        <div className="space-y-6">
          <EvidenceStage number="01" label="Query context">
            <QueryEvidence recommendation={recommendation} />
          </EvidenceStage>

          <EvidenceStage number="02" label="Experimental validation">
            <ValidationEvidence recommendation={recommendation} />
          </EvidenceStage>

          <EvidenceStage number="03" label="Stored benchmark evidence">
            <BenchmarkEvidence
              recommendation={recommendation}
              onViewBenchmark={onViewBenchmark}
            />
          </EvidenceStage>

          <EvidenceStage number="04" label="Cost & benefit">
            <CostEvidence recommendation={recommendation} />
          </EvidenceStage>

          <EvidenceStage number="05" label="Production framework" last>
            <DecisionEvidence recommendation={recommendation} />
          </EvidenceStage>
        </div>
      </section>
    </div>
  )
}

export default RecommendationDetailPage

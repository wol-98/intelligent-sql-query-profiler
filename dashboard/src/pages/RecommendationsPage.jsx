import { useEffect, useMemo, useState } from 'react'

import { getRecommendations } from '../api/recommendations'
import RecommendationFilters from '../components/recommendations/RecommendationFilters'
import RecommendationTable from '../components/recommendations/RecommendationTable'

function RecommendationsPage({ onSelectRecommendation }) {
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [search, setSearch] = useState('')
  const [priority, setPriority] = useState('ALL')
  const [decision, setDecision] = useState('ALL')
  const [evidence, setEvidence] = useState('ALL')
  const [validation, setValidation] = useState('ALL')

  useEffect(() => {
    let mounted = true

    async function loadRecommendations() {
      try {
        setLoading(true)
        setError(null)

        const data = await getRecommendations()

        if (mounted) {
          setRecommendations(data)
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

    loadRecommendations()

    return () => {
      mounted = false
    }
  }, [])

  const filteredRecommendations = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase()

    return recommendations.filter((recommendation) => {
      const searchableText = [
        recommendation.recommendation_id,
        recommendation.table_name,
        recommendation.index_name,
        recommendation.reason,
        ...recommendation.columns,
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()

      const matchesSearch =
        normalizedSearch.length === 0 ||
        searchableText.includes(normalizedSearch)

      const matchesPriority =
        priority === 'ALL' || recommendation.priority === priority

      const matchesDecision =
        decision === 'ALL' || recommendation.decision.state === decision

      const matchesEvidence =
        evidence === 'ALL' ||
        recommendation.provenance.evidence_status === evidence

      const matchesValidation =
        validation === 'ALL' ||
        recommendation.validation.outcome === validation

      return (
        matchesSearch &&
        matchesPriority &&
        matchesDecision &&
        matchesEvidence &&
        matchesValidation
      )
    })
  }, [
    recommendations,
    search,
    priority,
    decision,
    evidence,
    validation,
  ])

  function clearFilters() {
    setSearch('')
    setPriority('ALL')
    setDecision('ALL')
    setEvidence('ALL')
    setValidation('ALL')
  }

  const activeFilterCount = [
    search.trim().length > 0,
    priority !== 'ALL',
    decision !== 'ALL',
    evidence !== 'ALL',
    validation !== 'ALL',
  ].filter(Boolean).length

  if (loading) {
    return (
      <div className="dashboard-card p-8">
        <div className="flex items-center gap-3">
          <span className="h-2 w-2 animate-pulse rounded-full bg-blue-500" />

          <p className="text-sm font-medium text-slate-500">
            Loading recommendations...
          </p>
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

          <div>
            <h3 className="text-lg font-bold text-slate-900">
              Unable to load recommendations
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
    <div className="space-y-6">
      <section className="dashboard-page-header mb-0">
        <div className="relative z-10">
          <div className="flex flex-wrap items-start justify-between gap-5">
            <div>
              <div className="mb-2 flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-violet-500 shadow-[0_0_0_4px_rgba(139,92,246,0.10)]" />

                <span className="text-[0.68rem] font-bold uppercase tracking-[0.12em] text-violet-600">
                  Recommendation Intelligence
                </span>
              </div>

              <h2 className="text-[1.7rem] font-bold tracking-[-0.03em] text-slate-950">
                Recommendation Explorer
              </h2>

              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
                Explore index recommendations, validation outcomes, production
                decisions, and evidence coverage.
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white/85 px-4 py-3 shadow-sm backdrop-blur">
              <p className="text-[0.62rem] font-bold uppercase tracking-[0.1em] text-slate-400">
                Inventory
              </p>

              <p className="mt-1 text-xl font-bold tracking-tight text-slate-900">
                {recommendations.length}
              </p>

              <p className="text-[0.68rem] text-slate-400">
                recommendations available
              </p>
            </div>
          </div>
        </div>
      </section>

      <RecommendationFilters
        search={search}
        onSearchChange={setSearch}
        priority={priority}
        onPriorityChange={setPriority}
        decision={decision}
        onDecisionChange={setDecision}
        evidence={evidence}
        onEvidenceChange={setEvidence}
        validation={validation}
        onValidationChange={setValidation}
        onClear={clearFilters}
        activeFilterCount={activeFilterCount}
      />

      <section>
        <div className="mb-3 flex flex-wrap items-end justify-between gap-3">
          <div>
            <h3 className="dashboard-section-title">
              Recommendation inventory
            </h3>

            <p className="dashboard-section-description">
              Select a recommendation to inspect its complete evidence chain.
            </p>
          </div>

          <div className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-[0.68rem] font-semibold text-slate-600 shadow-sm">
            Showing {filteredRecommendations.length} of {recommendations.length}
          </div>
        </div>

        <RecommendationTable
          recommendations={filteredRecommendations}
          onSelect={onSelectRecommendation}
        />
      </section>
    </div>
  )
}

export default RecommendationsPage

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

  if (loading) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm text-slate-500">
          Loading recommendations...
        </p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-white p-8 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">
          Unable to load recommendations
        </h3>

        <p className="mt-2 text-sm text-slate-500">
          The reporting API could not be reached.
        </p>

        <p className="mt-3 text-xs text-red-600">{error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <section>
        <h3 className="text-lg font-semibold text-slate-900">
          Recommendation Explorer
        </h3>

        <p className="mt-1 text-sm text-slate-500">
          Explore index recommendations, validation outcomes, production
          decisions, and evidence coverage.
        </p>
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
      />

      <RecommendationTable
        recommendations={filteredRecommendations}
        onSelect={onSelectRecommendation}
      />
    </div>
  )
}

export default RecommendationsPage

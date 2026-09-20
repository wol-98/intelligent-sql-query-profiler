import { useEffect, useState } from 'react'

import { getWorkloads } from '../../../api/client'
import EvidenceField from './EvidenceField'
import EvidenceSection from './EvidenceSection'

function formatPercent(value) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return `${Number(value).toFixed(2)}%`
}

function QueryEvidence({ recommendation }) {
  const { query, workload, validation } = recommendation

  const [linkedWorkload, setLinkedWorkload] = useState(null)
  const [workloadLoading, setWorkloadLoading] = useState(true)

  useEffect(() => {
    let mounted = true

    async function loadWorkload() {
      try {
        setWorkloadLoading(true)

        const workloads = await getWorkloads()

        const matchedWorkload = workloads.find((item) =>
          item.recommendation_ids.includes(
            recommendation.recommendation_id,
          ),
        )

        if (mounted) {
          setLinkedWorkload(matchedWorkload ?? null)
        }
      } catch {
        if (mounted) {
          setLinkedWorkload(null)
        }
      } finally {
        if (mounted) {
          setWorkloadLoading(false)
        }
      }
    }

    loadWorkload()

    return () => {
      mounted = false
    }
  }, [recommendation.recommendation_id])

  const displayWorkload = linkedWorkload ?? workload

  function workloadValue(value) {
    if (workloadLoading) {
      return 'Loading...'
    }

    if (value === null || value === undefined) {
      return 'Not available'
    }

    return value
  }

  return (
    <EvidenceSection
      eyebrow="01 · Query context"
      title="Query & workload"
      description="The workload context associated with this recommendation."
      accent="blue"
    >
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <EvidenceField
          label="Query type"
          value={query.query_type}
        />

        <EvidenceField
          label="Workload priority"
          value={workloadValue(displayWorkload?.priority)}
        />

        <EvidenceField
          label="Execution count"
          value={workloadValue(displayWorkload?.execution_count)}
        />

        <EvidenceField
          label="Time share"
          value={
            workloadLoading
              ? 'Loading...'
              : formatPercent(displayWorkload?.time_share)
          }
          emphasize
        />

        <EvidenceField
          label="Frequency share"
          value={
            workloadLoading
              ? 'Loading...'
              : formatPercent(displayWorkload?.frequency_share)
          }
        />

        <EvidenceField
          label="Fingerprint"
          value={query.fingerprint}
          mono
        />
      </div>

      <div className="mt-4 rounded-xl border border-slate-200 bg-slate-950 p-4">
        <div className="mb-2 flex items-center justify-between gap-3">
          <p className="text-[0.62rem] font-bold uppercase tracking-[0.08em] text-slate-400">
            Query template
          </p>

          <span className="rounded-md bg-white/10 px-2 py-1 text-[0.6rem] font-semibold text-slate-400">
            NORMALIZED
          </span>
        </div>

        <pre className="overflow-x-auto text-xs leading-6 text-slate-100">
          {query.template || 'Not available'}
        </pre>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <EvidenceField
          label="Validation outcome"
          value={validation.outcome}
        />

        <EvidenceField
          label="Rows preserved"
          value={
            validation.rows_preserved === null ||
            validation.rows_preserved === undefined
              ? 'Not available'
              : validation.rows_preserved
                ? 'Yes'
                : 'No'
          }
        />

        <EvidenceField
          label="Index used"
          value={
            validation.index_used === null ||
            validation.index_used === undefined
              ? 'Not available'
              : validation.index_used
                ? 'Yes'
                : 'No'
          }
        />
      </div>
    </EvidenceSection>
  )
}

export default QueryEvidence

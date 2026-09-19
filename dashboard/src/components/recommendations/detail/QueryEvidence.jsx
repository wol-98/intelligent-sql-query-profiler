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
      title="Query & workload"
      description="The workload context associated with this recommendation."
    >
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
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

      <div className="mt-6">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
          Query template
        </p>

        <pre className="mt-2 overflow-x-auto rounded-lg bg-slate-900 p-4 text-xs leading-6 text-slate-100">
          {query.template || 'Not available'}
        </pre>
      </div>

      <div className="mt-5 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
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

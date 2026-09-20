import { useEffect, useMemo, useState } from 'react'

import { getProvenance } from '../api/client'
import StatusBadge from '../components/common/StatusBadge'
import ProvenanceDetail from '../components/provenance/ProvenanceDetail'

function SummaryCard({ label, value, description }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-2xl font-semibold text-slate-900">
        {value}
      </p>

      {description && (
        <p className="mt-1 text-xs text-slate-500">
          {description}
        </p>
      )}
    </div>
  )
}

function ProvenanceTable({
  records,
  selectedRecommendationId,
  onSelect,
}) {
  if (records.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-10 text-center shadow-sm">
        <h3 className="text-base font-semibold text-slate-900">
          No provenance records found
        </h3>

        <p className="mt-2 text-sm text-slate-500">
          Try changing the current filters.
        </p>
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-[1050px] w-full border-collapse text-left">
          <thead className="bg-slate-50">
            <tr className="border-b border-slate-200">
              <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Recommendation
              </th>

              <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Index
              </th>

              <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Experiment
              </th>

              <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Provenance
              </th>

              <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Evidence
              </th>
            </tr>
          </thead>

          <tbody>
            {records.map((record) => {
              const selected =
                record.recommendation_id === selectedRecommendationId

              return (
                <tr
                  key={record.recommendation_id}
                  onClick={() => onSelect(record)}
                  className={`cursor-pointer border-b border-slate-100 last:border-b-0 ${
                    selected
                      ? 'bg-slate-50'
                      : 'hover:bg-slate-50'
                  }`}
                >
                  <td className="px-5 py-4">
                    <span className="font-mono text-sm font-semibold text-slate-700">
                      #{record.recommendation_id}
                    </span>
                  </td>

                  <td className="px-5 py-4">
                    <span className="font-mono text-xs text-slate-600">
                      {record.index_name || 'Not available'}
                    </span>
                  </td>

                  <td className="px-5 py-4">
                    <span className="font-mono text-xs text-slate-600">
                      {record.linked_experiment_id || 'Not available'}
                    </span>
                  </td>

                  <td className="px-5 py-4">
                    <StatusBadge value={record.status} />
                  </td>

                  <td className="px-5 py-4">
                    <StatusBadge value={record.evidence_status} />
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <div className="border-t border-slate-200 bg-slate-50 px-5 py-3">
        <p className="text-xs text-slate-500">
          Showing {records.length} provenance record
          {records.length === 1 ? '' : 's'}.
        </p>
      </div>
    </div>
  )
}

function EvidenceProvenancePage() {
  const [records, setRecords] = useState([])
  const [selectedRecommendationId, setSelectedRecommendationId] =
    useState(null)

  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('ALL')
  const [evidenceStatus, setEvidenceStatus] = useState('ALL')

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true

    async function loadProvenance() {
      try {
        setLoading(true)
        setError(null)

        const data = await getProvenance()

        if (mounted) {
          setRecords(data)

          if (data.length > 0) {
            setSelectedRecommendationId(
              data[0].recommendation_id,
            )
          }
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

    loadProvenance()

    return () => {
      mounted = false
    }
  }, [])

  const statuses = useMemo(() => {
    return [
      'ALL',
      ...Array.from(
        new Set(
          records
            .map((record) => record.status)
            .filter(Boolean),
        ),
      ).sort(),
    ]
  }, [records])

  const evidenceStatuses = useMemo(() => {
    return [
      'ALL',
      ...Array.from(
        new Set(
          records
            .map((record) => record.evidence_status)
            .filter(Boolean),
        ),
      ).sort(),
    ]
  }, [records])

  const filteredRecords = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase()

    return records.filter((record) => {
      const matchesStatus =
        status === 'ALL' || record.status === status

      const matchesEvidence =
        evidenceStatus === 'ALL' ||
        record.evidence_status === evidenceStatus

      const searchable = [
        record.recommendation_id,
        record.query_fingerprint,
        record.index_name,
        record.linked_experiment_id,
        record.status,
        record.evidence_status,
      ]
        .filter(
          (value) =>
            value !== null &&
            value !== undefined,
        )
        .join(' ')
        .toLowerCase()

      const matchesSearch =
        normalizedSearch.length === 0 ||
        searchable.includes(normalizedSearch)

      return (
        matchesStatus &&
        matchesEvidence &&
        matchesSearch
      )
    })
  }, [
    records,
    search,
    status,
    evidenceStatus,
  ])

  const selectedRecord = useMemo(() => {
    return (
      records.find(
        (record) =>
          record.recommendation_id ===
          selectedRecommendationId,
      ) || null
    )
  }, [records, selectedRecommendationId])

  const summary = useMemo(() => {
    const linked = records.filter(
      (record) => record.status === 'LINKED',
    ).length

    const notEstablished = records.filter(
      (record) => record.status === 'NOT_ESTABLISHED',
    ).length

    const complete = records.filter(
      (record) => record.evidence_status === 'COMPLETE',
    ).length

    const insufficient = records.filter(
      (record) => record.evidence_status === 'INSUFFICIENT',
    ).length

    const partial = records.filter(
      (record) => record.evidence_status === 'PARTIAL',
    ).length

    return {
      total: records.length,
      linked,
      notEstablished,
      complete,
      partial,
      insufficient,
    }
  }, [records])

  if (loading) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm text-slate-500">
          Loading evidence and provenance...
        </p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-white p-8 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">
          Unable to load evidence and provenance
        </h3>

        <p className="mt-2 text-sm text-slate-500">
          The reporting API could not be reached.
        </p>

        <p className="mt-3 text-xs text-red-600">
          {error}
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <section>
        <h3 className="text-lg font-semibold text-slate-900">
          Evidence &amp; Provenance
        </h3>

        <p className="mt-1 text-sm text-slate-500">
          Trace recommendation evidence back to its explicitly
          established experimental provenance.
        </p>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <SummaryCard
          label="Total Records"
          value={summary.total}
          description="Recommendation provenance records"
        />

        <SummaryCard
          label="Linked"
          value={summary.linked}
          description="Explicit provenance established"
        />

        <SummaryCard
          label="Not Established"
          value={summary.notEstablished}
          description="No explicit experimental linkage"
        />

        <SummaryCard
          label="Complete"
          value={summary.complete}
          description="Evidence status COMPLETE"
        />

        <SummaryCard
          label="Insufficient"
          value={summary.insufficient}
          description="Evidence status INSUFFICIENT"
        />
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row">
          <div className="flex-1">
            <label
              htmlFor="provenance-search"
              className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500"
            >
              Search
            </label>

            <input
              id="provenance-search"
              type="text"
              value={search}
              onChange={(event) =>
                setSearch(event.target.value)
              }
              placeholder="Search recommendation, fingerprint, index, or experiment..."
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-500 focus:ring-1 focus:ring-slate-500"
            />
          </div>

          <div className="lg:w-52">
            <label
              htmlFor="provenance-status"
              className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500"
            >
              Provenance
            </label>

            <select
              id="provenance-status"
              value={status}
              onChange={(event) =>
                setStatus(event.target.value)
              }
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-500 focus:ring-1 focus:ring-slate-500"
            >
              {statuses.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </div>

          <div className="lg:w-52">
            <label
              htmlFor="provenance-evidence"
              className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500"
            >
              Evidence
            </label>

            <select
              id="provenance-evidence"
              value={evidenceStatus}
              onChange={(event) =>
                setEvidenceStatus(event.target.value)
              }
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-500 focus:ring-1 focus:ring-slate-500"
            >
              {evidenceStatuses.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </div>
        </div>
      </section>

      <ProvenanceTable
        records={filteredRecords}
        selectedRecommendationId={
          selectedRecommendationId
        }
        onSelect={(record) =>
          setSelectedRecommendationId(
            record.recommendation_id,
          )
        }
      />

      <ProvenanceDetail provenance={selectedRecord} />
    </div>
  )
}

export default EvidenceProvenancePage

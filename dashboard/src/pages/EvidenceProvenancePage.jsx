import { useEffect, useMemo, useState } from 'react'

import { getProvenance } from '../api/client'
import StatusBadge from '../components/common/StatusBadge'
import ProvenanceDetail from '../components/provenance/ProvenanceDetail'

function SectionLabel({ children, tone = 'blue' }) {
  const tones = {
    blue: 'bg-blue-500',
    cyan: 'bg-cyan-500',
    violet: 'bg-violet-500',
    emerald: 'bg-emerald-500',
    amber: 'bg-amber-500',
  }

  return (
    <div className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">
      <span className={`h-2 w-2 rounded-full ${tones[tone] || tones.blue}`} />
      {children}
    </div>
  )
}

function SummaryCard({ label, value, description, tone = 'blue' }) {
  const accents = {
    blue: 'border-blue-200',
    cyan: 'border-cyan-200',
    violet: 'border-violet-200',
    emerald: 'border-emerald-200',
    slate: 'border-slate-200',
  }

  const dots = {
    blue: 'bg-blue-500',
    cyan: 'bg-cyan-500',
    violet: 'bg-violet-500',
    emerald: 'bg-emerald-500',
    slate: 'bg-slate-400',
  }

  return (
    <div
      className={`relative overflow-hidden rounded-2xl border bg-white p-5 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:shadow-md ${
        accents[tone] || accents.blue
      }`}
    >
      <span
        className={`absolute right-4 top-4 h-2 w-2 rounded-full ${
          dots[tone] || dots.blue
        }`}
      />

      <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">
        {label}
      </p>

      <p className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">
        {value}
      </p>

      <p className="mt-1 text-xs leading-5 text-slate-400">
        {description}
      </p>
    </div>
  )
}

function DistributionCard({
  label,
  value,
  total,
  description,
  tone = 'blue',
}) {
  const colors = {
    blue: 'bg-blue-500',
    cyan: 'bg-cyan-500',
    violet: 'bg-violet-500',
    emerald: 'bg-emerald-500',
    slate: 'bg-slate-400',
  }

  const percentage = total > 0 ? (value / total) * 100 : 0

  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <span
            className={`h-2 w-2 rounded-full ${
              colors[tone] || colors.blue
            }`}
          />
          <span className="text-sm font-semibold text-slate-800">
            {label}
          </span>
        </div>

        <span className="text-sm font-semibold text-slate-900">
          {value}
        </span>
      </div>

      <div className="mt-3 h-2 overflow-hidden rounded-full bg-white">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            colors[tone] || colors.blue
          }`}
          style={{ width: `${Math.max(percentage, value > 0 ? 2 : 0)}%` }}
        />
      </div>

      <p className="mt-2 text-[11px] text-slate-400">
        {description}
      </p>
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
      <div className="rounded-2xl border border-slate-200 bg-white p-12 text-center shadow-sm">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-slate-100 text-slate-400">
          —
        </div>

        <h3 className="mt-4 text-base font-semibold text-slate-900">
          No provenance records found
        </h3>

        <p className="mt-2 text-sm text-slate-500">
          Try changing the current filters or search terms.
        </p>
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-cyan-500">
            Evidence register
          </p>

          <h3 className="mt-1 text-base font-semibold text-slate-950">
            Provenance records
          </h3>
        </div>

        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-500">
          {records.length} records
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-[1050px] w-full border-collapse text-left">
          <thead className="bg-slate-50/80">
            <tr className="border-b border-slate-200">
              {[
                'Recommendation',
                'Query fingerprint',
                'Index',
                'Experiment',
                'Provenance',
                'Evidence',
              ].map((heading) => (
                <th
                  key={heading}
                  className="px-5 py-3 text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400"
                >
                  {heading}
                </th>
              ))}
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
                  className={`cursor-pointer border-b border-slate-100 transition last:border-b-0 ${
                    selected
                      ? 'bg-blue-50/70'
                      : 'hover:bg-slate-50'
                  }`}
                >
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <span
                        className={`h-8 w-1 rounded-full ${
                          selected ? 'bg-blue-500' : 'bg-transparent'
                        }`}
                      />

                      <div>
                        <p className="font-mono text-sm font-semibold text-slate-900">
                          #{record.recommendation_id}
                        </p>

                        <p className="mt-1 text-[11px] text-slate-400">
                          Recommendation record
                        </p>
                      </div>
                    </div>
                  </td>

                  <td className="px-5 py-4">
                    <span
                      className="block max-w-[250px] truncate font-mono text-[11px] text-slate-500"
                      title={record.query_fingerprint || undefined}
                    >
                      {record.query_fingerprint || 'Not available'}
                    </span>
                  </td>

                  <td className="px-5 py-4">
                    <span
                      className="block max-w-[220px] truncate font-mono text-[11px] text-slate-600"
                      title={record.index_name || undefined}
                    >
                      {record.index_name || 'Not available'}
                    </span>
                  </td>

                  <td className="px-5 py-4">
                    <span className="font-mono text-xs font-semibold text-slate-600">
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

      <div className="border-t border-slate-200 bg-slate-50/60 px-5 py-3">
        <p className="text-xs text-slate-400">
          Showing {records.length} provenance record
          {records.length === 1 ? '' : 's'} from the reporting API.
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
            setSelectedRecommendationId(data[0].recommendation_id)
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

  const statuses = useMemo(
    () => [
      'ALL',
      ...Array.from(
        new Set(
          records
            .map((record) => record.status)
            .filter(Boolean),
        ),
      ).sort(),
    ],
    [records],
  )

  const evidenceStatuses = useMemo(
    () => [
      'ALL',
      ...Array.from(
        new Set(
          records
            .map((record) => record.evidence_status)
            .filter(Boolean),
        ),
      ).sort(),
    ],
    [records],
  )

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

      return (
        matchesStatus &&
        matchesEvidence &&
        (normalizedSearch.length === 0 ||
          searchable.includes(normalizedSearch))
      )
    })
  }, [records, search, status, evidenceStatus])

  const selectedRecord = useMemo(
    () =>
      records.find(
        (record) =>
          record.recommendation_id ===
          selectedRecommendationId,
      ) || null,
    [records, selectedRecommendationId],
  )

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
      <div className="rounded-2xl border border-slate-200 bg-white p-10 shadow-sm">
        <p className="text-sm text-slate-500">
          Loading evidence and provenance...
        </p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-red-200 bg-white p-8 shadow-sm">
        <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-red-500">
          Reporting error
        </p>

        <h3 className="mt-2 text-lg font-semibold text-slate-900">
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
    <div className="space-y-7">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-7 shadow-sm">
        <div className="absolute right-0 top-0 h-40 w-64 rounded-bl-full bg-gradient-to-br from-cyan-50 via-blue-50 to-transparent" />

        <div className="relative flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <SectionLabel tone="cyan">
              Decision &amp; evidence
            </SectionLabel>

            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
              Evidence &amp; Provenance Intelligence
            </h1>

            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
              Trace recommendation evidence through explicitly established
              experimental provenance without inferring missing links.
            </p>
          </div>

          <div className="relative min-w-[180px] rounded-xl border border-cyan-100 bg-cyan-50/50 px-5 py-4">
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-cyan-600">
              Evidence register
            </p>

            <p className="mt-2 text-3xl font-semibold text-slate-950">
              {summary.total}
            </p>

            <p className="mt-1 text-xs text-slate-400">
              recommendation provenance records
            </p>
          </div>
        </div>
      </section>

      {/* KPI summary */}
      <section>
        <div className="mb-3">
          <SectionLabel tone="blue">
            Evidence snapshot
          </SectionLabel>

          <h2 className="mt-2 text-xl font-semibold text-slate-950">
            Provenance coverage
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Current provenance and evidence-completeness states reported by
            the M20 reporting API.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
          <SummaryCard
            label="Total records"
            value={summary.total}
            description="Recommendation provenance records"
            tone="blue"
          />

          <SummaryCard
            label="Linked"
            value={summary.linked}
            description="Explicit experimental linkage established"
            tone="cyan"
          />

          <SummaryCard
            label="Not established"
            value={summary.notEstablished}
            description="No explicit experimental linkage"
            tone="slate"
          />

          <SummaryCard
            label="Complete"
            value={summary.complete}
            description="Evidence status COMPLETE"
            tone="emerald"
          />

          <SummaryCard
            label="Insufficient"
            value={summary.insufficient}
            description="Evidence status INSUFFICIENT"
            tone="violet"
          />
        </div>
      </section>

      {/* Provenance health */}
      <section className="grid gap-5 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <SectionLabel tone="cyan">
            Provenance state
          </SectionLabel>

          <h2 className="mt-2 text-lg font-semibold text-slate-950">
            Explicit linkage coverage
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Only explicitly established experimental relationships are shown
            as linked.
          </p>

          <div className="mt-5 space-y-3">
            <DistributionCard
              label="Linked"
              value={summary.linked}
              total={summary.total}
              description="Explicit provenance established"
              tone="cyan"
            />

            <DistributionCard
              label="Not established"
              value={summary.notEstablished}
              total={summary.total}
              description="No explicit experimental linkage"
              tone="slate"
            />
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <SectionLabel tone="violet">
            Evidence completeness
          </SectionLabel>

          <h2 className="mt-2 text-lg font-semibold text-slate-950">
            Evidence readiness
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Completeness is reported independently from provenance linkage.
          </p>

          <div className="mt-5 space-y-3">
            <DistributionCard
              label="Complete"
              value={summary.complete}
              total={summary.total}
              description="Required evidence available"
              tone="emerald"
            />

            <DistributionCard
              label="Partial"
              value={summary.partial}
              total={summary.total}
              description="Evidence partially established"
              tone="violet"
            />

            <DistributionCard
              label="Insufficient"
              value={summary.insufficient}
              total={summary.total}
              description="Evidence not sufficient for complete linkage"
              tone="slate"
            />
          </div>
        </div>
      </section>

      {/* Evidence chain */}
      <section className="rounded-2xl border border-blue-100 bg-gradient-to-r from-blue-50/70 via-white to-cyan-50/50 p-6 shadow-sm">
        <SectionLabel tone="blue">
          Evidence chain
        </SectionLabel>

        <h2 className="mt-2 text-lg font-semibold text-slate-950">
          Recommendation → experiment provenance
        </h2>

        <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-500">
          A provenance record preserves the identity of the recommendation
          and the explicitly established evidence relationship.
        </p>

        <div className="mt-6 grid gap-3 md:grid-cols-5">
          {[
            ['01', 'Recommendation', 'Recommendation ID'],
            ['02', 'Query', 'Query fingerprint'],
            ['03', 'Index', 'Index identity'],
            ['04', 'Experiment', 'Linked experiment'],
            ['05', 'Evidence', 'Completeness state'],
          ].map(([number, title, detail], index) => (
            <div
              key={title}
              className="relative rounded-xl border border-slate-200 bg-white p-4"
            >
              <div className="flex items-center gap-3">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100 text-[10px] font-bold text-slate-500">
                  {number}
                </span>

                <div>
                  <p className="text-sm font-semibold text-slate-900">
                    {title}
                  </p>

                  <p className="mt-0.5 text-[10px] text-slate-400">
                    {detail}
                  </p>
                </div>
              </div>

              {index < 4 && (
                <span className="absolute -right-2 top-1/2 hidden h-4 w-4 -translate-y-1/2 items-center justify-center rounded-full bg-white text-slate-300 md:flex">
                  →
                </span>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Filters */}
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-end">
          <div className="flex-1">
            <SectionLabel tone="blue">
              Evidence register
            </SectionLabel>

            <h2 className="mt-2 text-lg font-semibold text-slate-950">
              Explore provenance records
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Search by recommendation, fingerprint, index, experiment, or
              evidence state.
            </p>
          </div>

          <div className="flex flex-col gap-3 lg:flex-row">
            <div className="lg:w-80">
              <label
                htmlFor="provenance-search"
                className="mb-2 block text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400"
              >
                Search evidence
              </label>

              <input
                id="provenance-search"
                type="text"
                value={search}
                onChange={(event) =>
                  setSearch(event.target.value)
                }
                placeholder="Recommendation, fingerprint, index..."
                className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-400 focus:bg-white focus:ring-2 focus:ring-blue-100"
              />
            </div>

            <div className="lg:w-48">
              <label
                htmlFor="provenance-status"
                className="mb-2 block text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400"
              >
                Provenance
              </label>

              <select
                id="provenance-status"
                value={status}
                onChange={(event) =>
                  setStatus(event.target.value)
                }
                className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-400 focus:bg-white focus:ring-2 focus:ring-blue-100"
              >
                {statuses.map((value) => (
                  <option key={value} value={value}>
                    {value}
                  </option>
                ))}
              </select>
            </div>

            <div className="lg:w-48">
              <label
                htmlFor="provenance-evidence"
                className="mb-2 block text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400"
              >
                Evidence
              </label>

              <select
                id="provenance-evidence"
                value={evidenceStatus}
                onChange={(event) =>
                  setEvidenceStatus(event.target.value)
                }
                className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-400 focus:bg-white focus:ring-2 focus:ring-blue-100"
              >
                {evidenceStatuses.map((value) => (
                  <option key={value} value={value}>
                    {value}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="mt-5 flex items-center justify-between border-t border-slate-100 pt-4">
          <p className="text-xs text-slate-400">
            Showing{' '}
            <span className="font-semibold text-slate-600">
              {filteredRecords.length}
            </span>{' '}
            of{' '}
            <span className="font-semibold text-slate-600">
              {records.length}
            </span>{' '}
            provenance records.
          </p>

          <button
            type="button"
            onClick={() => {
              setSearch('')
              setStatus('ALL')
              setEvidenceStatus('ALL')
            }}
            className="text-xs font-semibold text-blue-600 transition hover:text-blue-700"
          >
            Reset filters
          </button>
        </div>
      </section>

      <ProvenanceTable
        records={filteredRecords}
        selectedRecommendationId={selectedRecommendationId}
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

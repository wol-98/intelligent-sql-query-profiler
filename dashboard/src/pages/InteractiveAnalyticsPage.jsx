import { useEffect, useMemo, useState } from 'react'

import {
  getBenchmarks,
  getCompositeIndexes,
  getCostBenefits,
  getProductionDecisions,
  getProvenance,
  getQueries,
  getWorkloads,
} from '../api/client'

const MAX_BARS = 8

function recommendationMatches(id, recommendationFilter, effectiveRecommendationIds) {
  if (id === null || id === undefined) {
    return recommendationFilter === 'ALL' && !effectiveRecommendationIds
  }

  const numericId = Number(id)

  if (recommendationFilter !== 'ALL' && numericId !== Number(recommendationFilter)) {
    return false
  }

  if (effectiveRecommendationIds && !effectiveRecommendationIds.has(numericId)) {
    return false
  }

  return true
}

function formatNumber(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '—'
  }

  return Number(value).toLocaleString(undefined, {
    maximumFractionDigits: digits,
  })
}

function formatPercent(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '—'
  }

  return `${formatNumber(value, digits)}%`
}

function shortText(value, length = 22) {
  const text = String(value ?? '')
  return text.length > length ? `${text.slice(0, length - 1)}…` : text
}

function badgeClass(value) {
  const normalized = String(value ?? '').toUpperCase()

  if (['SUCCESSFUL', 'APPROVED', 'ACCEPT', 'MEASURED', 'COMPLETE'].includes(normalized)) {
    return 'bg-emerald-50 text-emerald-700 ring-emerald-200'
  }

  if (['UNSUCCESSFUL', 'REJECTED', 'BLOCKED'].includes(normalized)) {
    return 'bg-rose-50 text-rose-700 ring-rose-200'
  }

  if (['PARTIAL', 'INSUFFICIENT', 'NEUTRAL', 'PENDING'].includes(normalized)) {
    return 'bg-amber-50 text-amber-700 ring-amber-200'
  }

  return 'bg-slate-100 text-slate-600 ring-slate-200'
}

function StatusBadge({ value }) {
  if (value === null || value === undefined || value === '') {
    return <span className="text-slate-400">—</span>
  }

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-1 text-[0.68rem] font-bold uppercase tracking-[0.08em] ring-1 ${badgeClass(value)}`}
    >
      {String(value).replaceAll('_', ' ')}
    </span>
  )
}

function SectionHeader({ eyebrow, title, question, action }) {
  return (
    <div className="mb-5 flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p className="text-[0.67rem] font-bold uppercase tracking-[0.18em] text-blue-600">
          {eyebrow}
        </p>
        <h2 className="mt-1 text-lg font-bold text-slate-900">{title}</h2>
        <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-500">
          {question}
        </p>
      </div>

      {action}
    </div>
  )
}

function MetricCard({ label, value, detail }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-[0.68rem] font-bold uppercase tracking-[0.16em] text-slate-400">
        {label}
      </p>
      <p className="mt-2 text-2xl font-bold tracking-tight text-slate-900">{value}</p>
      {detail && <p className="mt-1 text-xs leading-5 text-slate-500">{detail}</p>}
    </div>
  )
}

function HorizontalBars({ items, valueKey, labelKey, onSelect, selectedLabel }) {
  const maxValue = Math.max(...items.map((item) => Number(item[valueKey] ?? 0)), 1)

  return (
    <div className="space-y-3">
      {items.map((item) => {
        const value = Number(item[valueKey] ?? 0)
        const label = String(item[labelKey] ?? '')
        const selected = selectedLabel === label

        return (
          <button
            key={label}
            type="button"
            onClick={() => onSelect?.(item)}
            className={`w-full rounded-xl p-2 text-left transition ${selected ? 'bg-blue-50 ring-1 ring-blue-200' : 'hover:bg-slate-50'}`}
          >
            <div className="mb-1 flex items-center justify-between gap-3 text-xs">
              <span className="truncate font-semibold text-slate-700">{shortText(label, 32)}</span>
              <span className="shrink-0 font-bold text-slate-600">{formatNumber(value)}</span>
            </div>
            <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-blue-500 transition-all"
                style={{ width: `${Math.max((value / maxValue) * 100, value > 0 ? 3 : 0)}%` }}
              />
            </div>
          </button>
        )
      })}
    </div>
  )
}

function OutcomeSegments({ items, onSelect, selected }) {
  const total = items.reduce((sum, item) => sum + item.count, 0) || 1
  const segments = [
    { key: 'SUCCESSFUL', label: 'Successful', className: 'bg-emerald-500' },
    { key: 'NEUTRAL', label: 'Neutral', className: 'bg-amber-400' },
    { key: 'UNSUCCESSFUL', label: 'Unsuccessful', className: 'bg-rose-500' },
    { key: 'OTHER', label: 'Other', className: 'bg-slate-400' },
  ]

  return (
    <div>
      <div className="flex h-5 overflow-hidden rounded-full bg-slate-100">
        {segments.map((segment) => {
          const item = items.find((entry) => entry.key === segment.key)
          const count = item?.count ?? 0
          const width = `${(count / total) * 100}%`

          if (!count) return null

          return (
            <button
              key={segment.key}
              type="button"
              aria-label={`${segment.label}: ${count}`}
              title={`${segment.label}: ${count}`}
              onClick={() => onSelect?.(segment.key)}
              className={`${segment.className} h-full transition-opacity ${selected && selected !== segment.key ? 'opacity-35' : ''}`}
              style={{ width }}
            />
          )
        })}
      </div>

      <div className="mt-4 grid gap-2 sm:grid-cols-2">
        {segments.map((segment) => {
          const count = items.find((entry) => entry.key === segment.key)?.count ?? 0

          return (
            <button
              key={segment.key}
              type="button"
              onClick={() => onSelect?.(segment.key)}
              className={`flex items-center justify-between rounded-lg border px-3 py-2 text-left ${selected === segment.key ? 'border-blue-200 bg-blue-50' : 'border-slate-200 bg-slate-50'}`}
            >
              <span className="flex items-center gap-2 text-xs font-semibold text-slate-600">
                <span className={`h-2 w-2 rounded-full ${segment.className}`} />
                {segment.label}
              </span>
              <span className="text-xs font-bold text-slate-800">{count}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

function BenchmarkComparison({ benchmarks, onSelect }) {
  const rows = benchmarks
    .filter((item) => item.baseline_time_ms !== null || item.indexed_time_ms !== null)
    .slice()
    .sort((a, b) => Number(b.baseline_time_ms ?? 0) - Number(a.baseline_time_ms ?? 0))
    .slice(0, MAX_BARS)

  const maxTime = Math.max(
    ...rows.flatMap((item) => [Number(item.baseline_time_ms ?? 0), Number(item.indexed_time_ms ?? 0)]),
    1,
  )

  return (
    <div className="space-y-4">
      {rows.length === 0 ? (
        <p className="rounded-xl bg-slate-50 p-5 text-sm text-slate-500">
          No benchmark timing data is available for the current filters.
        </p>
      ) : (
        rows.map((item) => {
          const baseline = Number(item.baseline_time_ms ?? 0)
          const indexed = Number(item.indexed_time_ms ?? 0)

          return (
            <button
              key={item.benchmark_id ?? `${item.recommendation_id}-${baseline}`}
              type="button"
              onClick={() => onSelect?.(item)}
              className="w-full rounded-xl border border-slate-200 bg-slate-50/70 p-4 text-left transition hover:border-blue-200 hover:bg-blue-50/40"
            >
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-xs font-bold text-slate-800">
                    Recommendation #{item.recommendation_id ?? '—'}
                  </p>
                  <p className="mt-1 text-[0.68rem] uppercase tracking-[0.12em] text-slate-400">
                    Benchmark #{item.benchmark_id ?? '—'}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <StatusBadge value={item.outcome} />
                  <span className="text-sm font-bold text-emerald-700">
                    {formatPercent(item.improvement_percent)}
                  </span>
                </div>
              </div>

              <div className="mt-4 space-y-2">
                <div className="flex items-center gap-3">
                  <span className="w-14 text-[0.68rem] font-semibold uppercase tracking-[0.08em] text-slate-400">
                    Base
                  </span>
                  <div className="h-3 flex-1 overflow-hidden rounded-full bg-slate-200">
                    <div className="h-full rounded-full bg-slate-500" style={{ width: `${Math.max((baseline / maxTime) * 100, 2)}%` }} />
                  </div>
                  <span className="w-20 text-right text-xs font-bold text-slate-600">
                    {formatNumber(baseline)} ms
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="w-14 text-[0.68rem] font-semibold uppercase tracking-[0.08em] text-slate-400">
                    Indexed
                  </span>
                  <div className="h-3 flex-1 overflow-hidden rounded-full bg-emerald-50">
                    <div className="h-full rounded-full bg-emerald-500" style={{ width: `${Math.max((indexed / maxTime) * 100, indexed > 0 ? 2 : 0)}%` }} />
                  </div>
                  <span className="w-20 text-right text-xs font-bold text-slate-600">
                    {formatNumber(indexed)} ms
                  </span>
                </div>
              </div>
            </button>
          )
        })
      )}
    </div>
  )
}

function CostBenefitScatter({ items, onSelect }) {
  const width = 520
  const height = 270
  const padding = { top: 18, right: 24, bottom: 45, left: 54 }
  const plotWidth = width - padding.left - padding.right
  const plotHeight = height - padding.top - padding.bottom
  const maxX = Math.max(...items.map((item) => Number(item.storage?.ratio_percent ?? 0)), 1)
  const maxY = Math.max(
    ...items.map((item) => Number(item.read?.average_improvement_percent ?? 0)),
    1,
  )

  return (
    <div>
      {items.length === 0 ? (
        <p className="rounded-xl bg-slate-50 p-5 text-sm text-slate-500">
          No cost-benefit evidence is available for the current filters.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <svg viewBox={`0 0 ${width} ${height}`} className="min-w-[520px] w-full" role="img" aria-label="Read improvement versus storage ratio scatter plot">
            <line x1={padding.left} y1={padding.top + plotHeight} x2={padding.left + plotWidth} y2={padding.top + plotHeight} stroke="currentColor" className="text-slate-200" />
            <line x1={padding.left} y1={padding.top} x2={padding.left} y2={padding.top + plotHeight} stroke="currentColor" className="text-slate-200" />

            {[0, 0.5, 1].map((step) => (
              <g key={step}>
                <line
                  x1={padding.left}
                  y1={padding.top + plotHeight - plotHeight * step}
                  x2={padding.left + plotWidth}
                  y2={padding.top + plotHeight - plotHeight * step}
                  stroke="currentColor"
                  className="text-slate-100"
                />
                <text
                  x={padding.left - 8}
                  y={padding.top + plotHeight - plotHeight * step + 4}
                  textAnchor="end"
                  className="fill-slate-400 text-[10px]"
                >
                  {formatPercent(maxY * step)}
                </text>
              </g>
            ))}

            {items.map((item) => {
              const xValue = Number(item.storage?.ratio_percent ?? 0)
              const yValue = Number(item.read?.average_improvement_percent ?? 0)
              const x = padding.left + (xValue / maxX) * plotWidth
              const y = padding.top + plotHeight - (yValue / maxY) * plotHeight

              return (
                <g key={item.experiment_id}>
                  <circle
                    cx={x}
                    cy={y}
                    r="7"
                    className="cursor-pointer fill-blue-500 stroke-white stroke-2 hover:fill-blue-700"
                    onClick={() => onSelect?.(item)}
                  >
                    <title>{`Recommendation #${item.recommendation_id ?? '—'} · ${formatPercent(yValue)} read improvement · ${formatPercent(xValue)} storage ratio`}</title>
                  </circle>
                </g>
              )
            })}

            <text x={padding.left + plotWidth / 2} y={height - 8} textAnchor="middle" className="fill-slate-400 text-[10px]">
              Storage ratio (%)
            </text>
            <text
              x="14"
              y={padding.top + plotHeight / 2}
              transform={`rotate(-90 14 ${padding.top + plotHeight / 2})`}
              textAnchor="middle"
              className="fill-slate-400 text-[10px]"
            >
              Read improvement (%)
            </text>
          </svg>
        </div>
      )}

      {items.length > 0 && (
        <div className="mt-3 space-y-2">
          {items.map((item) => (
            <button
              key={`${item.experiment_id}-detail`}
              type="button"
              onClick={() => onSelect?.(item)}
              className="flex w-full items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-left hover:bg-blue-50"
            >
              <span className="text-xs font-semibold text-slate-600">
                Recommendation #{item.recommendation_id ?? '—'}
              </span>
              <span className="text-xs font-bold text-slate-800">
                {formatPercent(item.read?.average_improvement_percent)} · {formatPercent(item.storage?.ratio_percent)} storage
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

function CompositeOrderComparison({ items, onSelect }) {
  return (
    <div className="space-y-3">
      {items.length === 0 ? (
        <p className="rounded-xl bg-slate-50 p-5 text-sm text-slate-500">
          No composite-index order evidence matches the current filters.
        </p>
      ) : (
        items.map((item) => (
          <button
            key={item.recommendation_id}
            type="button"
            onClick={() => onSelect?.(item)}
            className="w-full rounded-xl border border-slate-200 bg-slate-50 p-4 text-left transition hover:border-blue-200 hover:bg-blue-50/40"
          >
            <div className="flex items-center justify-between gap-3">
              <span className="text-xs font-bold text-slate-800">
                Recommendation #{item.recommendation_id}
              </span>
              <span className="text-xs font-bold text-violet-700">
                {formatNumber(item.order_effect_percentage_points)} pp effect
              </span>
            </div>

            <div className="mt-3 grid gap-3 md:grid-cols-2">
              <div className="rounded-lg bg-white p-3 ring-1 ring-slate-200">
                <p className="text-[0.64rem] font-bold uppercase tracking-[0.08em] text-slate-400">Original order</p>
                <p className="mt-1 break-words text-xs font-semibold text-slate-700">
                  {item.original_order.join(' → ') || 'Not available'}
                </p>
                <p className="mt-2 text-xs text-slate-500">
                  Improvement: <span className="font-bold text-slate-700">{formatPercent(item.original_improvement_percent)}</span>
                </p>
              </div>
              <div className="rounded-lg bg-white p-3 ring-1 ring-slate-200">
                <p className="text-[0.64rem] font-bold uppercase tracking-[0.08em] text-slate-400">Alternative order</p>
                <p className="mt-1 break-words text-xs font-semibold text-slate-700">
                  {item.alternative_order.join(' → ') || 'Not available'}
                </p>
                <p className="mt-2 text-xs text-slate-500">
                  Improvement: <span className="font-bold text-slate-700">{formatPercent(item.alternative_improvement_percent)}</span>
                </p>
              </div>
            </div>
          </button>
        ))
      )}
    </div>
  )
}

function QueryPlanSummary({ query, onSelect }) {
  if (!query) {
    return <p className="rounded-xl bg-slate-50 p-5 text-sm text-slate-500">No query profile is available.</p>
  }

  const plan = query.plan

  return (
    <button
      type="button"
      onClick={() => onSelect?.(query)}
      className="w-full rounded-xl border border-slate-200 bg-slate-50 p-4 text-left transition hover:border-blue-200 hover:bg-blue-50/40"
    >
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <p className="text-xs font-bold text-slate-800">Query #{query.query_profile_id}</p>
          <p className="mt-1 truncate font-mono text-[0.68rem] text-slate-500">{shortText(query.fingerprint, 42)}</p>
        </div>
        <div className="flex gap-2 text-xs">
          <span className="rounded-lg bg-white px-2 py-1 font-bold text-slate-600 ring-1 ring-slate-200">
            {formatNumber(query.total_execution_time_ms)} ms total
          </span>
          <span className="rounded-lg bg-white px-2 py-1 font-bold text-slate-600 ring-1 ring-slate-200">
            {formatNumber(query.execution_count, 0)} runs
          </span>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {(plan?.node_types ?? []).map((node) => (
          <span key={node} className="rounded-full bg-white px-2.5 py-1 text-[0.66rem] font-semibold text-slate-600 ring-1 ring-slate-200">
            {node}
          </span>
        ))}
      </div>

      <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4">
        <div className="rounded-lg bg-white p-2.5 ring-1 ring-slate-200">
          <p className="text-[0.61rem] uppercase tracking-[0.08em] text-slate-400">Seq scans</p>
          <p className="mt-1 text-sm font-bold text-slate-700">{plan?.sequential_scans ?? 0}</p>
        </div>
        <div className="rounded-lg bg-white p-2.5 ring-1 ring-slate-200">
          <p className="text-[0.61rem] uppercase tracking-[0.08em] text-slate-400">Index scans</p>
          <p className="mt-1 text-sm font-bold text-slate-700">{plan?.index_scans ?? 0}</p>
        </div>
        <div className="rounded-lg bg-white p-2.5 ring-1 ring-slate-200">
          <p className="text-[0.61rem] uppercase tracking-[0.08em] text-slate-400">Joins</p>
          <p className="mt-1 text-sm font-bold text-slate-700">{plan?.joins ?? 0}</p>
        </div>
        <div className="rounded-lg bg-white p-2.5 ring-1 ring-slate-200">
          <p className="text-[0.61rem] uppercase tracking-[0.08em] text-slate-400">Index condition</p>
          <p className="mt-1 text-sm font-bold text-slate-700">{plan?.has_index_condition ? 'Yes' : 'No'}</p>
        </div>
      </div>
    </button>
  )
}

function JourneyStep({ number, title, detail, complete, active }) {
  return (
    <div className={`relative rounded-xl border p-4 ${active ? 'border-blue-200 bg-blue-50/50' : 'border-slate-200 bg-slate-50'}`}>
      <div className="flex items-start gap-3">
        <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-xs font-bold ${complete ? 'bg-emerald-500 text-white' : active ? 'bg-blue-600 text-white' : 'bg-white text-slate-400 ring-1 ring-slate-200'}`}>
          {complete ? '✓' : number}
        </div>
        <div className="min-w-0">
          <p className="text-xs font-bold text-slate-800">{title}</p>
          <p className="mt-1 text-[0.72rem] leading-5 text-slate-500">{detail}</p>
        </div>
      </div>
    </div>
  )
}

function InteractiveAnalyticsPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [recommendationFilter, setRecommendationFilter] = useState('ALL')
  const [outcomeFilter, setOutcomeFilter] = useState('ALL')
  const [evidenceFilter, setEvidenceFilter] = useState('ALL')
  const [priorityFilter, setPriorityFilter] = useState('ALL')
  const [selectedWorkloadFingerprint, setSelectedWorkloadFingerprint] = useState(null)
  const [selectedQueryId, setSelectedQueryId] = useState(null)

  useEffect(() => {
    let mounted = true

    async function loadAnalytics() {
      try {
        setLoading(true)
        setError(null)

        const [workloads, benchmarks, costBenefits, compositeIndexes, queries, decisions, provenance] = await Promise.all([
          getWorkloads(),
          getBenchmarks(),
          getCostBenefits(),
          getCompositeIndexes(),
          getQueries(),
          getProductionDecisions(),
          getProvenance(),
        ])

        if (mounted) {
          setData({ workloads, benchmarks, costBenefits, compositeIndexes, queries, decisions, provenance })
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

    loadAnalytics()

    return () => {
      mounted = false
    }
  }, [])

  const recommendationIds = useMemo(() => {
    if (!data) return []

    const ids = new Set()

    for (const row of data.workloads) {
      for (const id of row.recommendation_ids ?? []) ids.add(Number(id))
    }
    for (const row of data.benchmarks) if (row.recommendation_id !== null) ids.add(Number(row.recommendation_id))
    for (const row of data.costBenefits) if (row.recommendation_id !== null) ids.add(Number(row.recommendation_id))
    for (const row of data.compositeIndexes) if (row.recommendation_id !== null) ids.add(Number(row.recommendation_id))
    for (const row of data.queries) for (const id of row.recommendation_ids ?? []) ids.add(Number(id))
    for (const row of data.decisions) if (row.recommendation_id !== null) ids.add(Number(row.recommendation_id))
    for (const row of data.provenance) if (row.recommendation_id !== null) ids.add(Number(row.recommendation_id))

    return Array.from(ids).sort((a, b) => a - b)
  }, [data])

  const evidenceStatuses = useMemo(() => {
    if (!data) return []

    const values = new Set()
    for (const row of data.costBenefits) if (row.evidence_status) values.add(row.evidence_status)
    for (const row of data.decisions) if (row.evidence_status) values.add(row.evidence_status)
    for (const row of data.provenance) if (row.evidence_status) values.add(row.evidence_status)
    return Array.from(values).sort()
  }, [data])

  const priorities = useMemo(() => {
    if (!data) return []
    return Array.from(new Set(data.workloads.map((row) => row.priority).filter(Boolean))).sort()
  }, [data])

  const effectiveRecommendationIds = useMemo(() => {
    if (!selectedWorkloadFingerprint || !data) return null
    const selected = data.workloads.find((row) => row.fingerprint === selectedWorkloadFingerprint)
    return selected ? new Set((selected.recommendation_ids ?? []).map(Number)) : null
  }, [data, selectedWorkloadFingerprint])

  const filtered = useMemo(() => {
    if (!data) {
      return {
        workloads: [],
        benchmarks: [],
        costBenefits: [],
        compositeIndexes: [],
        queries: [],
        decisions: [],
        provenance: [],
      }
    }

    return {
      workloads: data.workloads.filter((row) => {
        if (priorityFilter !== 'ALL' && row.priority !== priorityFilter) return false
        if (selectedWorkloadFingerprint && row.fingerprint !== selectedWorkloadFingerprint) return false
        if (row.recommendation_ids?.length && !row.recommendation_ids.some((id) => recommendationMatches(id, recommendationFilter, effectiveRecommendationIds))) return false
        return !recommendationFilter || recommendationFilter === 'ALL' || (row.recommendation_ids ?? []).some((id) => Number(id) === Number(recommendationFilter))
      }),
      benchmarks: data.benchmarks.filter((row) => recommendationMatches(row.recommendation_id, recommendationFilter, effectiveRecommendationIds) && (outcomeFilter === 'ALL' || row.outcome === outcomeFilter)),
      costBenefits: data.costBenefits.filter((row) => recommendationMatches(row.recommendation_id, recommendationFilter, effectiveRecommendationIds) && (evidenceFilter === 'ALL' || row.evidence_status === evidenceFilter)),
      compositeIndexes: data.compositeIndexes.filter((row) => recommendationMatches(row.recommendation_id, recommendationFilter, effectiveRecommendationIds)),
      queries: data.queries.filter((row) => {
        if (selectedQueryId !== null && row.query_profile_id !== selectedQueryId) return false
        if (row.recommendation_ids?.length && !row.recommendation_ids.some((id) => recommendationMatches(id, recommendationFilter, effectiveRecommendationIds))) return false
        return recommendationFilter === 'ALL' && !effectiveRecommendationIds || (row.recommendation_ids ?? []).some((id) => recommendationMatches(id, recommendationFilter, effectiveRecommendationIds))
      }),
      decisions: data.decisions.filter((row) => recommendationMatches(row.recommendation_id, recommendationFilter, effectiveRecommendationIds) && (evidenceFilter === 'ALL' || row.evidence_status === evidenceFilter)),
      provenance: data.provenance.filter((row) => recommendationMatches(row.recommendation_id, recommendationFilter, effectiveRecommendationIds) && (evidenceFilter === 'ALL' || row.evidence_status === evidenceFilter)),
    }
  }, [
    data,
    effectiveRecommendationIds,
    evidenceFilter,
    outcomeFilter,
    priorityFilter,
    recommendationFilter,
    selectedQueryId,
    selectedWorkloadFingerprint,
  ])

  const workloadBars = useMemo(
    () => filtered.workloads
      .slice()
      .sort((a, b) => Number(b.total_execution_time_ms ?? 0) - Number(a.total_execution_time_ms ?? 0))
      .slice(0, MAX_BARS),
    [filtered.workloads],
  )

  const timeShareBars = useMemo(
    () => filtered.workloads
      .slice()
      .sort((a, b) => Number(b.time_share ?? 0) - Number(a.time_share ?? 0))
      .slice(0, MAX_BARS)
      .map((row) => ({ ...row, label: row.fingerprint, value: Number(row.time_share ?? 0) })),
    [filtered.workloads],
  )

  const outcomeSegments = useMemo(() => {
    if (!data) return []
    const counts = new Map()
    for (const row of filtered.benchmarks) {
      const rawKey = row.outcome || 'OTHER'
      const key = ['SUCCESSFUL', 'NEUTRAL', 'UNSUCCESSFUL'].includes(rawKey) ? rawKey : 'OTHER'
      counts.set(key, (counts.get(key) ?? 0) + 1)
    }
    return Array.from(counts, ([key, count]) => ({ key, count }))
  }, [data, filtered.benchmarks])

  const selectedQuery = filtered.queries.find((row) => row.query_profile_id === selectedQueryId) ?? filtered.queries[0] ?? null
  const selectedRecommendation = recommendationFilter !== 'ALL' ? Number(recommendationFilter) : (filtered.benchmarks.find((row) => row.recommendation_id !== null)?.recommendation_id ?? filtered.decisions[0]?.recommendation_id ?? null)

  const journey = useMemo(() => {
    if (!selectedRecommendation || !data) return null

    const recommendationId = Number(selectedRecommendation)
    const benchmarks = data.benchmarks.filter((row) => Number(row.recommendation_id) === recommendationId)
    const costs = data.costBenefits.filter((row) => Number(row.recommendation_id) === recommendationId)
    const decisions = data.decisions.filter((row) => Number(row.recommendation_id) === recommendationId)
    const provenance = data.provenance.filter((row) => Number(row.recommendation_id) === recommendationId)
    const query = data.queries.find((row) => (row.recommendation_ids ?? []).some((id) => Number(id) === recommendationId))

    return {
      recommendationId,
      query,
      benchmarks,
      costs,
      decisions,
      provenance,
    }
  }, [data, selectedRecommendation])

  function clearFilters() {
    setRecommendationFilter('ALL')
    setOutcomeFilter('ALL')
    setEvidenceFilter('ALL')
    setPriorityFilter('ALL')
    setSelectedWorkloadFingerprint(null)
    setSelectedQueryId(null)
  }

  if (loading) {
    return (
      <div className="dashboard-card p-8">
        <div className="flex items-center gap-3">
          <span className="h-2 w-2 animate-pulse rounded-full bg-blue-500" />
          <p className="text-sm font-medium text-slate-500">Loading interactive analytics...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-rose-200 bg-white p-8 shadow-sm">
        <h2 className="text-lg font-bold text-slate-900">Unable to load interactive analytics</h2>
        <p className="mt-2 text-sm leading-6 text-slate-500">{error}</p>
      </div>
    )
  }

  const measuredBenchmarks = filtered.benchmarks.filter((row) => row.improvement_percent !== null)
  const totalTime = filtered.workloads.reduce((sum, row) => sum + Number(row.total_execution_time_ms ?? 0), 0)
  const averageImprovement = measuredBenchmarks.length
    ? measuredBenchmarks.reduce((sum, row) => sum + Number(row.improvement_percent ?? 0), 0) / measuredBenchmarks.length
    : null

  return (
    <div className="space-y-7">
      <section className="rounded-3xl border border-slate-200 bg-gradient-to-br from-white via-white to-blue-50/70 p-6 shadow-sm md:p-8">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div className="max-w-3xl">
            <p className="text-[0.68rem] font-bold uppercase tracking-[0.2em] text-blue-600">M21.17 · Interactive analytics</p>
            <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">Optimization Evidence Explorer</h1>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              Interactive analytical views for workload, benchmark, cost-benefit, composite-index, query-plan, decision, and provenance evidence. Select a chart category to cross-filter related evidence without replacing the existing reporting pages.
            </p>
          </div>

          <button
            type="button"
            onClick={clearFilters}
            className="w-fit rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-xs font-bold uppercase tracking-[0.08em] text-slate-600 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
          >
            Clear cross-filters
          </button>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard label="Workloads" value={filtered.workloads.length} detail="Stored workload fingerprints in view" />
          <MetricCard label="Benchmark evidence" value={filtered.benchmarks.length} detail="Baseline/indexed comparisons in view" />
          <MetricCard label="Avg measured improvement" value={formatPercent(averageImprovement)} detail="Across benchmark rows with improvement values" />
          <MetricCard label="Execution time in view" value={`${formatNumber(totalTime)} ms`} detail="Combined workload total execution time" />
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <p className="text-[0.67rem] font-bold uppercase tracking-[0.18em] text-slate-400">Cross-filter context</p>
            <p className="mt-1 text-sm text-slate-600">Filters propagate through recommendation, workload, benchmark, evidence, and query relationships.</p>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <label className="text-xs font-semibold text-slate-600">
              Recommendation
              <select
                value={recommendationFilter}
                onChange={(event) => setRecommendationFilter(event.target.value)}
                className="mt-1.5 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-50"
              >
                <option value="ALL">All recommendations</option>
                {recommendationIds.map((id) => <option key={id} value={id}>#{id}</option>)}
              </select>
            </label>

            <label className="text-xs font-semibold text-slate-600">
              Benchmark outcome
              <select
                value={outcomeFilter}
                onChange={(event) => setOutcomeFilter(event.target.value)}
                className="mt-1.5 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-50"
              >
                <option value="ALL">All outcomes</option>
                {Array.from(new Set((data.benchmarks ?? []).map((row) => row.outcome).filter(Boolean))).sort().map((value) => <option key={value} value={value}>{value}</option>)}
              </select>
            </label>

            <label className="text-xs font-semibold text-slate-600">
              Evidence status
              <select
                value={evidenceFilter}
                onChange={(event) => setEvidenceFilter(event.target.value)}
                className="mt-1.5 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-50"
              >
                <option value="ALL">All evidence</option>
                {evidenceStatuses.map((value) => <option key={value} value={value}>{value}</option>)}
              </select>
            </label>

            <label className="text-xs font-semibold text-slate-600">
              Workload priority
              <select
                value={priorityFilter}
                onChange={(event) => setPriorityFilter(event.target.value)}
                className="mt-1.5 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-50"
              >
                <option value="ALL">All priorities</option>
                {priorities.map((value) => <option key={value} value={value}>{value}</option>)}
              </select>
            </label>
          </div>
        </div>

        {(selectedWorkloadFingerprint || recommendationFilter !== 'ALL' || outcomeFilter !== 'ALL' || evidenceFilter !== 'ALL' || priorityFilter !== 'ALL') && (
          <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-slate-100 pt-4 text-xs">
            <span className="font-bold uppercase tracking-[0.08em] text-slate-400">Active:</span>
            {selectedWorkloadFingerprint && <span className="rounded-full bg-blue-50 px-2.5 py-1 font-semibold text-blue-700">Workload {shortText(selectedWorkloadFingerprint, 18)}</span>}
            {recommendationFilter !== 'ALL' && <span className="rounded-full bg-blue-50 px-2.5 py-1 font-semibold text-blue-700">Recommendation #{recommendationFilter}</span>}
            {outcomeFilter !== 'ALL' && <span className="rounded-full bg-amber-50 px-2.5 py-1 font-semibold text-amber-700">Outcome {outcomeFilter}</span>}
            {evidenceFilter !== 'ALL' && <span className="rounded-full bg-violet-50 px-2.5 py-1 font-semibold text-violet-700">Evidence {evidenceFilter}</span>}
            {priorityFilter !== 'ALL' && <span className="rounded-full bg-slate-100 px-2.5 py-1 font-semibold text-slate-700">Priority {priorityFilter}</span>}
          </div>
        )}
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <div className="dashboard-card p-5">
          <SectionHeader
            eyebrow="Workload analytics"
            title="Total execution time by workload"
            question="Which stored workloads consume the most execution time?"
          />
          <HorizontalBars
            items={workloadBars}
            valueKey="total_execution_time_ms"
            labelKey="fingerprint"
            selectedLabel={selectedWorkloadFingerprint}
            onSelect={(item) => setSelectedWorkloadFingerprint((current) => current === item.fingerprint ? null : item.fingerprint)}
          />
        </div>

        <div className="dashboard-card p-5">
          <SectionHeader
            eyebrow="Workload analytics"
            title="Time-share concentration"
            question="How concentrated is the workload's execution-time share?"
          />
          <HorizontalBars items={timeShareBars} valueKey="value" labelKey="label" />
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <div className="dashboard-card p-5">
          <SectionHeader
            eyebrow="Recommendation outcomes"
            title="Benchmark outcome composition"
            question="What validation outcomes are represented in the currently selected evidence?"
            action={<span className="text-xs font-semibold text-slate-400">Click a segment to cross-filter</span>}
          />
          <OutcomeSegments
            items={outcomeSegments}
            selected={outcomeFilter === 'ALL' ? null : outcomeFilter}
            onSelect={(value) => setOutcomeFilter((current) => current === value ? 'ALL' : value)}
          />
        </div>

        <div className="dashboard-card p-5">
          <SectionHeader
            eyebrow="Recommendation outcomes"
            title="Evidence and decision states"
            question="Which evidence and production-decision states are connected to the selected recommendations?"
          />
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-xl bg-slate-50 p-4">
              <p className="text-[0.65rem] font-bold uppercase tracking-[0.12em] text-slate-400">Evidence</p>
              <div className="mt-3 space-y-2">
                {Array.from(new Set(filtered.provenance.map((row) => row.evidence_status).filter(Boolean))).map((status) => (
                  <button key={status} type="button" onClick={() => setEvidenceFilter((current) => current === status ? 'ALL' : status)} className="flex w-full items-center justify-between rounded-lg bg-white px-3 py-2 ring-1 ring-slate-200 hover:bg-violet-50">
                    <StatusBadge value={status} />
                    <span className="text-xs font-bold text-slate-700">{filtered.provenance.filter((row) => row.evidence_status === status).length}</span>
                  </button>
                ))}
              </div>
            </div>
            <div className="rounded-xl bg-slate-50 p-4">
              <p className="text-[0.65rem] font-bold uppercase tracking-[0.12em] text-slate-400">Decision</p>
              <div className="mt-3 space-y-2">
                {Array.from(new Set(filtered.decisions.map((row) => row.state).filter(Boolean))).map((state) => (
                  <div key={state} className="flex items-center justify-between rounded-lg bg-white px-3 py-2 ring-1 ring-slate-200">
                    <StatusBadge value={state} />
                    <span className="text-xs font-bold text-slate-700">{filtered.decisions.filter((row) => row.state === state).length}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="dashboard-card p-5">
        <SectionHeader
          eyebrow="Benchmark comparison"
          title="Baseline versus indexed execution time"
          question="Where does measured indexing change execution time, and by how much?"
          action={<span className="text-xs font-semibold text-slate-400">Click a benchmark for drill-down context</span>}
        />
        <BenchmarkComparison benchmarks={filtered.benchmarks} onSelect={(item) => setRecommendationFilter(item.recommendation_id == null ? 'ALL' : String(item.recommendation_id))} />
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <div className="dashboard-card p-5">
          <SectionHeader
            eyebrow="Cost-benefit analysis"
            title="Read improvement versus storage ratio"
            question="How does measured read benefit relate to index storage footprint?"
          />
          <CostBenefitScatter items={filtered.costBenefits} onSelect={(item) => setRecommendationFilter(item.recommendation_id == null ? 'ALL' : String(item.recommendation_id))} />
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {filtered.costBenefits.map((item) => (
              <div key={`write-${item.experiment_id}`} className="rounded-xl bg-slate-50 p-3">
                <p className="text-[0.63rem] font-bold uppercase tracking-[0.08em] text-slate-400">Write overhead · #{item.recommendation_id ?? '—'}</p>
                <p className="mt-1 text-sm font-bold text-slate-700">{formatPercent(item.write?.average_overhead_percent)}</p>
                <p className="mt-1 text-xs text-slate-500">Absolute: {formatNumber(item.write?.absolute_overhead_ms)} ms</p>
              </div>
            ))}
          </div>
        </div>

        <div className="dashboard-card p-5">
          <SectionHeader
            eyebrow="Composite indexes"
            title="Measured column-order effects"
            question="Does changing composite-index column order alter the measured improvement?"
          />
          <CompositeOrderComparison items={filtered.compositeIndexes} onSelect={(item) => setRecommendationFilter(String(item.recommendation_id))} />
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.35fr_0.65fr]">
        <div className="dashboard-card p-5">
          <SectionHeader
            eyebrow="Query-plan analytics"
            title="Execution-plan evidence summary"
            question="Which profiled queries show sequential scans, index scans, joins, and index-condition usage?"
          />
          <div className="space-y-3">
            {filtered.queries.slice().sort((a, b) => Number(b.total_execution_time_ms ?? 0) - Number(a.total_execution_time_ms ?? 0)).slice(0, 6).map((query) => (
              <QueryPlanSummary key={query.query_profile_id} query={query} onSelect={(item) => setSelectedQueryId((current) => current === item.query_profile_id ? null : item.query_profile_id)} />
            ))}
            {filtered.queries.length === 0 && <p className="rounded-xl bg-slate-50 p-5 text-sm text-slate-500">No query profiles match the current filters.</p>}
          </div>
        </div>

        <div className="dashboard-card p-5">
          <SectionHeader
            eyebrow="Selected query"
            title="Query context"
            question="Use the selected query to inspect the evidence links currently available."
          />
          {selectedQuery ? (
            <div className="space-y-4">
              <div className="rounded-xl bg-slate-950 p-4 text-xs leading-6 text-slate-100">
                <p className="mb-2 text-[0.65rem] font-bold uppercase tracking-[0.12em] text-slate-400">SQL</p>
                <pre className="overflow-x-auto whitespace-pre-wrap">{selectedQuery.query_text}</pre>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <MetricCard label="Rows processed" value={formatNumber(selectedQuery.rows_processed, 0)} />
                <MetricCard label="Recommendations" value={selectedQuery.recommendation_ids.length} />
              </div>
            </div>
          ) : (
            <p className="rounded-xl bg-slate-50 p-5 text-sm text-slate-500">Select a query profile to inspect it here.</p>
          )}
        </div>
      </section>

      <section className="dashboard-card p-5">
        <SectionHeader
          eyebrow="Optimization journey"
          title="Query → candidate → benchmark → decision → provenance"
          question="How far does the selected recommendation travel through the evidence chain?"
          action={selectedRecommendation ? <span className="text-xs font-bold text-blue-600">Recommendation #{selectedRecommendation}</span> : null}
        />

        {journey ? (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <JourneyStep number="1" title="Query context" complete={Boolean(journey.query)} active={Boolean(journey.query)} detail={journey.query ? `Linked query #${journey.query.query_profile_id}` : 'No linked query profile found'} />
            <JourneyStep number="2" title="Candidate" complete active detail={`Recommendation #${journey.recommendationId} is present in the evidence graph`} />
            <JourneyStep number="3" title="Benchmark" complete={journey.benchmarks.length > 0} active={journey.benchmarks.length > 0} detail={journey.benchmarks.length ? `${journey.benchmarks.length} benchmark record(s)` : 'No benchmark record linked'} />
            <JourneyStep number="4" title="Cost & benefit" complete={journey.costs.length > 0} active={journey.costs.length > 0} detail={journey.costs.length ? `${journey.costs.length} linked cost-benefit record(s)` : 'No linked cost-benefit record'} />
            <JourneyStep number="5" title="Production decision" complete={journey.decisions.length > 0} active={journey.decisions.length > 0} detail={journey.decisions.length ? journey.decisions.map((item) => item.state).join(', ') : 'No linked production decision'} />
            <JourneyStep number="6" title="Provenance" complete={journey.provenance.length > 0} active={journey.provenance.length > 0} detail={journey.provenance.length ? `${journey.provenance.length} provenance record(s)` : 'No provenance record linked'} />
          </div>
        ) : (
          <p className="rounded-xl bg-slate-50 p-5 text-sm text-slate-500">
            Select a recommendation, workload, benchmark, or evidence item to populate the optimization journey.
          </p>
        )}
      </section>
    </div>
  )
}

export default InteractiveAnalyticsPage

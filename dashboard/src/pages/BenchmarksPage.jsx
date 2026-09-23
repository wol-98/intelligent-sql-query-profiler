import { useEffect, useMemo, useState } from 'react'

import { getBenchmarks } from '../api/client'
import BenchmarkTable from '../components/benchmarks/BenchmarkTable'
import KpiCard from '../components/ui/KpiCard'
import BenchmarkDetail from '../components/benchmarks/BenchmarkDetail'

function OutcomeComposition({ summary }) {
  const total = summary.total || 1

  const outcomes = [
    {
      label: 'Successful',
      value: summary.successful,
      accent: 'bg-emerald-500',
      text: 'text-emerald-700',
      soft: 'bg-emerald-50',
      border: 'border-emerald-100',
    },
    {
      label: 'Neutral',
      value: summary.neutral,
      accent: 'bg-slate-400',
      text: 'text-slate-700',
      soft: 'bg-slate-50',
      border: 'border-slate-200',
    },
    {
      label: 'Unsuccessful',
      value: summary.unsuccessful,
      accent: 'bg-rose-500',
      text: 'text-rose-700',
      soft: 'bg-rose-50',
      border: 'border-rose-100',
    },
  ]

  return (
    <section className="dashboard-panel overflow-hidden">
      <div className="border-b border-slate-200/80 bg-gradient-to-r from-white via-slate-50/60 to-blue-50/30 px-6 py-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="section-eyebrow section-eyebrow-violet">
              Outcome composition
            </p>

            <h2 className="mt-1 text-lg font-semibold text-slate-950">
              Validation outcome mix
            </h2>

            <p className="mt-1 max-w-2xl text-xs leading-5 text-slate-500">
              Distribution of stored benchmark validation outcomes.
            </p>
          </div>

          <span className="status-badge status-badge-muted">
            {summary.total} total
          </span>
        </div>
      </div>

      <div className="grid gap-3 p-5 lg:grid-cols-3">
        {outcomes.map((item) => {
          const percentage = (item.value / total) * 100

          return (
            <div
              key={item.label}
              className={`rounded-2xl border p-4 ${item.soft} ${item.border}`}
            >
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span
                    className={`h-2.5 w-2.5 rounded-full ${item.accent}`}
                  />

                  <span className="text-sm font-semibold text-slate-800">
                    {item.label}
                  </span>
                </div>

                <span className={`text-sm font-bold ${item.text}`}>
                  {item.value}
                </span>
              </div>

              <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/80">
                <div
                  className={`h-full rounded-full ${item.accent} transition-all duration-500`}
                  style={{ width: `${percentage}%` }}
                />
              </div>

              <div className="mt-2 flex items-center justify-between">
                <span className="text-[10px] font-medium uppercase tracking-[0.12em] text-slate-400">
                  Share of benchmarks
                </span>

                <span className={`text-xs font-bold ${item.text}`}>
                  {percentage.toFixed(2)}%
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}

function EvidenceExplorer({
  search,
  setSearch,
  outcome,
  setOutcome,
  outcomes,
  filteredCount,
  totalCount,
}) {
  const filtersActive = search.trim() || outcome !== 'ALL'

  return (
    <section className="dashboard-panel overflow-hidden">
      <div className="border-b border-slate-200/80 bg-white px-6 py-5">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <p className="section-eyebrow section-eyebrow-blue">
              Evidence explorer
            </p>

            <h2 className="mt-1 text-lg font-semibold text-slate-950">
              Find a stored benchmark
            </h2>

            <p className="mt-1 text-xs leading-5 text-slate-500">
              Search benchmark identifiers and stored experimental metadata.
            </p>
          </div>

          <span className="status-badge status-badge-info">
            {filteredCount} of {totalCount} shown
          </span>
        </div>
      </div>

      <div className="grid gap-4 p-5 xl:grid-cols-[1fr_220px]">
        <div>
          <label
            htmlFor="benchmark-search"
            className="mb-2 block text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400"
          >
            Search evidence
          </label>

          <div className="relative">
            <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-sm text-slate-400">
              ⌕
            </span>

            <input
              id="benchmark-search"
              type="text"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Benchmark ID, recommendation, experiment, scope..."
              className="w-full rounded-xl border border-slate-200 bg-slate-50/70 py-3.5 pl-10 pr-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-300 focus:bg-white focus:ring-4 focus:ring-blue-50"
            />
          </div>
        </div>

        <div>
          <label
            htmlFor="benchmark-outcome"
            className="mb-2 block text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400"
          >
            Validation outcome
          </label>

          <select
            id="benchmark-outcome"
            value={outcome}
            onChange={(event) => setOutcome(event.target.value)}
            className="w-full rounded-xl border border-slate-200 bg-slate-50/70 px-3 py-3.5 text-sm text-slate-700 outline-none transition focus:border-blue-300 focus:bg-white focus:ring-4 focus:ring-blue-50"
          >
            {outcomes.map((value) => (
              <option key={value} value={value}>
                {value === 'ALL' ? 'All outcomes' : value}
              </option>
            ))}
          </select>
        </div>
      </div>

      {filtersActive && (
        <div className="flex items-center justify-between gap-3 border-t border-slate-100 bg-slate-50/50 px-5 py-3">
          <p className="text-xs text-slate-500">
            Active filters are narrowing the stored evidence inventory.
          </p>

          <button
            type="button"
            onClick={() => {
              setSearch('')
              setOutcome('ALL')
            }}
            className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
          >
            Clear filters
          </button>
        </div>
      )}
    </section>
  )
}

function BenchmarksPage({ onNavigateToRecommendation }) {
  const [benchmarks, setBenchmarks] = useState([])
  const [selectedBenchmarkId, setSelectedBenchmarkId] =
    useState(null)
  const [search, setSearch] = useState('')
  const [outcome, setOutcome] = useState('ALL')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false

    async function loadBenchmarks() {
      try {
        setLoading(true)
        setError(null)

        const data = await getBenchmarks()

        if (!cancelled) {
          setBenchmarks(data)

          if (data.length > 0) {
            setSelectedBenchmarkId(data[0].benchmark_id)
          }
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.message || 'Failed to load benchmarks.'
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadBenchmarks()

    return () => {
      cancelled = true
    }
  }, [])

  const outcomes = useMemo(() => {
    return [
      'ALL',
      ...Array.from(
        new Set(
          benchmarks
            .map((benchmark) => benchmark.outcome)
            .filter(Boolean)
        )
      ).sort(),
    ]
  }, [benchmarks])

  const filteredBenchmarks = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase()

    return benchmarks.filter((benchmark) => {
      const matchesOutcome =
        outcome === 'ALL' ||
        benchmark.outcome === outcome

      if (!normalizedSearch) {
        return matchesOutcome
      }

      const searchable = [
        benchmark.benchmark_id,
        benchmark.recommendation_id,
        benchmark.experiment_id,
        benchmark.scope,
        benchmark.outcome,
      ]
        .filter(
          (value) =>
            value !== null &&
            value !== undefined
        )
        .join(' ')
        .toLowerCase()

      return (
        matchesOutcome &&
        searchable.includes(normalizedSearch)
      )
    })
  }, [benchmarks, search, outcome])

  const selectedBenchmark = useMemo(() => {
    return (
      benchmarks.find(
        (benchmark) =>
          benchmark.benchmark_id === selectedBenchmarkId
      ) || null
    )
  }, [benchmarks, selectedBenchmarkId])

  const summary = useMemo(() => {
    const successful = benchmarks.filter(
      (benchmark) => benchmark.outcome === 'SUCCESS'
    ).length

    const neutral = benchmarks.filter(
      (benchmark) => benchmark.outcome === 'NEUTRAL'
    ).length

    const unsuccessful = benchmarks.filter(
      (benchmark) =>
        benchmark.outcome === 'UNSUCCESSFUL'
    ).length

    return {
      total: benchmarks.length,
      successful,
      neutral,
      unsuccessful,
    }
  }, [benchmarks])

  function handleRecommendationSelect(recommendationId) {
    if (onNavigateToRecommendation) {
      onNavigateToRecommendation(recommendationId)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <section className="dashboard-hero">
          <p className="section-eyebrow section-eyebrow-blue">
            Evaluation intelligence
          </p>

          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
            Benchmark evidence
          </h1>

          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
            Explore stored execution measurements, validation outcomes,
            and recommendation-linked benchmark evidence.
          </p>
        </section>

        <div className="dashboard-panel flex min-h-64 items-center justify-center">
          <div className="text-center">
            <div className="mx-auto h-8 w-8 animate-pulse rounded-full bg-blue-100" />

            <p className="mt-4 text-sm font-semibold text-slate-700">
              Loading benchmark evidence
            </p>

            <p className="mt-1 text-xs text-slate-400">
              Retrieving stored validation measurements...
            </p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <section className="dashboard-hero">
          <p className="section-eyebrow section-eyebrow-blue">
            Evaluation intelligence
          </p>

          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
            Benchmark evidence
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            Explore stored benchmark and validation evidence.
          </p>
        </section>

        <div className="rounded-2xl border border-rose-200 bg-rose-50 p-6">
          <div className="flex items-start gap-3">
            <span className="mt-1 h-2.5 w-2.5 rounded-full bg-rose-500" />

            <div>
              <p className="text-sm font-semibold text-rose-800">
                Unable to load benchmarks.
              </p>

              <p className="mt-1 text-xs leading-5 text-rose-700">
                {error}
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-7">
      <section className="dashboard-hero">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="section-eyebrow section-eyebrow-cyan">
              Evaluation intelligence
            </p>

            <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
              Benchmark evidence
            </h1>

            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
              Explore stored execution measurements, validation outcomes,
              and recommendation-linked experimental evidence.
            </p>

            <div className="mt-5 flex flex-wrap gap-2">
              <span className="status-badge status-badge-info">
                Stored evidence
              </span>

              <span className="status-badge status-badge-muted">
                Read-only reporting
              </span>

              <span className="status-badge status-badge-muted">
                {summary.total} benchmark records
              </span>
            </div>
          </div>

          <div className="relative overflow-hidden rounded-2xl border border-blue-100 bg-gradient-to-br from-white via-blue-50/60 to-cyan-50/60 px-6 py-5 shadow-sm">
            <div className="absolute -right-8 -top-8 h-24 w-24 rounded-full bg-blue-200/30 blur-2xl" />

            <div className="relative">
              <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-blue-500">
                Inventory
              </p>

              <p className="mt-1 text-3xl font-bold tracking-tight text-slate-950">
                {summary.total}
              </p>

              <p className="text-xs text-slate-500">
                stored benchmarks
              </p>

              <div className="mt-4 h-px w-20 bg-blue-200" />

              <p className="mt-3 text-[10px] font-medium uppercase tracking-[0.12em] text-slate-400">
                Validation records
              </p>
            </div>
          </div>
        </div>
      </section>

      <section>
        <div className="mb-3">
          <p className="section-eyebrow section-eyebrow-blue">
            Validation snapshot
          </p>

          <h2 className="mt-1 text-xl font-semibold text-slate-950">
            Benchmark activity
          </h2>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            Current stored benchmark outcomes reported by the validation API.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <KpiCard
            label="Total benchmarks"
            value={summary.total}
            description="Stored benchmark records"
            meta="100.00%"
            tone="default"
          />

          <KpiCard
            label="Successful"
            value={summary.successful}
            description="Successful validation outcomes"
            meta={
              summary.total
                ? `${((summary.successful / summary.total) * 100).toFixed(2)}%`
                : '0.00%'
            }
            tone="success"
          />

          <KpiCard
            label="Neutral"
            value={summary.neutral}
            description="Neutral validation outcomes"
            meta={
              summary.total
                ? `${((summary.neutral / summary.total) * 100).toFixed(2)}%`
                : '0.00%'
            }
            tone="neutral"
          />

          <KpiCard
            label="Unsuccessful"
            value={summary.unsuccessful}
            description="Unsuccessful validation outcomes"
            meta={
              summary.total
                ? `${((summary.unsuccessful / summary.total) * 100).toFixed(2)}%`
                : '0.00%'
            }
            tone="danger"
          />
        </div>
      </section>

      <OutcomeComposition summary={summary} />

      <EvidenceExplorer
        search={search}
        setSearch={setSearch}
        outcome={outcome}
        setOutcome={setOutcome}
        outcomes={outcomes}
        filteredCount={filteredBenchmarks.length}
        totalCount={benchmarks.length}
      />

      <BenchmarkTable
        benchmarks={filteredBenchmarks}
        selectedBenchmarkId={selectedBenchmarkId}
        onSelect={(benchmark) =>
          setSelectedBenchmarkId(benchmark.benchmark_id)
        }
      />

      <BenchmarkDetail
        benchmark={selectedBenchmark}
        onRecommendationSelect={
          handleRecommendationSelect
        }
      />
    </div>
  )
}

export default BenchmarksPage

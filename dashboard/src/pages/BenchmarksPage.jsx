import { useEffect, useMemo, useState } from 'react'
import { getBenchmarks } from '../api/client'
import BenchmarkTable from '../components/benchmarks/BenchmarkTable'
import BenchmarkDetail from '../components/benchmarks/BenchmarkDetail'

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
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">
            Benchmarks
          </h1>

          <p className="mt-1 text-sm text-slate-500">
            Loading stored benchmark evidence...
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-8">
          <p className="text-sm text-slate-500">
            Loading benchmark results...
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">
            Benchmarks
          </h1>

          <p className="mt-1 text-sm text-slate-500">
            Explore stored benchmark and validation evidence.
          </p>
        </div>

        <div className="rounded-xl border border-red-200 bg-red-50 p-6">
          <p className="text-sm font-medium text-red-800">
            Unable to load benchmarks.
          </p>

          <p className="mt-1 text-sm text-red-700">
            {error}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">
          Benchmarks
        </h1>

        <p className="mt-1 text-sm text-slate-500">
          Explore stored benchmark and validation evidence.
        </p>
      </div>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Total Benchmarks
          </p>

          <p className="mt-2 text-2xl font-semibold text-slate-900">
            {summary.total}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Successful
          </p>

          <p className="mt-2 text-2xl font-semibold text-slate-900">
            {summary.successful}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Neutral
          </p>

          <p className="mt-2 text-2xl font-semibold text-slate-900">
            {summary.neutral}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Unsuccessful
          </p>

          <p className="mt-2 text-2xl font-semibold text-slate-900">
            {summary.unsuccessful}
          </p>
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-5">
        <div className="flex flex-col gap-4 md:flex-row">
          <div className="flex-1">
            <label
              htmlFor="benchmark-search"
              className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500"
            >
              Search
            </label>

            <input
              id="benchmark-search"
              type="text"
              value={search}
              onChange={(event) =>
                setSearch(event.target.value)
              }
              placeholder="Search benchmark or recommendation ID..."
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-500 focus:ring-1 focus:ring-slate-500"
            />
          </div>

          <div className="md:w-52">
            <label
              htmlFor="benchmark-outcome"
              className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500"
            >
              Outcome
            </label>

            <select
              id="benchmark-outcome"
              value={outcome}
              onChange={(event) =>
                setOutcome(event.target.value)
              }
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-500 focus:ring-1 focus:ring-slate-500"
            >
              {outcomes.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </div>
        </div>
      </section>

      <BenchmarkTable
        benchmarks={filteredBenchmarks}
        selectedBenchmarkId={selectedBenchmarkId}
        onSelect={(benchmark) =>
          setSelectedBenchmarkId(
            benchmark.benchmark_id
          )
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

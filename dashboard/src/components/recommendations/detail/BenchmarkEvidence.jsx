import { useEffect, useMemo, useState } from 'react'

import { getBenchmarks } from '../../../api/client'

function formatNumber(value, digits = 2) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return Number(value).toFixed(digits)
}

function Metric({ label, value }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </p>

      <p className="mt-1 text-sm font-semibold text-slate-900">
        {value}
      </p>
    </div>
  )
}

function BooleanMetric({ label, value }) {
  let display = 'Not available'

  if (value === true) {
    display = 'Yes'
  } else if (value === false) {
    display = 'No'
  }

  return <Metric label={label} value={display} />
}

function OutcomeBadge({ value }) {
  if (!value) {
    return (
      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-500">
        Not available
      </span>
    )
  }

  const styles = {
    SUCCESS: 'bg-green-50 text-green-700',
    NEUTRAL: 'bg-slate-100 text-slate-700',
    UNSUCCESSFUL: 'bg-red-50 text-red-700',
    UNSAFE: 'bg-red-50 text-red-700',
  }

  return (
    <span
      className={`rounded-full px-3 py-1 text-xs font-semibold ${
        styles[value] || 'bg-slate-100 text-slate-700'
      }`}
    >
      {value}
    </span>
  )
}

function BenchmarkCard({ benchmark, onViewBenchmark }) {
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Benchmark Evidence
          </p>

          <h4 className="mt-1 text-base font-semibold text-slate-900">
            Benchmark #{benchmark.benchmark_id}
          </h4>
        </div>

        <OutcomeBadge value={benchmark.outcome} />
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric
          label="Baseline"
          value={
            benchmark.baseline_time_ms === null ||
            benchmark.baseline_time_ms === undefined
              ? 'Not available'
              : `${formatNumber(benchmark.baseline_time_ms)} ms`
          }
        />

        <Metric
          label="Indexed"
          value={
            benchmark.indexed_time_ms === null ||
            benchmark.indexed_time_ms === undefined
              ? 'Not available'
              : `${formatNumber(benchmark.indexed_time_ms)} ms`
          }
        />

        <Metric
          label="Improvement"
          value={
            benchmark.improvement_percent === null ||
            benchmark.improvement_percent === undefined
              ? 'Not available'
              : `${formatNumber(benchmark.improvement_percent)}%`
          }
        />

        <Metric
          label="Savings"
          value={
            benchmark.savings_ms === null ||
            benchmark.savings_ms === undefined
              ? 'Not available'
              : `${formatNumber(benchmark.savings_ms)} ms`
          }
        />
      </div>

      <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric
          label="Median Improvement"
          value={
            benchmark.median_improvement_percent === null ||
            benchmark.median_improvement_percent === undefined
              ? 'Not available'
              : `${formatNumber(
                  benchmark.median_improvement_percent
                )}%`
          }
        />

        <BooleanMetric
          label="Rows Preserved"
          value={benchmark.rows_preserved}
        />

        <BooleanMetric
          label="Index Used"
          value={benchmark.index_used}
        />

        <BooleanMetric
          label="Plan Changed"
          value={benchmark.plan_changed}
        />
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-slate-500">
        <span>
          Scope:{' '}
          <span className="font-medium text-slate-700">
            {benchmark.scope || 'Not available'}
          </span>
        </span>

        <span>
          Experiment:{' '}
          <span className="font-medium text-slate-700">
            {benchmark.experiment_id || 'Not available'}
          </span>
        </span>
      </div>

      <button
        type="button"
        onClick={() => onViewBenchmark(benchmark.benchmark_id)}
        className="mt-5 rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-sm font-medium text-blue-700 transition hover:bg-blue-100"
      >
        View benchmark evidence
      </button>
    </article>
  )
}

function BenchmarkEvidence({
  recommendation,
  onViewBenchmark,
}) {
  const [benchmarks, setBenchmarks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true

    async function loadBenchmarks() {
      try {
        setLoading(true)
        setError(null)

        const data = await getBenchmarks()

        if (mounted) {
          setBenchmarks(data)
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

    loadBenchmarks()

    return () => {
      mounted = false
    }
  }, [])

  const matchingBenchmarks = useMemo(() => {
    return benchmarks.filter(
      (benchmark) =>
        benchmark.recommendation_id === recommendation.recommendation_id
    )
  }, [benchmarks, recommendation.recommendation_id])

  if (loading) {
    return (
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-base font-semibold text-slate-900">
          Benchmark Evidence
        </h3>

        <p className="mt-2 text-sm text-slate-500">
          Loading stored benchmark evidence...
        </p>
      </section>
    )
  }

  if (error) {
    return (
      <section className="rounded-xl border border-red-200 bg-white p-6 shadow-sm">
        <h3 className="text-base font-semibold text-slate-900">
          Benchmark Evidence
        </h3>

        <p className="mt-2 text-sm text-slate-500">
          The stored benchmark evidence could not be retrieved.
        </p>

        <p className="mt-2 text-xs text-red-600">{error}</p>
      </section>
    )
  }

  if (matchingBenchmarks.length === 0) {
    return (
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Benchmark Evidence
          </p>

          <h3 className="mt-1 text-base font-semibold text-slate-900">
            No stored benchmark evidence
          </h3>
        </div>

        <p className="mt-2 text-sm leading-6 text-slate-500">
          No stored benchmark record is linked to recommendation #
          {recommendation.recommendation_id}.
        </p>

        <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Evidence Boundary
          </p>

          <p className="mt-2 text-sm leading-6 text-slate-600">
            Missing benchmark evidence is reported as unavailable. It is not
            treated as zero and does not create a new validation or production
            decision.
          </p>
        </div>
      </section>
    )
  }

  return (
    <section className="space-y-4">
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Benchmark Evidence
        </p>

        <h3 className="mt-1 text-base font-semibold text-slate-900">
          Stored validation benchmarks
        </h3>

        <p className="mt-1 text-sm text-slate-500">
          {matchingBenchmarks.length} stored benchmark{' '}
          {matchingBenchmarks.length === 1 ? 'record' : 'records'} linked to
          this recommendation.
        </p>
      </div>

      {matchingBenchmarks.map((benchmark) => (
        <BenchmarkCard
          key={benchmark.benchmark_id}
          benchmark={benchmark}
          onViewBenchmark={onViewBenchmark}
        />
      ))}

      <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Evidence Boundary
        </p>

        <p className="mt-2 text-sm leading-6 text-slate-600">
          This section reports stored benchmark evidence. It does not rerun
          benchmarks, create or remove indexes, recalculate validation
          outcomes, or make production decisions.
        </p>
      </div>
    </section>
  )
}

export default BenchmarkEvidence

import { useEffect, useMemo, useState } from 'react'

import { getBenchmarks } from '../../../api/client'
import StatusBadge from '../../common/StatusBadge'

function formatNumber(value, digits = 2) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return Number(value).toFixed(digits)
}

function Metric({ label, value }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50/65 p-3.5 transition-colors hover:border-slate-300 hover:bg-slate-50">
      <p className="text-[0.62rem] font-bold uppercase tracking-[0.08em] text-slate-400">
        {label}
      </p>

      <p className="mt-2 break-words text-sm font-semibold leading-5 text-slate-800">
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

function BenchmarkCard({ benchmark, onViewBenchmark }) {
  return (
    <article className="dashboard-card-interactive rounded-xl border border-slate-200 bg-white p-5">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-[0.65rem] font-bold uppercase tracking-[0.1em] text-cyan-600">
            Stored benchmark
          </p>

          <h4 className="mt-1 text-base font-bold tracking-[-0.01em] text-slate-950">
            Benchmark #{benchmark.benchmark_id}
          </h4>
        </div>

        <StatusBadge value={benchmark.outcome} />
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
          label="Median improvement"
          value={
            benchmark.median_improvement_percent === null ||
            benchmark.median_improvement_percent === undefined
              ? 'Not available'
              : `${formatNumber(
                  benchmark.median_improvement_percent,
                )}%`
          }
        />

        <BooleanMetric
          label="Rows preserved"
          value={benchmark.rows_preserved}
        />

        <BooleanMetric
          label="Index used"
          value={benchmark.index_used}
        />

        <BooleanMetric
          label="Plan changed"
          value={benchmark.plan_changed}
        />
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-slate-500">
        <span>
          Scope:{' '}
          <span className="font-semibold text-slate-700">
            {benchmark.scope || 'Not available'}
          </span>
        </span>

        <span>
          Experiment:{' '}
          <span className="font-semibold text-slate-700">
            {benchmark.experiment_id || 'Not available'}
          </span>
        </span>
      </div>

      <button
        type="button"
        onClick={() => onViewBenchmark(benchmark.benchmark_id)}
        className="dashboard-focus mt-5 rounded-xl border border-blue-200 bg-blue-50 px-3.5 py-2.5 text-xs font-bold text-blue-700 transition hover:border-blue-300 hover:bg-blue-100"
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
        benchmark.recommendation_id ===
        recommendation.recommendation_id,
    )
  }, [benchmarks, recommendation.recommendation_id])

  if (loading) {
    return (
      <section className="dashboard-card p-6">
        <div className="flex items-center gap-3">
          <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-500" />

          <div>
            <p className="text-[0.65rem] font-bold uppercase tracking-[0.1em] text-cyan-600">
              03 · Stored benchmark evidence
            </p>

            <h3 className="mt-1 text-base font-bold text-slate-950">
              Loading benchmark evidence
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Loading stored benchmark evidence...
            </p>
          </div>
        </div>
      </section>
    )
  }

  if (error) {
    return (
      <section className="rounded-2xl border border-rose-200 bg-white p-6 shadow-sm">
        <div className="flex items-start gap-3">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-rose-50 font-bold text-rose-600">
            !
          </span>

          <div>
            <p className="text-[0.65rem] font-bold uppercase tracking-[0.1em] text-rose-600">
              03 · Stored benchmark evidence
            </p>

            <h3 className="mt-1 text-base font-bold text-slate-950">
              Benchmark evidence unavailable
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              The stored benchmark evidence could not be retrieved.
            </p>

            <p className="mt-3 rounded-lg bg-rose-50 px-3 py-2 text-xs text-rose-700">
              {error}
            </p>
          </div>
        </div>
      </section>
    )
  }

  if (matchingBenchmarks.length === 0) {
    return (
      <section className="dashboard-card p-6">
        <div>
          <p className="text-[0.65rem] font-bold uppercase tracking-[0.1em] text-cyan-600">
            03 · Stored benchmark evidence
          </p>

          <h3 className="mt-1 text-base font-bold text-slate-950">
            No stored benchmark evidence
          </h3>

          <p className="mt-1 text-sm leading-6 text-slate-500">
            No stored benchmark record is linked to recommendation #
            {recommendation.recommendation_id}.
          </p>
        </div>

        <div className="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-4">
          <p className="text-[0.62rem] font-bold uppercase tracking-[0.08em] text-slate-500">
            Evidence boundary
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
      <div className="dashboard-card p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-[0.65rem] font-bold uppercase tracking-[0.1em] text-cyan-600">
              03 · Stored benchmark evidence
            </p>

            <h3 className="mt-1 text-base font-bold tracking-[-0.01em] text-slate-950">
              Stored validation benchmarks
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              {matchingBenchmarks.length} stored benchmark{' '}
              {matchingBenchmarks.length === 1
                ? 'record'
                : 'records'}{' '}
              linked to this recommendation.
            </p>
          </div>

          <div className="rounded-lg bg-cyan-50 px-2.5 py-1.5 text-[0.62rem] font-bold uppercase tracking-[0.06em] text-cyan-700">
            Evidence
          </div>
        </div>
      </div>

      {matchingBenchmarks.map((benchmark) => (
        <BenchmarkCard
          key={benchmark.benchmark_id}
          benchmark={benchmark}
          onViewBenchmark={onViewBenchmark}
        />
      ))}

      <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">
        <p className="text-[0.62rem] font-bold uppercase tracking-[0.08em] text-slate-500">
          Evidence boundary
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

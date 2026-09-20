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

function BenchmarkDetail({
  benchmark,
  onRecommendationSelect,
}) {
  if (!benchmark) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8">
        <p className="text-sm text-slate-500">
          Select a benchmark to inspect its evidence.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-slate-200 bg-white p-6">
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Benchmark Evidence
            </p>

            <h2 className="mt-1 text-xl font-semibold text-slate-900">
              Benchmark #{benchmark.benchmark_id}
            </h2>
          </div>

          <OutcomeBadge value={benchmark.outcome} />
        </div>
      </section>

      <section>
        <h3 className="mb-3 text-base font-semibold text-slate-900">
          Performance
        </h3>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
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
      </section>

      <section>
        <h3 className="mb-3 text-base font-semibold text-slate-900">
          Validation Evidence
        </h3>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
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
        </div>
      </section>

      <section>
        <h3 className="mb-3 text-base font-semibold text-slate-900">
          Benchmark Identity
        </h3>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <Metric
            label="Benchmark ID"
            value={benchmark.benchmark_id}
          />

          <Metric
            label="Recommendation"
            value={
              benchmark.recommendation_id === null ||
              benchmark.recommendation_id === undefined
                ? 'Not available'
                : `#${benchmark.recommendation_id}`
            }
          />

          <Metric
            label="Experiment ID"
            value={benchmark.experiment_id || 'Not available'}
          />
        </div>
      </section>

      {benchmark.recommendation_id !== null &&
        benchmark.recommendation_id !== undefined && (
          <section className="rounded-xl border border-slate-200 bg-white p-6">
            <h3 className="text-base font-semibold text-slate-900">
              Associated Recommendation
            </h3>

            <button
              type="button"
              onClick={() =>
                onRecommendationSelect(
                  benchmark.recommendation_id
                )
              }
              className="mt-4 rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-sm font-medium text-blue-700 transition hover:bg-blue-100"
            >
              Open Recommendation #{benchmark.recommendation_id}
            </button>
          </section>
        )}

      <section className="rounded-xl border border-slate-200 bg-slate-50 p-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Evidence Boundary
        </p>

        <p className="mt-2 text-sm leading-6 text-slate-600">
          This page reports stored benchmark evidence. It does not
          rerun benchmarks, create or remove indexes, or make new
          production decisions.
        </p>
      </section>
    </div>
  )
}

export default BenchmarkDetail

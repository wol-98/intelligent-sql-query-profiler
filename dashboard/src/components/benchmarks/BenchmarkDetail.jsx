import StatusBadge from '../common/StatusBadge'

function formatNumber(value, digits = 2) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return Number(value).toFixed(digits)
}

function Metric({
  label,
  value,
  accent = 'default',
  mono = false,
}) {
  const accentClasses = {
    default: 'border-slate-200 bg-slate-50/70',
    blue: 'border-blue-100 bg-blue-50/50',
    green: 'border-emerald-100 bg-emerald-50/50',
    violet: 'border-violet-100 bg-violet-50/50',
  }

  return (
    <div
      className={`rounded-2xl border p-4 ${
        accentClasses[accent] || accentClasses.default
      }`}
    >
      <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">
        {label}
      </p>

      <p
        className={`mt-2 text-sm font-semibold text-slate-900 ${
          mono ? 'font-mono text-xs' : ''
        }`}
      >
        {value}
      </p>
    </div>
  )
}

function BooleanMetric({ label, value }) {
  let display = 'Not available'
  let className = 'text-slate-500'
  let dotClass = 'bg-slate-300'

  if (value === true) {
    display = 'Yes'
    className = 'text-emerald-700'
    dotClass = 'bg-emerald-500'
  } else if (value === false) {
    display = 'No'
    className = 'text-rose-700'
    dotClass = 'bg-rose-500'
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4">
      <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">
        {label}
      </p>

      <div className="mt-2 flex items-center gap-2">
        <span className={`h-2 w-2 rounded-full ${dotClass}`} />

        <p className={`text-sm font-semibold ${className}`}>
          {display}
        </p>
      </div>
    </div>
  )
}

function PerformanceComparison({ benchmark }) {
  const baseline =
    benchmark.baseline_time_ms !== null &&
    benchmark.baseline_time_ms !== undefined
      ? `${formatNumber(benchmark.baseline_time_ms)} ms`
      : 'Not available'

  const indexed =
    benchmark.indexed_time_ms !== null &&
    benchmark.indexed_time_ms !== undefined
      ? `${formatNumber(benchmark.indexed_time_ms)} ms`
      : 'Not available'

  const improvement =
    benchmark.improvement_percent !== null &&
    benchmark.improvement_percent !== undefined
      ? `${formatNumber(benchmark.improvement_percent)}%`
      : 'Not available'

  const savings =
    benchmark.savings_ms !== null &&
    benchmark.savings_ms !== undefined
      ? `${formatNumber(benchmark.savings_ms)} ms`
      : 'Not available'

  const numericImprovement =
    benchmark.improvement_percent !== null &&
    benchmark.improvement_percent !== undefined
      ? Number(benchmark.improvement_percent)
      : null

  const improvementClass =
    numericImprovement === null
      ? 'text-slate-500'
      : numericImprovement > 0
        ? 'text-emerald-600'
        : numericImprovement < 0
          ? 'text-rose-600'
          : 'text-slate-600'

  return (
    <section className="dashboard-panel overflow-hidden">
      <div className="border-b border-slate-200/80 bg-gradient-to-r from-white via-blue-50/40 to-cyan-50/30 px-6 py-5">
        <p className="section-eyebrow section-eyebrow-blue">
          Performance comparison
        </p>

        <h3 className="mt-1 text-lg font-semibold text-slate-950">
          Baseline versus indexed execution
        </h3>

        <p className="mt-1 text-xs leading-5 text-slate-500">
          Stored execution measurements reported by the benchmark evidence.
        </p>
      </div>

      <div className="p-5">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="relative overflow-hidden rounded-2xl border border-slate-200 bg-slate-50 p-5">
            <div className="absolute right-0 top-0 h-20 w-20 rounded-full bg-slate-200/40 blur-2xl" />

            <div className="relative">
              <div className="flex items-center justify-between">
                <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">
                  Baseline
                </p>

                <span className="h-2.5 w-2.5 rounded-full bg-slate-400" />
              </div>

              <p className="mt-5 font-mono text-3xl font-bold tracking-tight text-slate-900">
                {baseline}
              </p>

              <p className="mt-1 text-xs text-slate-500">
                Before index
              </p>
            </div>
          </div>

          <div className="relative overflow-hidden rounded-2xl border border-blue-100 bg-gradient-to-br from-blue-50 to-cyan-50/70 p-5">
            <div className="absolute right-0 top-0 h-20 w-20 rounded-full bg-blue-200/40 blur-2xl" />

            <div className="relative">
              <div className="flex items-center justify-between">
                <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-blue-500">
                  Indexed
                </p>

                <span className="h-2.5 w-2.5 rounded-full bg-blue-500" />
              </div>

              <p className="mt-5 font-mono text-3xl font-bold tracking-tight text-blue-700">
                {indexed}
              </p>

              <p className="mt-1 text-xs text-blue-600/70">
                After index
              </p>
            </div>
          </div>
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <div className="rounded-2xl border border-emerald-100 bg-emerald-50/50 p-4">
            <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-emerald-600">
              Improvement
            </p>

            <p
              className={`mt-2 text-2xl font-bold tracking-tight ${improvementClass}`}
            >
              {improvement}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              Reported benchmark improvement
            </p>
          </div>

          <div className="rounded-2xl border border-violet-100 bg-violet-50/50 p-4">
            <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-violet-600">
              Execution-time savings
            </p>

            <p className="mt-2 text-2xl font-bold tracking-tight text-violet-700">
              {savings}
            </p>

            <p className="mt-1 text-xs text-slate-500">
              Baseline minus indexed execution time
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}

function BenchmarkDetail({
  benchmark,
  onRecommendationSelect,
}) {
  if (!benchmark) {
    return (
      <section className="dashboard-panel flex min-h-64 items-center justify-center">
        <div className="text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-500">
            <span className="text-lg">↗</span>
          </div>

          <p className="mt-4 text-sm font-semibold text-slate-800">
            Select a benchmark
          </p>

          <p className="mt-1 text-xs text-slate-500">
            Choose a result above to inspect its stored evidence.
          </p>
        </div>
      </section>
    )
  }

  return (
    <div className="space-y-5">
      <section className="dashboard-panel overflow-hidden">
        <div className="relative overflow-hidden border-b border-slate-200 bg-gradient-to-br from-white via-blue-50/50 to-cyan-50/40 px-6 py-7">
          <div className="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-blue-200/30 blur-3xl" />

          <div className="relative flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span className="status-badge status-badge-info">
                  Stored evidence
                </span>

                <span className="status-badge status-badge-muted">
                  {benchmark.scope || 'Scope unavailable'}
                </span>
              </div>

              <p className="mt-4 text-[10px] font-bold uppercase tracking-[0.16em] text-blue-500">
                Selected benchmark
              </p>

              <h2 className="mt-1 text-2xl font-bold tracking-tight text-slate-950">
                Benchmark #{benchmark.benchmark_id}
              </h2>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                Stored experimental validation evidence associated with this
                benchmark record.
              </p>
            </div>

            <div className="shrink-0">
              <StatusBadge value={benchmark.outcome} />
            </div>
          </div>

          <div className="relative mt-5 flex flex-wrap gap-2">
            {benchmark.recommendation_id !== null &&
              benchmark.recommendation_id !== undefined && (
                <span className="status-badge status-badge-info">
                  Recommendation #{benchmark.recommendation_id}
                </span>
              )}

            {benchmark.experiment_id && (
              <span className="status-badge status-badge-muted">
                {benchmark.experiment_id}
              </span>
            )}
          </div>
        </div>

        <div className="grid gap-3 p-5 sm:grid-cols-3">
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
            accent="blue"
          />

          <Metric
            label="Experiment ID"
            value={benchmark.experiment_id || 'Not available'}
            mono
          />
        </div>
      </section>

      <PerformanceComparison benchmark={benchmark} />

      <section className="dashboard-panel overflow-hidden">
        <div className="border-b border-slate-200/80 bg-gradient-to-r from-white to-violet-50/30 px-6 py-5">
          <p className="section-eyebrow section-eyebrow-violet">
            Validation evidence
          </p>

          <h3 className="mt-1 text-lg font-semibold text-slate-950">
            Execution validation
          </h3>

          <p className="mt-1 text-xs leading-5 text-slate-500">
            Stored validation properties associated with this benchmark.
          </p>
        </div>

        <div className="grid gap-3 p-5 sm:grid-cols-2 lg:grid-cols-4">
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

          <Metric
            label="Median improvement"
            value={
              benchmark.median_improvement_percent === null ||
              benchmark.median_improvement_percent === undefined
                ? 'Not available'
                : `${formatNumber(
                    benchmark.median_improvement_percent
                  )}%`
            }
            accent="violet"
          />
        </div>
      </section>

      {benchmark.recommendation_id !== null &&
        benchmark.recommendation_id !== undefined && (
          <section className="dashboard-panel overflow-hidden">
            <div className="flex flex-col gap-5 bg-gradient-to-r from-white via-blue-50/30 to-white p-6 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="section-eyebrow section-eyebrow-blue">
                  Evidence linkage
                </p>

                <h3 className="mt-1 text-base font-semibold text-slate-950">
                  Associated recommendation
                </h3>

                <p className="mt-1 max-w-2xl text-xs leading-5 text-slate-500">
                  Open the recommendation to inspect its complete evidence
                  chain.
                </p>
              </div>

              <button
                type="button"
                onClick={() =>
                  onRecommendationSelect(
                    benchmark.recommendation_id
                  )
                }
                className="inline-flex shrink-0 items-center justify-center rounded-xl border border-blue-200 bg-blue-50 px-4 py-2.5 text-sm font-semibold text-blue-700 transition hover:border-blue-300 hover:bg-blue-100 hover:shadow-sm"
              >
                Open Recommendation #
                {benchmark.recommendation_id}
                <span className="ml-2">→</span>
              </button>
            </div>
          </section>
        )}

      <section className="rounded-2xl border border-slate-200 bg-slate-50/80 p-5">
        <div className="flex gap-3">
          <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-white text-blue-600 shadow-sm">
            <span className="text-sm font-semibold">i</span>
          </div>

          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">
              Evidence boundary
            </p>

            <p className="mt-2 text-xs leading-5 text-slate-600">
              This page reports stored benchmark evidence. It does not rerun
              benchmarks, create or remove indexes, recalculate validation
              outcomes, or make production decisions.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}

export default BenchmarkDetail

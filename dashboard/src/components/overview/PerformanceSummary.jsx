function formatPercent(value) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return `${value.toFixed(2)}%`
}

function PerformanceMetric({
  label,
  value,
  accent,
  note,
}) {
  return (
    <div className="relative overflow-hidden rounded-xl border border-slate-200 bg-slate-50/70 p-4">
      <div
        className={`absolute bottom-0 left-0 top-0 w-0.5 ${accent}`}
      />

      <p className="text-[0.68rem] font-semibold uppercase tracking-[0.08em] text-slate-400">
        {label}
      </p>

      <p className="mt-2 text-[1.7rem] font-bold tracking-[-0.04em] text-slate-950">
        {value}
      </p>

      {note && (
        <p className="mt-1 text-[0.68rem] text-slate-400">
          {note}
        </p>
      )}
    </div>
  )
}

function PerformanceSummary({ performance }) {
  return (
    <section className="dashboard-card p-6">
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <h3 className="dashboard-section-title">
            Performance
          </h3>

          <p className="dashboard-section-description">
            Validated optimization outcomes available through the reporting
            API.
          </p>
        </div>

        <div className="rounded-lg bg-blue-50 px-2.5 py-1.5 text-[0.65rem] font-semibold text-blue-700">
          VALIDATED
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <PerformanceMetric
          label="Average improvement"
          value={formatPercent(
            performance.average_improvement_percent,
          )}
          accent="bg-blue-500"
          note="Across evaluated recommendations"
        />

        <PerformanceMetric
          label="Median improvement"
          value={formatPercent(
            performance.median_improvement_percent,
          )}
          accent="bg-violet-500"
          note="Median value not available"
        />

        <PerformanceMetric
          label="Index usage"
          value={formatPercent(
            performance.index_usage_percent,
          )}
          accent="bg-cyan-500"
          note="Validated executions using the index"
        />

        <PerformanceMetric
          label="Rows preserved"
          value={formatPercent(
            performance.rows_preserved_percent,
          )}
          accent="bg-emerald-500"
          note="All validated rows preserved"
        />
      </div>
    </section>
  )
}

export default PerformanceSummary

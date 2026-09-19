function formatPercent(value) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return `${value.toFixed(2)}%`
}

function PerformanceSummary({ performance }) {
  return (
    <section>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-slate-900">
          Performance
        </h3>
        <p className="mt-1 text-sm text-slate-500">
          Validated optimization outcomes available through the reporting API.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Average improvement</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">
            {formatPercent(performance.average_improvement_percent)}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Median improvement</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">
            {formatPercent(performance.median_improvement_percent)}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Index usage</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">
            {formatPercent(performance.index_usage_percent)}
          </p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Rows preserved</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">
            {formatPercent(performance.rows_preserved_percent)}
          </p>
        </div>
      </div>
    </section>
  )
}

export default PerformanceSummary

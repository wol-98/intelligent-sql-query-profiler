import StatusBadge from '../common/StatusBadge'

function formatNumber(value, digits = 2) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return Number(value).toFixed(digits)
}

function IndexUsage({ value }) {
  if (value === true) {
    return (
      <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-700">
        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
        Used
      </span>
    )
  }

  if (value === false) {
    return (
      <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-rose-600">
        <span className="h-1.5 w-1.5 rounded-full bg-rose-500" />
        Not used
      </span>
    )
  }

  return (
    <span className="text-xs font-medium text-slate-400">
      Not available
    </span>
  )
}

function ImprovementValue({ value }) {
  if (value === null || value === undefined) {
    return (
      <span className="text-xs font-medium text-slate-400">
        Not available
      </span>
    )
  }

  const numericValue = Number(value)

  const valueClass =
    numericValue > 0
      ? 'text-emerald-600'
      : numericValue < 0
        ? 'text-rose-600'
        : 'text-slate-600'

  return (
    <div className="text-right">
      <p className={`text-sm font-bold ${valueClass}`}>
        {formatNumber(value)}%
      </p>

      <p className="mt-0.5 text-[9px] font-medium uppercase tracking-[0.12em] text-slate-400">
        improvement
      </p>
    </div>
  )
}

function BenchmarkTable({
  benchmarks,
  selectedBenchmarkId,
  onSelect,
}) {
  if (!benchmarks.length) {
    return (
      <div className="dashboard-panel flex min-h-64 items-center justify-center">
        <div className="text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
            <span className="text-lg">∅</span>
          </div>

          <p className="mt-4 text-sm font-semibold text-slate-800">
            No benchmark results found
          </p>

          <p className="mt-1 text-xs text-slate-500">
            Try changing the current search or outcome filter.
          </p>
        </div>
      </div>
    )
  }

  return (
    <section className="dashboard-panel overflow-hidden">
      <div className="border-b border-slate-200/80 bg-gradient-to-r from-white to-slate-50/70 px-6 py-5">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="section-eyebrow section-eyebrow-blue">
              Stored evidence
            </p>

            <h2 className="mt-1 text-lg font-semibold text-slate-950">
              Benchmark inventory
            </h2>

            <p className="mt-1 text-xs leading-5 text-slate-500">
              Select a benchmark to inspect its stored experimental evidence.
            </p>
          </div>

          <span className="status-badge status-badge-muted">
            {benchmarks.length} result
            {benchmarks.length === 1 ? '' : 's'}
          </span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-[1080px] w-full">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50/80">
              <th className="px-6 py-3 text-left text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">
                Benchmark
              </th>

              <th className="px-4 py-3 text-left text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">
                Recommendation
              </th>

              <th className="px-4 py-3 text-right text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">
                Baseline
              </th>

              <th className="px-4 py-3 text-right text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">
                Indexed
              </th>

              <th className="px-4 py-3 text-right text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">
                Improvement
              </th>

              <th className="px-4 py-3 text-left text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">
                Index
              </th>

              <th className="px-6 py-3 text-left text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">
                Outcome
              </th>
            </tr>
          </thead>

          <tbody>
            {benchmarks.map((benchmark) => {
              const selected =
                benchmark.benchmark_id === selectedBenchmarkId

              return (
                <tr
                  key={benchmark.benchmark_id}
                  onClick={() => onSelect(benchmark)}
                  className={`group cursor-pointer border-b border-slate-100 transition-all duration-200 last:border-b-0 ${
                    selected
                      ? 'bg-blue-50/70 shadow-[inset_3px_0_0_#2f7df6]'
                      : 'hover:bg-slate-50/80'
                  }`}
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div
                        className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-[11px] font-bold transition ${
                          selected
                            ? 'bg-blue-600 text-white shadow-sm shadow-blue-200'
                            : 'bg-slate-100 text-slate-500 group-hover:bg-blue-50 group-hover:text-blue-600'
                        }`}
                      >
                        #{benchmark.benchmark_id}
                      </div>

                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-slate-900">
                          Benchmark #{benchmark.benchmark_id}
                        </p>

                        <p className="mt-1 truncate text-[10px] font-medium uppercase tracking-[0.1em] text-slate-400">
                          {benchmark.scope || 'Scope unavailable'}
                        </p>
                      </div>
                    </div>
                  </td>

                  <td className="px-4 py-4">
                    {benchmark.recommendation_id !== null &&
                    benchmark.recommendation_id !== undefined ? (
                      <span className="inline-flex items-center gap-1.5 rounded-lg border border-blue-100 bg-blue-50 px-2.5 py-1.5 text-xs font-bold text-blue-700">
                        <span className="h-1.5 w-1.5 rounded-full bg-blue-500" />
                        #{benchmark.recommendation_id}
                      </span>
                    ) : (
                      <span className="text-xs text-slate-400">
                        Not available
                      </span>
                    )}
                  </td>

                  <td className="px-4 py-4 text-right">
                    <span className="font-mono text-xs font-semibold text-slate-700">
                      {formatNumber(benchmark.baseline_time_ms)} ms
                    </span>
                  </td>

                  <td className="px-4 py-4 text-right">
                    <span className="font-mono text-xs font-semibold text-slate-700">
                      {formatNumber(benchmark.indexed_time_ms)} ms
                    </span>
                  </td>

                  <td className="px-4 py-4">
                    <ImprovementValue
                      value={benchmark.improvement_percent}
                    />
                  </td>

                  <td className="px-4 py-4">
                    <IndexUsage value={benchmark.index_used} />
                  </td>

                  <td className="px-6 py-4">
                    <StatusBadge value={benchmark.outcome} />
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <div className="border-t border-slate-100 bg-slate-50/50 px-6 py-3">
        <p className="text-[10px] font-medium uppercase tracking-[0.1em] text-slate-400">
          Select a row to inspect stored validation evidence
        </p>
      </div>
    </section>
  )
}

export default BenchmarkTable

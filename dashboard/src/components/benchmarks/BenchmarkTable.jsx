function formatNumber(value, digits = 2) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return Number(value).toFixed(digits)
}

function StatusBadge({ value }) {
  if (!value) {
    return (
      <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-500">
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
      className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
        styles[value] || 'bg-slate-100 text-slate-700'
      }`}
    >
      {value}
    </span>
  )
}

function BenchmarkTable({
  benchmarks,
  selectedBenchmarkId,
  onSelect,
}) {
  if (!benchmarks.length) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">
        <p className="text-sm text-slate-500">
          No benchmark results match the current filters.
        </p>
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Benchmark
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Recommendation
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Baseline
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Indexed
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Improvement
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Index Used
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Outcome
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-200">
            {benchmarks.map((benchmark) => {
              const selected =
                benchmark.benchmark_id === selectedBenchmarkId

              return (
                <tr
                  key={benchmark.benchmark_id}
                  onClick={() => onSelect(benchmark)}
                  className={`cursor-pointer transition ${
                    selected
                      ? 'bg-slate-100'
                      : 'hover:bg-slate-50'
                  }`}
                >
                  <td className="px-4 py-4">
                    <div className="font-medium text-slate-900">
                      Benchmark #{benchmark.benchmark_id}
                    </div>

                    <div className="mt-1 text-xs text-slate-500">
                      {benchmark.scope || 'Not available'}
                    </div>
                  </td>

                  <td className="px-4 py-4">
                    {benchmark.recommendation_id !== null &&
                    benchmark.recommendation_id !== undefined ? (
                      <span className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">
                        #{benchmark.recommendation_id}
                      </span>
                    ) : (
                      <span className="text-xs text-slate-400">
                        Not available
                      </span>
                    )}
                  </td>

                  <td className="px-4 py-4 text-right text-sm text-slate-700">
                    {formatNumber(benchmark.baseline_time_ms)} ms
                  </td>

                  <td className="px-4 py-4 text-right text-sm text-slate-700">
                    {formatNumber(benchmark.indexed_time_ms)} ms
                  </td>

                  <td className="px-4 py-4 text-right text-sm font-semibold text-slate-900">
                    {formatNumber(benchmark.improvement_percent)}%
                  </td>

                  <td className="px-4 py-4">
                    <span
                      className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                        benchmark.index_used === true
                          ? 'bg-green-50 text-green-700'
                          : benchmark.index_used === false
                            ? 'bg-red-50 text-red-700'
                            : 'bg-slate-100 text-slate-500'
                      }`}
                    >
                      {benchmark.index_used === true
                        ? 'Yes'
                        : benchmark.index_used === false
                          ? 'No'
                          : 'Not available'}
                    </span>
                  </td>

                  <td className="px-4 py-4">
                    <StatusBadge value={benchmark.outcome} />
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default BenchmarkTable

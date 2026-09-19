import StatusBadge from '../common/StatusBadge'

function formatMilliseconds(value) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return `${Number(value).toFixed(3)} ms`
}

function formatPercent(value) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return `${Number(value).toFixed(2)}%`
}

function WorkloadTable({ workloads }) {
  if (workloads.length === 0) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm text-slate-500">
          No workload patterns are available.
        </p>
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Priority
              </th>

              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Query Pattern
              </th>

              <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Executions
              </th>

              <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Total Time
              </th>

              <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Avg Time
              </th>

              <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Time Share
              </th>

              <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Frequency
              </th>

              <th className="px-5 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Recommendations
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-100">
            {workloads.map((workload) => (
              <tr
                key={workload.fingerprint}
                className="align-top transition hover:bg-slate-50"
              >
                <td className="whitespace-nowrap px-5 py-4">
                  <StatusBadge value={workload.priority} />
                </td>

                <td className="min-w-[420px] px-5 py-4">
                  <p
                    className="line-clamp-3 font-mono text-xs leading-5 text-slate-700"
                    title={workload.template}
                  >
                    {workload.template}
                  </p>

                  <p className="mt-2 font-mono text-[10px] text-slate-400">
                    {workload.fingerprint}
                  </p>
                </td>

                <td className="whitespace-nowrap px-5 py-4 text-right text-sm font-medium text-slate-700">
                  {workload.execution_count}
                </td>

                <td className="whitespace-nowrap px-5 py-4 text-right text-sm text-slate-700">
                  {formatMilliseconds(workload.total_execution_time_ms)}
                </td>

                <td className="whitespace-nowrap px-5 py-4 text-right text-sm text-slate-700">
                  {formatMilliseconds(workload.average_execution_time_ms)}
                </td>

                <td className="whitespace-nowrap px-5 py-4 text-right text-sm font-medium text-slate-700">
                  {formatPercent(workload.time_share)}
                </td>

                <td className="whitespace-nowrap px-5 py-4 text-right text-sm text-slate-700">
                  {formatPercent(workload.frequency_share)}
                </td>

                <td className="whitespace-nowrap px-5 py-4 text-right">
                  <span className="text-sm font-medium text-slate-700">
                    {workload.recommendation_ids.length}
                  </span>

                  {workload.recommendation_ids.length > 0 && (
                    <p className="mt-1 text-xs text-slate-400">
                      #{workload.recommendation_ids.join(', #')}
                    </p>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default WorkloadTable

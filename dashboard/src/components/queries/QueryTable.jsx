
function formatNumber(value, digits = 2) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return Number(value).toFixed(digits)
}

function formatInteger(value) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return Number(value).toLocaleString()
}

function QueryTable({ queries, selectedFingerprint, onSelect }) {
  if (!queries.length) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 text-center">
        <p className="text-sm text-slate-500">
          No queries match the current filters.
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
                Query
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Type
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Executions
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Avg. Time
              </th>
              <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">
                Rows
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Plan
              </th>
              <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                Recommendations
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-200">
            {queries.map((query) => {
              const isSelected = query.fingerprint === selectedFingerprint

              return (
                <tr
                  key={query.query_profile_id}
                  onClick={() => onSelect(query)}
                  className={`cursor-pointer transition ${
                    isSelected
                      ? 'bg-slate-100'
                      : 'hover:bg-slate-50'
                  }`}
                >
                  <td className="max-w-md px-4 py-4">
                    <div className="font-medium text-slate-900">
                      Profile #{query.query_profile_id}
                    </div>

                    <div
                      className="mt-1 truncate font-mono text-xs text-slate-500"
                      title={query.template || query.query_text}
                    >
                      {query.template || query.query_text}
                    </div>

                    <div className="mt-1 truncate font-mono text-[11px] text-slate-400">
                      {query.fingerprint}
                    </div>
                  </td>

                  <td className="px-4 py-4">
                    <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
                      {query.query_type}
                    </span>
                  </td>

                  <td className="px-4 py-4 text-right text-sm text-slate-700">
                    {formatInteger(query.execution_count)}
                  </td>

                  <td className="px-4 py-4 text-right text-sm font-medium text-slate-900">
                    {formatNumber(query.average_execution_time_ms)} ms
                  </td>

                  <td className="px-4 py-4 text-right text-sm text-slate-700">
                    {formatInteger(query.rows_processed)}
                  </td>

                  <td className="px-4 py-4">
                    <div className="flex flex-wrap gap-1.5">
                      {(query.plan?.node_types || []).map((nodeType) => (
                        <span
                          key={nodeType}
                          className="rounded-full bg-slate-100 px-2 py-1 text-[11px] text-slate-600"
                        >
                          {nodeType}
                        </span>
                      ))}
                    </div>
                  </td>

                  <td className="px-4 py-4">
                    {query.recommendation_ids?.length ? (
                      <div className="flex flex-wrap gap-1.5">
                        {query.recommendation_ids.map((id) => (
                          <span
                            key={id}
                            className="rounded-full bg-blue-50 px-2 py-1 text-[11px] font-medium text-blue-700"
                          >
                            #{id}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="text-xs text-slate-400">
                        None
                      </span>
                    )}
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

export default QueryTable

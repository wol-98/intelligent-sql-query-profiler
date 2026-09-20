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
      <div className="rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-sm">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-xl text-slate-400">
          ⌕
        </div>
        <p className="mt-4 text-sm font-semibold text-slate-700">
          No queries match the current filters.
        </p>
        <p className="mt-1 text-xs text-slate-400">
          Try a different search term or query type.
        </p>
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-50/90">
            <tr>
              <th className="px-5 py-3.5 text-left text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-400">
                Query
              </th>
              <th className="px-4 py-3.5 text-left text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-400">
                Type
              </th>
              <th className="px-4 py-3.5 text-right text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-400">
                Executions
              </th>
              <th className="px-4 py-3.5 text-right text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-400">
                Avg. Time
              </th>
              <th className="px-4 py-3.5 text-right text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-400">
                Rows
              </th>
              <th className="px-4 py-3.5 text-left text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-400">
                Plan
              </th>
              <th className="px-5 py-3.5 text-left text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-400">
                Recommendations
              </th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-100">
            {queries.map((query) => {
              const isSelected =
                query.fingerprint === selectedFingerprint

              return (
                <tr
                  key={query.query_profile_id}
                  onClick={() => onSelect(query)}
                  className={`cursor-pointer transition ${
                    isSelected
                      ? 'bg-blue-50/70'
                      : 'bg-white hover:bg-slate-50'
                  }`}
                >
                  <td className="relative max-w-md px-5 py-4">
                    {isSelected && (
                      <span className="absolute bottom-0 left-0 top-0 w-1 bg-blue-500" />
                    )}

                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-slate-900">
                        Profile #{query.query_profile_id}
                      </span>

                      {isSelected && (
                        <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-blue-700">
                          Selected
                        </span>
                      )}
                    </div>

                    <div
                      className="mt-1.5 truncate font-mono text-xs leading-5 text-slate-500"
                      title={query.template || query.query_text}
                    >
                      {query.template || query.query_text}
                    </div>

                    <div
                      className="mt-1 truncate font-mono text-[10px] text-slate-400"
                      title={query.fingerprint}
                    >
                      {query.fingerprint}
                    </div>
                  </td>

                  <td className="px-4 py-4">
                    <span className="inline-flex rounded-full border border-blue-100 bg-blue-50 px-2.5 py-1 text-[11px] font-semibold text-blue-700">
                      {query.query_type}
                    </span>
                  </td>

                  <td className="px-4 py-4 text-right text-sm font-medium text-slate-700">
                    {formatInteger(query.execution_count)}
                  </td>

                  <td className="px-4 py-4 text-right">
                    <span className="text-sm font-bold text-slate-900">
                      {formatNumber(query.average_execution_time_ms)}
                    </span>
                    <span className="ml-1 text-xs text-slate-400">
                      ms
                    </span>
                  </td>

                  <td className="px-4 py-4 text-right text-sm text-slate-600">
                    {formatInteger(query.rows_processed)}
                  </td>

                  <td className="px-4 py-4">
                    <div className="flex max-w-[190px] flex-wrap gap-1.5">
                      {(query.plan?.node_types || []).length ? (
                        query.plan.node_types.map((nodeType) => (
                          <span
                            key={nodeType}
                            className="rounded-full border border-slate-200 bg-slate-50 px-2 py-1 text-[10px] font-medium text-slate-600"
                          >
                            {nodeType}
                          </span>
                        ))
                      ) : (
                        <span className="text-xs text-slate-400">
                          Not available
                        </span>
                      )}
                    </div>
                  </td>

                  <td className="px-5 py-4">
                    {query.recommendation_ids?.length ? (
                      <div className="flex flex-wrap gap-1.5">
                        {query.recommendation_ids.map((id) => (
                          <span
                            key={id}
                            className="rounded-full border border-blue-100 bg-blue-50 px-2.5 py-1 text-[10px] font-semibold text-blue-700"
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

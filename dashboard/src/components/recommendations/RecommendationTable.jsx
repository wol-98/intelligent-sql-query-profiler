import StatusBadge from '../common/StatusBadge'

function formatPercent(value) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return `${value.toFixed(2)}%`
}

function RecommendationTable({ recommendations, onSelect }) {
  if (recommendations.length === 0) {
    return (
      <div className="dashboard-card p-12 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-lg text-slate-500">
          ⌕
        </div>

        <h3 className="mt-4 text-base font-bold text-slate-900">
          No recommendations found
        </h3>

        <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
          No recommendation matches the current search and filter combination.
          Try changing or clearing the active filters.
        </p>
      </div>
    )
  }

  return (
    <div className="dashboard-card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-[1200px] w-full border-collapse text-left">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50/90">
              <th className="px-5 py-3.5 text-[0.64rem] font-bold uppercase tracking-[0.08em] text-slate-400">
                ID
              </th>

              <th className="px-5 py-3.5 text-[0.64rem] font-bold uppercase tracking-[0.08em] text-slate-400">
                Target
              </th>

              <th className="px-5 py-3.5 text-[0.64rem] font-bold uppercase tracking-[0.08em] text-slate-400">
                Score
              </th>

              <th className="px-5 py-3.5 text-[0.64rem] font-bold uppercase tracking-[0.08em] text-slate-400">
                Priority
              </th>

              <th className="px-5 py-3.5 text-[0.64rem] font-bold uppercase tracking-[0.08em] text-slate-400">
                Validation
              </th>

              <th className="px-5 py-3.5 text-[0.64rem] font-bold uppercase tracking-[0.08em] text-slate-400">
                Improvement
              </th>

              <th className="px-5 py-3.5 text-[0.64rem] font-bold uppercase tracking-[0.08em] text-slate-400">
                Decision
              </th>

              <th className="px-5 py-3.5 text-[0.64rem] font-bold uppercase tracking-[0.08em] text-slate-400">
                Evidence
              </th>
            </tr>
          </thead>

          <tbody>
            {recommendations.map((recommendation) => (
              <tr
                key={recommendation.recommendation_id}
                onClick={() =>
                  onSelect(recommendation.recommendation_id)
                }
                className="group cursor-pointer border-b border-slate-100 transition last:border-b-0 hover:bg-blue-50/35"
              >
                <td className="relative px-5 py-4 align-top">
                  <span className="absolute bottom-0 left-0 top-0 w-0.5 bg-transparent transition group-hover:bg-blue-500" />

                  <span className="inline-flex rounded-lg bg-slate-100 px-2.5 py-1 font-mono text-xs font-bold text-slate-600 transition group-hover:bg-blue-100 group-hover:text-blue-700">
                    #{recommendation.recommendation_id}
                  </span>
                </td>

                <td className="px-5 py-4 align-top">
                  <div className="min-w-[240px]">
                    <p className="font-semibold text-slate-900">
                      {recommendation.table_name}
                    </p>

                    <p className="mt-1 text-xs font-medium text-slate-500">
                      {recommendation.columns.length > 0
                        ? recommendation.columns.join(', ')
                        : 'Column information not available'}
                    </p>

                    {recommendation.index_name && (
                      <p className="mt-2 max-w-[280px] truncate rounded-md bg-slate-50 px-2 py-1 font-mono text-[0.65rem] text-slate-400">
                        {recommendation.index_name}
                      </p>
                    )}
                  </div>
                </td>

                <td className="px-5 py-4 align-top">
                  <span className="font-mono text-sm font-semibold text-slate-800">
                    {recommendation.score.toFixed(2)}
                  </span>
                </td>

                <td className="px-5 py-4 align-top">
                  <StatusBadge
                    value={recommendation.priority?.toUpperCase()}
                  />
                </td>

                <td className="px-5 py-4 align-top">
                  <StatusBadge value={recommendation.validation.outcome} />
                </td>

                <td className="px-5 py-4 align-top">
                  <span className="text-sm font-semibold text-slate-800">
                    {formatPercent(recommendation.validation.improvement)}
                  </span>
                </td>

                <td className="px-5 py-4 align-top">
                  <StatusBadge value={recommendation.decision.state} />
                </td>

                <td className="px-5 py-4 align-top">
                  <StatusBadge
                    value={recommendation.provenance.evidence_status}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-200 bg-slate-50/70 px-5 py-3">
        <p className="text-xs font-medium text-slate-500">
          Showing {recommendations.length} recommendation
          {recommendations.length === 1 ? '' : 's'}.
        </p>

        <p className="text-[0.68rem] text-slate-400">
          Select a row to inspect evidence
        </p>
      </div>
    </div>
  )
}

export default RecommendationTable

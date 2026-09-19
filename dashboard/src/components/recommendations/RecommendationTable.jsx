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
      <div className="rounded-xl border border-slate-200 bg-white p-10 text-center shadow-sm">
        <h3 className="text-base font-semibold text-slate-900">
          No recommendations found
        </h3>

        <p className="mt-2 text-sm text-slate-500">
          Try changing or clearing the current filters.
        </p>
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-[1200px] w-full border-collapse text-left">
          <thead className="bg-slate-50">
            <tr className="border-b border-slate-200">
              <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                ID
              </th>

              <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Target
              </th>

              <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Score
              </th>

              <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Priority
              </th>

              <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Validation
              </th>

              <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Improvement
              </th>

              <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Decision
              </th>

              <th className="px-5 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
                Evidence
              </th>
            </tr>
          </thead>

          <tbody>
            {recommendations.map((recommendation) => (
              <tr
                key={recommendation.recommendation_id}
                onClick={() => onSelect(recommendation.recommendation_id)}
                className="cursor-pointer border-b border-slate-100 last:border-b-0 hover:bg-slate-50"
              >
                <td className="px-5 py-4 align-top">
                  <span className="font-mono text-sm font-medium text-slate-700">
                    #{recommendation.recommendation_id}
                  </span>
                </td>

                <td className="px-5 py-4 align-top">
                  <div className="min-w-[240px]">
                    <p className="font-medium text-slate-900">
                      {recommendation.table_name}
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      {recommendation.columns.length > 0
                        ? recommendation.columns.join(', ')
                        : 'Column information not available'}
                    </p>

                    {recommendation.index_name && (
                      <p className="mt-1 font-mono text-xs text-slate-400">
                        {recommendation.index_name}
                      </p>
                    )}
                  </div>
                </td>

                <td className="px-5 py-4 align-top">
                  <span className="font-medium text-slate-800">
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
                  <span className="text-sm font-medium text-slate-800">
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

      <div className="border-t border-slate-200 bg-slate-50 px-5 py-3">
        <p className="text-xs text-slate-500">
          Showing {recommendations.length} recommendation
          {recommendations.length === 1 ? '' : 's'}.
        </p>
      </div>
    </div>
  )
}

export default RecommendationTable

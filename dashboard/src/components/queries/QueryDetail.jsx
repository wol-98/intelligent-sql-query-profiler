
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

function Metric({ label, value }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <p className="mt-1 text-sm font-semibold text-slate-900">
        {value}
      </p>
    </div>
  )
}

function BooleanMetric({ label, value }) {
  let display = 'Not available'

  if (value === true) {
    display = 'Yes'
  } else if (value === false) {
    display = 'No'
  }

  return <Metric label={label} value={display} />
}

function QueryDetail({ query, onRecommendationSelect }) {
  if (!query) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8">
        <p className="text-sm text-slate-500">
          Select a query to inspect its details.
        </p>
      </div>
    )
  }

  const plan = query.plan

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-slate-200 bg-white p-6">
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Query Profile
            </p>

            <h2 className="mt-1 text-xl font-semibold text-slate-900">
              Profile #{query.query_profile_id}
            </h2>

            <p className="mt-2 break-all font-mono text-xs text-slate-500">
              {query.fingerprint}
            </p>
          </div>

          <span className="w-fit rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
            {query.query_type}
          </span>
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6">
        <h3 className="text-base font-semibold text-slate-900">
          SQL
        </h3>

        <div className="mt-4 space-y-4">
          <div>
            <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
              Template
            </p>

            <pre className="overflow-x-auto rounded-lg bg-slate-950 p-4 text-sm text-slate-100">
              <code>{query.template || 'Not available'}</code>
            </pre>
          </div>

          <div>
            <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
              Captured Query
            </p>

            <pre className="overflow-x-auto rounded-lg bg-slate-50 p-4 font-mono text-sm text-slate-700">
              <code>{query.query_text}</code>
            </pre>
          </div>
        </div>
      </section>

      <section>
        <h3 className="mb-3 text-base font-semibold text-slate-900">
          Execution Characteristics
        </h3>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Metric
            label="Executions"
            value={formatInteger(query.execution_count)}
          />

          <Metric
            label="Total Time"
            value={
              query.total_execution_time_ms === null ||
              query.total_execution_time_ms === undefined
                ? 'Not available'
                : `${formatNumber(query.total_execution_time_ms)} ms`
            }
          />

          <Metric
            label="Average Time"
            value={
              query.average_execution_time_ms === null ||
              query.average_execution_time_ms === undefined
                ? 'Not available'
                : `${formatNumber(query.average_execution_time_ms)} ms`
            }
          />

          <Metric
            label="Rows Processed"
            value={formatInteger(query.rows_processed)}
          />
        </div>
      </section>

      <section>
        <h3 className="mb-3 text-base font-semibold text-slate-900">
          Query Context
        </h3>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <Metric
            label="Table"
            value={query.table_name || 'Not available'}
          />

          <Metric
            label="Profile ID"
            value={query.query_profile_id}
          />

          <Metric
            label="Captured At"
            value={query.captured_at || 'Not available'}
          />
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6">
        <h3 className="text-base font-semibold text-slate-900">
          Execution Plan
        </h3>

        {plan ? (
          <div className="mt-4 space-y-4">
            <div>
              <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-500">
                Node Types
              </p>

              <div className="flex flex-wrap gap-2">
                {plan.node_types?.length ? (
                  plan.node_types.map((nodeType) => (
                    <span
                      key={nodeType}
                      className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700"
                    >
                      {nodeType}
                    </span>
                  ))
                ) : (
                  <span className="text-sm text-slate-400">
                    Not available
                  </span>
                )}
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <Metric
                label="Sequential Scans"
                value={formatInteger(plan.sequential_scans)}
              />

              <Metric
                label="Index Scans"
                value={formatInteger(plan.index_scans)}
              />

              <Metric
                label="Bitmap Scans"
                value={formatInteger(plan.bitmap_scans)}
              />

              <Metric
                label="Joins"
                value={formatInteger(plan.joins)}
              />
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <BooleanMetric
                label="Has Filter"
                value={plan.has_filter}
              />

              <BooleanMetric
                label="Has Index Condition"
                value={plan.has_index_condition}
              />
            </div>
          </div>
        ) : (
          <p className="mt-4 text-sm text-slate-500">
            Execution-plan information is not available for this query.
          </p>
        )}
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-6">
        <h3 className="text-base font-semibold text-slate-900">
          Associated Recommendations
        </h3>

        {query.recommendation_ids?.length ? (
          <div className="mt-4 flex flex-wrap gap-2">
            {query.recommendation_ids.map((id) => (
              <button
                key={id}
                type="button"
                onClick={() => onRecommendationSelect(id)}
                className="rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-sm font-medium text-blue-700 transition hover:bg-blue-100"
              >
                Recommendation #{id}
              </button>
            ))}
          </div>
        ) : (
          <p className="mt-4 text-sm text-slate-500">
            No recommendations are associated with this query profile.
          </p>
        )}
      </section>
    </div>
  )
}

export default QueryDetail

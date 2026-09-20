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

function Metric({ label, value, accent = 'blue' }) {
  const accents = {
    blue: 'border-blue-100 bg-blue-50/40',
    cyan: 'border-cyan-100 bg-cyan-50/40',
    violet: 'border-violet-100 bg-violet-50/40',
    emerald: 'border-emerald-100 bg-emerald-50/40',
  }

  return (
    <div
      className={`rounded-xl border p-4 ${
        accents[accent] || accents.blue
      }`}
    >
      <p className="text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-400">
        {label}
      </p>
      <p className="mt-2 break-words text-sm font-bold text-slate-900">
        {value}
      </p>
    </div>
  )
}

function BooleanMetric({ label, value }) {
  let display = 'Not available'
  let className = 'border-slate-200 bg-slate-50 text-slate-500'

  if (value === true) {
    display = 'Yes'
    className = 'border-emerald-100 bg-emerald-50 text-emerald-700'
  } else if (value === false) {
    display = 'No'
    className = 'border-slate-200 bg-slate-50 text-slate-600'
  }

  return (
    <div className={`rounded-xl border p-4 ${className}`}>
      <p className="text-[10px] font-semibold uppercase tracking-[0.15em] opacity-70">
        {label}
      </p>
      <p className="mt-2 text-sm font-bold">
        {display}
      </p>
    </div>
  )
}

function QueryDetail({ query, onRecommendationSelect }) {
  if (!query) {
    return (
      <section className="rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center shadow-sm">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-500">
          ↗
        </div>
        <p className="mt-4 text-sm font-semibold text-slate-700">
          Select a query to inspect its details.
        </p>
        <p className="mt-1 text-xs text-slate-400">
          Query execution, plan, and recommendation evidence will appear here.
        </p>
      </section>
    )
  }

  const plan = query.plan

  return (
    <section className="space-y-6">
      <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-cyan-600">
        <span className="h-2 w-2 rounded-full bg-cyan-500" />
        Selected query
      </div>

      <section className="relative overflow-hidden rounded-2xl border border-blue-100 bg-white shadow-sm">
        <div className="absolute right-0 top-0 h-36 w-64 rounded-bl-full bg-gradient-to-br from-blue-50 via-indigo-50 to-transparent" />

        <div className="relative p-6 lg:p-7">
          <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-blue-500">
                Query profile
              </p>

              <h2 className="mt-2 text-2xl font-bold tracking-tight text-slate-950">
                Profile #{query.query_profile_id}
              </h2>

              <p className="mt-3 break-all font-mono text-xs leading-5 text-slate-400">
                {query.fingerprint}
              </p>
            </div>

            <span className="w-fit rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700">
              {query.query_type}
            </span>
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-violet-600">
            <span className="h-2 w-2 rounded-full bg-violet-500" />
            SQL evidence
          </div>
          <h3 className="mt-2 text-lg font-bold text-slate-950">
            Query text
          </h3>
          <p className="mt-1 text-sm text-slate-500">
            Normalized template and captured query text reported by the profiler.
          </p>
        </div>

        <div className="mt-5 space-y-4">
          <div>
            <p className="mb-2 text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-400">
              Template
            </p>

            <pre className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-950 p-5 font-mono text-xs leading-6 text-slate-100 shadow-inner">
              <code>{query.template || 'Not available'}</code>
            </pre>
          </div>

          <div>
            <p className="mb-2 text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-400">
              Captured Query
            </p>

            <pre className="overflow-x-auto rounded-xl border border-slate-200 bg-slate-50 p-5 font-mono text-xs leading-6 text-slate-700">
              <code>{query.query_text}</code>
            </pre>
          </div>
        </div>
      </section>

      <section>
        <div className="mb-4">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-blue-600">
            <span className="h-2 w-2 rounded-full bg-blue-500" />
            Execution evidence
          </div>
          <h3 className="mt-2 text-lg font-bold text-slate-950">
            Execution characteristics
          </h3>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Metric
            label="Executions"
            value={formatInteger(query.execution_count)}
            accent="blue"
          />

          <Metric
            label="Total Time"
            value={
              query.total_execution_time_ms === null ||
              query.total_execution_time_ms === undefined
                ? 'Not available'
                : `${formatNumber(query.total_execution_time_ms)} ms`
            }
            accent="cyan"
          />

          <Metric
            label="Average Time"
            value={
              query.average_execution_time_ms === null ||
              query.average_execution_time_ms === undefined
                ? 'Not available'
                : `${formatNumber(query.average_execution_time_ms)} ms`
            }
            accent="violet"
          />

          <Metric
            label="Rows Processed"
            value={formatInteger(query.rows_processed)}
            accent="emerald"
          />
        </div>
      </section>

      <section>
        <div className="mb-4">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-cyan-600">
            <span className="h-2 w-2 rounded-full bg-cyan-500" />
            Query context
          </div>
          <h3 className="mt-2 text-lg font-bold text-slate-950">
            Profile context
          </h3>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <Metric
            label="Table"
            value={query.table_name || 'Not available'}
            accent="cyan"
          />

          <Metric
            label="Profile ID"
            value={query.query_profile_id}
            accent="blue"
          />

          <Metric
            label="Captured At"
            value={query.captured_at || 'Not available'}
            accent="violet"
          />
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-emerald-600">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            Plan evidence
          </div>
          <h3 className="mt-2 text-lg font-bold text-slate-950">
            Execution plan
          </h3>
          <p className="mt-1 text-sm text-slate-500">
            Plan characteristics available for the selected query profile.
          </p>
        </div>

        {plan ? (
          <div className="mt-5 space-y-5">
            <div>
              <p className="mb-2 text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-400">
                Node Types
              </p>

              <div className="flex flex-wrap gap-2">
                {plan.node_types?.length ? (
                  plan.node_types.map((nodeType) => (
                    <span
                      key={nodeType}
                      className="rounded-full border border-emerald-100 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700"
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
                accent="blue"
              />

              <Metric
                label="Index Scans"
                value={formatInteger(plan.index_scans)}
                accent="emerald"
              />

              <Metric
                label="Bitmap Scans"
                value={formatInteger(plan.bitmap_scans)}
                accent="cyan"
              />

              <Metric
                label="Joins"
                value={formatInteger(plan.joins)}
                accent="violet"
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
          <div className="mt-5 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-5">
            <p className="text-sm text-slate-500">
              Execution-plan information is not available for this query.
            </p>
          </div>
        )}
      </section>

      <section className="rounded-2xl border border-blue-100 bg-blue-50/30 p-6 shadow-sm">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-blue-600">
            <span className="h-2 w-2 rounded-full bg-blue-500" />
            Recommendation evidence
          </div>
          <h3 className="mt-2 text-lg font-bold text-slate-950">
            Associated recommendations
          </h3>
          <p className="mt-1 text-sm text-slate-500">
            Recommendations explicitly associated with this query profile.
          </p>
        </div>

        {query.recommendation_ids?.length ? (
          <div className="mt-5 flex flex-wrap gap-2">
            {query.recommendation_ids.map((id) => (
              <button
                key={id}
                type="button"
                onClick={() => onRecommendationSelect(id)}
                className="rounded-xl border border-blue-200 bg-white px-4 py-2.5 text-sm font-semibold text-blue-700 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-300 hover:bg-blue-50 hover:shadow-md focus:outline-none focus:ring-4 focus:ring-blue-100"
              >
                Recommendation #{id}
                <span className="ml-2">→</span>
              </button>
            ))}
          </div>
        ) : (
          <div className="mt-5 rounded-xl border border-dashed border-blue-200 bg-white/70 p-5">
            <p className="text-sm text-slate-500">
              No recommendations are associated with this query profile.
            </p>
          </div>
        )}
      </section>
    </section>
  )
}

export default QueryDetail

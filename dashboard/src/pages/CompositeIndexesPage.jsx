import { useEffect, useMemo, useState } from 'react'
import { getCompositeIndexes } from '../api/client'

function formatPercent(value) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return `${value.toFixed(2)}%`
}

function formatEffect(value) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return `${value > 0 ? '+' : ''}${value.toFixed(2)} pp`
}

function UsageBadge({ used }) {
  if (used === true) {
    return (
      <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
        Used
      </span>
    )
  }

  if (used === false) {
    return (
      <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
        Not used
      </span>
    )
  }

  return (
    <span className="rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700">
      Not available
    </span>
  )
}

function ColumnOrder({ columns }) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      {columns.map((column, index) => (
        <div key={`${column}-${index}`} className="flex items-center gap-2">
          <span className="rounded-md bg-slate-100 px-2.5 py-1.5 font-mono text-xs text-slate-700">
            {column}
          </span>

          {index < columns.length - 1 && (
            <span className="text-slate-400">→</span>
          )}
        </div>
      ))}
    </div>
  )
}

function SummaryCard({ label, value, detail }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
        {label}
      </p>

      <p className="mt-2 text-2xl font-semibold text-slate-900">
        {value}
      </p>

      {detail && (
        <p className="mt-1 text-xs text-slate-500">
          {detail}
        </p>
      )}
    </div>
  )
}

function CompositeExperimentCard({ experiment }) {
  return (
    <article className="rounded-xl border border-slate-200 bg-white">
      <div className="border-b border-slate-200 px-6 py-5">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              M16.2 experiment
            </p>

            <h3 className="mt-1 text-base font-semibold text-slate-900">
              Recommendation {experiment.recommendation_id}
            </h3>
          </div>

          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
            {experiment.column_count} columns
          </span>
        </div>
      </div>

      <div className="space-y-6 px-6 py-6">
        <div className="grid gap-6 lg:grid-cols-2">
          <div>
            <p className="mb-3 text-xs font-medium uppercase tracking-wide text-slate-400">
              Original order
            </p>

            <ColumnOrder columns={experiment.original_order} />
          </div>

          <div>
            <p className="mb-3 text-xs font-medium uppercase tracking-wide text-slate-400">
              Alternative order
            </p>

            <ColumnOrder columns={experiment.alternative_order} />
          </div>
        </div>

        <div className="grid gap-4 border-t border-slate-100 pt-5 sm:grid-cols-3">
          <div>
            <p className="text-xs text-slate-400">
              Original improvement
            </p>

            <p className="mt-1 text-lg font-semibold text-slate-900">
              {formatPercent(experiment.original_improvement_percent)}
            </p>
          </div>

          <div>
            <p className="text-xs text-slate-400">
              Alternative improvement
            </p>

            <p className="mt-1 text-lg font-semibold text-slate-900">
              {formatPercent(experiment.alternative_improvement_percent)}
            </p>
          </div>

          <div>
            <p className="text-xs text-slate-400">
              Order effect
            </p>

            <p className="mt-1 text-lg font-semibold text-slate-900">
              {formatEffect(experiment.order_effect_percentage_points)}
            </p>
          </div>
        </div>

        <div className="grid gap-4 border-t border-slate-100 pt-5 sm:grid-cols-3">
          <div>
            <p className="text-xs text-slate-400">
              Original index
            </p>

            <div className="mt-2">
              <UsageBadge used={experiment.original_index_used} />
            </div>
          </div>

          <div>
            <p className="text-xs text-slate-400">
              Alternative index
            </p>

            <div className="mt-2">
              <UsageBadge used={experiment.alternative_index_used} />
            </div>
          </div>

          <div>
            <p className="text-xs text-slate-400">
              Rows preserved
            </p>

            <p className="mt-2 text-sm font-medium text-slate-700">
              {experiment.original_rows_preserved &&
              experiment.alternative_rows_preserved
                ? 'Yes — both variants'
                : 'Evidence differs'}
            </p>
          </div>
        </div>
      </div>
    </article>
  )
}

function CompositeIndexesPage() {
  const [experiments, setExperiments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let active = true

    async function loadCompositeIndexes() {
      try {
        setLoading(true)
        setError(null)

        const data = await getCompositeIndexes()

        if (active) {
          setExperiments(data)
        }
      } catch (requestError) {
        if (active) {
          setError(requestError.message)
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    loadCompositeIndexes()

    return () => {
      active = false
    }
  }, [])

  const summary = useMemo(() => {
    const twoColumn = experiments.filter(
      (experiment) => experiment.column_count === 2,
    ).length

    const threeColumn = experiments.filter(
      (experiment) => experiment.column_count === 3,
    ).length

    const originalUsed = experiments.filter(
      (experiment) => experiment.original_index_used === true,
    ).length

    const alternativeUsed = experiments.filter(
      (experiment) => experiment.alternative_index_used === true,
    ).length

    return {
      total: experiments.length,
      twoColumn,
      threeColumn,
      originalUsed,
      alternativeUsed,
    }
  }, [experiments])

  return (
    <main className="space-y-8 p-8">
      <div>
        <p className="text-sm font-medium text-slate-500">
          M20.8 · Composite Indexes
        </p>

        <h2 className="mt-1 text-2xl font-semibold text-slate-900">
          Composite Indexes
        </h2>

        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
          Controlled M16.2 evidence comparing alternative column orders
          for composite indexes. The dashboard reports established
          experimental results and does not rerun index experiments.
        </p>
      </div>

      {loading && (
        <div className="rounded-xl border border-slate-200 bg-white p-8 text-sm text-slate-500">
          Loading composite index evidence…
        </div>
      )}

      {error && !loading && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-6">
          <p className="text-sm font-medium text-red-800">
            Unable to load composite index evidence.
          </p>

          <p className="mt-1 text-sm text-red-700">
            {error}
          </p>
        </div>
      )}

      {!loading && !error && (
        <>
          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
            <SummaryCard
              label="Experiments"
              value={summary.total}
              detail="Established M16.2 results"
            />

            <SummaryCard
              label="Two-column"
              value={summary.twoColumn}
              detail="Composite index experiments"
            />

            <SummaryCard
              label="Three-column"
              value={summary.threeColumn}
              detail="Composite index experiments"
            />

            <SummaryCard
              label="Original used"
              value={`${summary.originalUsed}/${summary.total}`}
              detail="Original order variants"
            />

            <SummaryCard
              label="Alternative used"
              value={`${summary.alternativeUsed}/${summary.total}`}
              detail="Alternative order variants"
            />
          </section>

          <section className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-slate-900">
                Column-order experiments
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                Original and alternative orders are compared against the
                same experimental baseline.
              </p>
            </div>

            {experiments.map((experiment) => (
              <CompositeExperimentCard
                key={experiment.recommendation_id}
                experiment={experiment}
              />
            ))}
          </section>

          <section className="rounded-xl border border-slate-200 bg-slate-50 p-6">
            <h3 className="text-sm font-semibold text-slate-900">
              Evidence boundary
            </h3>

            <p className="mt-2 text-sm leading-6 text-slate-600">
              These results describe the tested queries, database state,
              data, planner, cache, and experimental conditions. They
              do not establish a universal optimal column order or create
              permanent indexes.
            </p>

            <p className="mt-3 text-xs text-slate-400">
              Evidence source: M16.2
            </p>
          </section>
        </>
      )}
    </main>
  )
}

export default CompositeIndexesPage

import { useEffect, useMemo, useState } from 'react'

import { getCompositeIndexes } from '../api/client'
import KpiCard from '../components/ui/KpiCard'

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

function effectTone(value) {
  if (value === null || value === undefined) {
    return 'text-slate-900'
  }

  if (value > 0) {
    return 'text-emerald-600'
  }

  if (value < 0) {
    return 'text-rose-600'
  }

  return 'text-slate-900'
}

function usageTone(used) {
  if (used === true) {
    return 'border-emerald-200 bg-emerald-50 text-emerald-700'
  }

  if (used === false) {
    return 'border-slate-200 bg-slate-100 text-slate-600'
  }

  return 'border-amber-200 bg-amber-50 text-amber-700'
}

function UsageBadge({ used }) {
  const label =
    used === true ? 'Used' : used === false ? 'Not used' : 'Not available'

  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${usageTone(
        used,
      )}`}
    >
      <span
        className={`mr-1.5 h-1.5 w-1.5 rounded-full ${
          used === true
            ? 'bg-emerald-500'
            : used === false
              ? 'bg-slate-400'
              : 'bg-amber-500'
        }`}
      />
      {label}
    </span>
  )
}

function SectionEyebrow({ children, tone = 'blue' }) {
  const tones = {
    blue: 'bg-blue-500',
    cyan: 'bg-cyan-500',
    violet: 'bg-violet-500',
    emerald: 'bg-emerald-500',
    amber: 'bg-amber-500',
  }

  return (
    <div className="flex items-center gap-2 text-[0.68rem] font-semibold uppercase tracking-[0.18em] text-slate-400">
      <span className={`h-2 w-2 rounded-full ${tones[tone]}`} />
      {children}
    </div>
  )
}

function ColumnOrder({ columns, emphasized = false }) {
  return (
    <div
      className={`rounded-xl border p-4 ${
        emphasized
          ? 'border-blue-200 bg-blue-50/60'
          : 'border-slate-200 bg-slate-50/70'
      }`}
    >
      <div className="flex flex-wrap items-center gap-2">
        {columns.map((column, index) => (
          <div key={`${column}-${index}`} className="flex items-center gap-2">
            <span
              className={`rounded-lg border px-3 py-2 font-mono text-xs font-medium ${
                emphasized
                  ? 'border-blue-200 bg-white text-blue-800'
                  : 'border-slate-200 bg-white text-slate-700'
              }`}
            >
              {column}
            </span>

            {index < columns.length - 1 && (
              <span className="text-sm font-semibold text-slate-300">→</span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function ImprovementBar({ value, label }) {
  const safeValue =
    value === null || value === undefined ? 0 : Math.max(0, Math.min(value, 100))

  return (
    <div>
      <div className="mb-2 flex items-end justify-between gap-4">
        <p className="text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-slate-400">
          {label}
        </p>

        <p className="text-sm font-semibold text-slate-900">
          {formatPercent(value)}
        </p>
      </div>

      <div className="h-2 overflow-hidden rounded-full bg-slate-100">
        <div
          className="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-400 transition-all duration-500"
          style={{ width: `${safeValue}%` }}
        />
      </div>
    </div>
  )
}

function CompositeExperimentCard({ experiment }) {
  const effect = experiment.order_effect_percentage_points

  const effectDescription =
    effect === null || effect === undefined
      ? 'Order effect not available'
      : effect > 0
        ? 'Alternative order measured higher improvement'
        : effect < 0
          ? 'Alternative order measured lower improvement'
          : 'No measured difference between the orders'

  return (
    <article className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition duration-200 hover:-translate-y-0.5 hover:shadow-lg">
      <div className="border-b border-slate-200 bg-gradient-to-r from-slate-50 via-white to-blue-50/40 px-6 py-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <SectionEyebrow tone="default">M16.2 experiment</SectionEyebrow>

            <div className="mt-2 flex flex-wrap items-center gap-3">
              <h3 className="text-lg font-semibold text-slate-950">
                Recommendation #{experiment.recommendation_id}
              </h3>

              <span className="rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs font-medium text-slate-500">
                {experiment.column_count} columns
              </span>
            </div>

            <p className="mt-1 text-sm text-slate-500">
              Controlled comparison of composite-index column order.
            </p>
          </div>

          <div
            className={`rounded-xl border px-4 py-3 ${
              effect !== null && effect < 0
                ? 'border-rose-200 bg-rose-50'
                : effect > 0
                  ? 'border-emerald-200 bg-emerald-50'
                  : 'border-slate-200 bg-white'
            }`}
          >
            <p className="text-[0.62rem] font-semibold uppercase tracking-[0.14em] text-slate-400">
              Order effect
            </p>

            <p
              className={`mt-1 text-xl font-semibold ${effectTone(effect)}`}
            >
              {formatEffect(effect)}
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-6 p-6">
        <div className="grid gap-5 lg:grid-cols-2">
          <div>
            <div className="mb-3 flex items-center justify-between">
              <p className="text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-slate-400">
                Original order
              </p>

              <span className="text-xs text-slate-400">Tested</span>
            </div>

            <ColumnOrder
              columns={experiment.original_order}
              emphasized
            />
          </div>

          <div>
            <div className="mb-3 flex items-center justify-between">
              <p className="text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-slate-400">
                Alternative order
              </p>

              <span className="text-xs text-slate-400">Tested</span>
            </div>

            <ColumnOrder columns={experiment.alternative_order} />
          </div>
        </div>

        <div className="grid gap-4 border-t border-slate-100 pt-5 sm:grid-cols-3">
          <KpiCard
            label="Original improvement"
            value={formatPercent(experiment.original_improvement_percent)}
            tone={
              experiment.original_improvement_percent > 0
                ? 'success'
                : experiment.original_improvement_percent < 0
                  ? 'danger'
                  : 'default'
            }
          />

          <KpiCard
            label="Alternative improvement"
            value={formatPercent(experiment.alternative_improvement_percent)}
            tone={
              experiment.alternative_improvement_percent > 0
                ? 'success'
                : experiment.alternative_improvement_percent < 0
                  ? 'danger'
                  : 'default'
            }
          />

          <KpiCard
            label="Order effect"
            value={formatEffect(effect)}
            tone={
              effect > 0
                ? 'success'
                : effect < 0
                  ? 'danger'
                  : 'default'
            }
          />
        </div>

        <div className="grid gap-5 lg:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4">
            <div className="mb-4 flex items-center justify-between">
              <p className="text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-slate-400">
                Measured improvement
              </p>

              <span className="text-xs text-slate-400">0–100%</span>
            </div>

            <div className="space-y-4">
              <ImprovementBar
                label="Original"
                value={experiment.original_improvement_percent}
              />

              <ImprovementBar
                label="Alternative"
                value={experiment.alternative_improvement_percent}
              />
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-4">
            <p className="text-[0.68rem] font-semibold uppercase tracking-[0.14em] text-slate-400">
              Experimental checks
            </p>

            <div className="mt-4 grid gap-3 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3">
              <div>
                <p className="text-xs text-slate-400">Original index</p>
                <div className="mt-2">
                  <UsageBadge used={experiment.original_index_used} />
                </div>
              </div>

              <div>
                <p className="text-xs text-slate-400">Alternative index</p>
                <div className="mt-2">
                  <UsageBadge used={experiment.alternative_index_used} />
                </div>
              </div>

              <div>
                <p className="text-xs text-slate-400">Rows preserved</p>
                <p className="mt-2 text-sm font-semibold text-slate-800">
                  {experiment.original_rows_preserved &&
                  experiment.alternative_rows_preserved
                    ? 'Yes — both variants'
                    : 'Evidence differs'}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-blue-100 bg-blue-50/50 px-4 py-3">
          <p className="text-xs font-medium text-blue-900">
            {effectDescription}
          </p>

          <p className="mt-1 text-xs leading-5 text-blue-700">
            The order effect is the measured percentage-point difference
            between the original and alternative experimental results.
          </p>
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

    const negativeEffects = experiments.filter(
      (experiment) =>
        experiment.order_effect_percentage_points !== null &&
        experiment.order_effect_percentage_points < 0,
    ).length

    const positiveEffects = experiments.filter(
      (experiment) =>
        experiment.order_effect_percentage_points !== null &&
        experiment.order_effect_percentage_points > 0,
    ).length

    return {
      total: experiments.length,
      twoColumn,
      threeColumn,
      originalUsed,
      alternativeUsed,
      negativeEffects,
      positiveEffects,
    }
  }, [experiments])

  return (
    <main className="space-y-8">
      <section className="relative overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="absolute right-0 top-0 h-32 w-64 rounded-bl-full bg-gradient-to-bl from-violet-100/70 to-transparent" />

        <div className="relative flex flex-col gap-6 px-7 py-7 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <SectionEyebrow tone="default">
              Evaluation intelligence
            </SectionEyebrow>

            <h1 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
              Composite Index Intelligence
            </h1>

            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
              Controlled M16.2 evidence comparing alternative column orders for
              composite indexes across the tested query patterns.
            </p>
          </div>

          <div className="relative min-w-[170px] rounded-2xl border border-violet-200 bg-white p-5 shadow-sm">
            <p className="text-[0.65rem] font-semibold uppercase tracking-[0.16em] text-slate-400">
              Inventory
            </p>

            <p className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">
              {summary.total}
            </p>

            <p className="mt-1 text-xs text-slate-400">
              evaluated order comparisons
            </p>
          </div>
        </div>
      </section>

      {loading && (
        <div className="rounded-2xl border border-slate-200 bg-white p-8 text-sm text-slate-500 shadow-sm">
          Loading composite index evidence…
        </div>
      )}

      {error && !loading && (
        <div className="rounded-2xl border border-rose-200 bg-rose-50 p-6">
          <p className="text-sm font-semibold text-rose-800">
            Unable to load composite index evidence.
          </p>

          <p className="mt-1 text-sm text-rose-700">{error}</p>
        </div>
      )}

      {!loading && !error && (
        <>
          <section>
            <div className="mb-4">
              <SectionEyebrow tone="default">Evidence snapshot</SectionEyebrow>

              <h2 className="mt-2 text-xl font-semibold text-slate-950">
                Composite-order experiment overview
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Summary of the established M16.2 comparison evidence.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
              <KpiCard
                label="Evaluated"
                value={summary.total}
                description="Established M16.2 comparisons"
                tone="default"
              />

              <KpiCard
                label="Two-column"
                value={summary.twoColumn}
                description="Two-column order tests"
                tone="default"
              />

              <KpiCard
                label="Three-column"
                value={summary.threeColumn}
                description="Three-column order tests"
                tone="default"
              />

              <KpiCard
                label="Original used"
                value={`${summary.originalUsed}/${summary.total}`}
                description="Original variants used"
                tone="default"
              />

              <KpiCard
                label="Alternative used"
                value={`${summary.alternativeUsed}/${summary.total}`}
                description="Alternative variants used"
                tone="default"
              />
            </div>
          </section>

          <section>
            <div className="mb-4">
              <SectionEyebrow tone="default">
                Order-effect overview
              </SectionEyebrow>

              <h2 className="mt-2 text-xl font-semibold text-slate-950">
                What changed when column order changed?
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Percentage-point differences measured between the tested
                original and alternative orders.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <p className="text-[0.68rem] font-semibold uppercase tracking-[0.15em] text-slate-400">
                  Positive effects
                </p>

                <p className="mt-3 text-3xl font-semibold text-emerald-600">
                  {summary.positiveEffects}
                </p>

                <p className="mt-2 text-xs leading-5 text-slate-400">
                  Alternative order measured higher improvement.
                </p>
              </div>

              <div className="rounded-2xl border border-rose-200 bg-white p-5 shadow-sm">
                <p className="text-[0.68rem] font-semibold uppercase tracking-[0.15em] text-slate-400">
                  Negative effects
                </p>

                <p className="mt-3 text-3xl font-semibold text-rose-600">
                  {summary.negativeEffects}
                </p>

                <p className="mt-2 text-xs leading-5 text-slate-400">
                  Alternative order measured lower improvement.
                </p>
              </div>

              <div className="rounded-2xl border border-blue-200 bg-blue-50/50 p-5 shadow-sm">
                <p className="text-[0.68rem] font-semibold uppercase tracking-[0.15em] text-blue-500">
                  Evidence source
                </p>

                <p className="mt-3 text-3xl font-semibold text-blue-900">
                  M16.2
                </p>

                <p className="mt-2 text-xs leading-5 text-blue-700">
                  Stored experimental comparison results.
                </p>
              </div>
            </div>
          </section>

          <section>
            <div className="mb-4">
              <SectionEyebrow tone="default">
                Column-order experiments
              </SectionEyebrow>

              <h2 className="mt-2 text-xl font-semibold text-slate-950">
                Original versus alternative order
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Each card reports the measured results for one controlled
                comparison.
              </p>
            </div>

            <div className="space-y-5">
              {experiments.map((experiment) => (
                <CompositeExperimentCard
                  key={experiment.recommendation_id}
                  experiment={experiment}
                />
              ))}
            </div>
          </section>

          <section className="rounded-2xl border border-amber-200 bg-gradient-to-r from-amber-50/70 via-white to-white p-6 shadow-sm">
            <SectionEyebrow tone="warning">Evidence boundary</SectionEyebrow>

            <h2 className="mt-3 text-base font-semibold text-slate-950">
              How to interpret composite-index order evidence
            </h2>

            <p className="mt-2 max-w-4xl text-sm leading-6 text-slate-600">
              These results describe the tested queries, database state, data,
              planner, cache, and experimental conditions. They demonstrate
              that column order can affect measured performance in the tested
              cases, but they do not establish a universal optimal column
              order.
            </p>

            <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-slate-400">
              <span className="rounded-full border border-slate-200 bg-white px-3 py-1.5">
                Evidence source: M16.2
              </span>

              <span className="rounded-full border border-slate-200 bg-white px-3 py-1.5">
                Reporting only
              </span>

              <span className="rounded-full border border-slate-200 bg-white px-3 py-1.5">
                No permanent indexes created
              </span>
            </div>
          </section>
        </>
      )}
    </main>
  )
}

export default CompositeIndexesPage

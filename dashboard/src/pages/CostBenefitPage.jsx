import { useEffect, useMemo, useState } from 'react'

import { getCostBenefits } from '../api/client'
import StatusBadge from '../components/common/StatusBadge'

function formatPercent(value) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return `${Number(value).toFixed(2)}%`
}

function formatMilliseconds(value) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return `${Number(value).toFixed(3)} ms`
}

function formatBytes(value) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return `${Number(value).toLocaleString()} bytes`
}

function SummaryCard({ label, value, description }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-2xl font-semibold text-slate-900">
        {value}
      </p>

      {description && (
        <p className="mt-1 text-xs text-slate-500">
          {description}
        </p>
      )}
    </div>
  )
}

function MetricCard({ label, value, description }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-xl font-semibold text-slate-900">
        {value}
      </p>

      {description && (
        <p className="mt-1 text-xs text-slate-500">
          {description}
        </p>
      )}
    </div>
  )
}

function ExperimentRow({ experiment }) {
  return (
    <tr className="border-t border-slate-100">
      <td className="px-4 py-4">
        <p className="font-mono text-xs font-semibold text-slate-800">
          {experiment.experiment_id}
        </p>
      </td>

      <td className="px-4 py-4 text-sm text-slate-700">
        {experiment.recommendation_id ?? 'Not available'}
      </td>

      <td className="px-4 py-4">
        <div className="space-y-1 text-xs text-slate-600">
          <p>
            Average:{' '}
            <strong className="text-slate-800">
              {formatPercent(
                experiment.read.average_improvement_percent,
              )}
            </strong>
          </p>

          <p>
            Median:{' '}
            <strong className="text-slate-800">
              {formatPercent(
                experiment.read.median_improvement_percent,
              )}
            </strong>
          </p>

          <p>
            Saved:{' '}
            <strong className="text-slate-800">
              {formatMilliseconds(experiment.read.savings_ms)}
            </strong>
          </p>
        </div>
      </td>

      <td className="px-4 py-4">
        <div className="space-y-1 text-xs text-slate-600">
          <p>
            Ratio:{' '}
            <strong className="text-slate-800">
              {formatPercent(experiment.storage.ratio_percent)}
            </strong>
          </p>

          <p>
            Index size:{' '}
            <strong className="text-slate-800">
              {formatBytes(
                experiment.storage.index_size_bytes,
              )}
            </strong>
          </p>
        </div>
      </td>

      <td className="px-4 py-4">
        <div className="space-y-1 text-xs text-slate-600">
          <p>
            Average:{' '}
            <strong className="text-slate-800">
              {formatPercent(
                experiment.write.average_overhead_percent,
              )}
            </strong>
          </p>

          <p>
            Median:{' '}
            <strong className="text-slate-800">
              {formatPercent(
                experiment.write.median_overhead_percent,
              )}
            </strong>
          </p>
        </div>
      </td>

      <td className="px-4 py-4">
        <StatusBadge value={experiment.evidence_status} />
      </td>
    </tr>
  )
}

function CostBenefitPage() {
  const [experiments, setExperiments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true

    async function loadCostBenefits() {
      try {
        setLoading(true)
        setError(null)

        const data = await getCostBenefits()

        if (mounted) {
          setExperiments(data)
        }
      } catch (requestError) {
        if (mounted) {
          setError(requestError.message)
        }
      } finally {
        if (mounted) {
          setLoading(false)
        }
      }
    }

    loadCostBenefits()

    return () => {
      mounted = false
    }
  }, [])

  const summary = useMemo(() => {
    const complete = experiments.filter(
      (experiment) => experiment.evidence_status === 'COMPLETE',
    )

    const improvements = complete
      .map(
        (experiment) =>
          experiment.read.average_improvement_percent,
      )
      .filter(
        (value) => value !== null && value !== undefined,
      )

    const storageRatios = complete
      .map(
        (experiment) => experiment.storage.ratio_percent,
      )
      .filter(
        (value) => value !== null && value !== undefined,
      )

    const average = (values) =>
      values.length > 0
        ? values.reduce((sum, value) => sum + Number(value), 0) /
          values.length
        : null

    return {
      total: experiments.length,
      complete: complete.length,
      averageImprovement: average(improvements),
      averageStorageRatio: average(storageRatios),
    }
  }, [experiments])

  if (loading) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm text-slate-500">
          Loading cost-benefit evidence...
        </p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-white p-8 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">
          Unable to load cost-benefit evidence
        </h3>

        <p className="mt-2 text-sm text-slate-500">
          The reporting API could not be reached.
        </p>

        <p className="mt-3 text-xs text-red-600">
          {error}
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <section>
        <h3 className="text-lg font-semibold text-slate-900">
          Cost &amp; Benefit
        </h3>

        <p className="mt-1 text-sm text-slate-500">
          Controlled read-benefit, storage, and write-impact
          evidence from explicitly linked experiments.
        </p>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <SummaryCard
          label="Linked Experiments"
          value={summary.total}
          description="Explicitly linked M18 evidence"
        />

        <SummaryCard
          label="Complete Evidence"
          value={summary.complete}
          description="Evidence status COMPLETE"
        />

        <SummaryCard
          label="Average Read Improvement"
          value={formatPercent(summary.averageImprovement)}
          description="Across available complete evidence"
        />

        <SummaryCard
          label="Average Storage Ratio"
          value={formatPercent(summary.averageStorageRatio)}
          description="Index size relative to table size"
        />
      </section>

      <section>
        <div className="mb-3">
          <h4 className="text-sm font-semibold text-slate-900">
            Read Benefit
          </h4>

          <p className="mt-1 text-xs text-slate-500">
            Measured performance benefit from the linked
            controlled experiments.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {experiments.map((experiment) => (
            <MetricCard
              key={`${experiment.experiment_id}-read`}
              label={experiment.experiment_id}
              value={formatPercent(
                experiment.read.average_improvement_percent,
              )}
              description={`Median ${formatPercent(
                experiment.read.median_improvement_percent,
              )} · Saved ${formatMilliseconds(
                experiment.read.savings_ms,
              )}`}
            />
          ))}
        </div>
      </section>

      <section>
        <div className="mb-3">
          <h4 className="text-sm font-semibold text-slate-900">
            Cost Impact
          </h4>

          <p className="mt-1 text-xs text-slate-500">
            Storage and write-impact evidence associated with
            the same linked experiments.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {experiments.map((experiment) => (
            <div
              key={`${experiment.experiment_id}-cost`}
              className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold text-slate-900">
                  {experiment.experiment_id}
                </h4>

                <StatusBadge
                  value={experiment.evidence_status}
                />
              </div>

              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <MetricCard
                  label="Storage Ratio"
                  value={formatPercent(
                    experiment.storage.ratio_percent,
                  )}
                  description={`Index size: ${formatBytes(
                    experiment.storage.index_size_bytes,
                  )}`}
                />

                <MetricCard
                  label="Average Write Overhead"
                  value={formatPercent(
                    experiment.write.average_overhead_percent,
                  )}
                  description={`Median: ${formatPercent(
                    experiment.write.median_overhead_percent,
                  )}`}
                />
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-100 px-5 py-4">
          <h4 className="text-sm font-semibold text-slate-900">
            Experiment Evidence
          </h4>

          <p className="mt-1 text-xs text-slate-500">
            Values are presented directly from the reporting API.
            Missing evidence is shown as unavailable.
          </p>
        </div>

        {experiments.length === 0 ? (
          <div className="p-6">
            <p className="text-sm text-slate-500">
              No linked cost-benefit experiments are available.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                  <th className="px-4 py-3">
                    Experiment
                  </th>

                  <th className="px-4 py-3">
                    Recommendation
                  </th>

                  <th className="px-4 py-3">
                    Read Benefit
                  </th>

                  <th className="px-4 py-3">
                    Storage
                  </th>

                  <th className="px-4 py-3">
                    Write Impact
                  </th>

                  <th className="px-4 py-3">
                    Evidence
                  </th>
                </tr>
              </thead>

              <tbody>
                {experiments.map((experiment) => (
                  <ExperimentRow
                    key={experiment.experiment_id}
                    experiment={experiment}
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}

export default CostBenefitPage

import { useEffect, useMemo, useState } from 'react'

import { getWorkloads } from '../api/client'
import StatusBadge from '../components/common/StatusBadge'
import PerformanceAnalytics from '../components/workloads/PerformanceAnalytics'
import WorkloadTable from '../components/workloads/WorkloadTable'

function formatMilliseconds(value) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return `${Number(value).toFixed(3)} ms`
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

function WorkloadsPage({ onSelectRecommendation }) {
  const [workloads, setWorkloads] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true

    async function loadWorkloads() {
      try {
        setLoading(true)
        setError(null)

        const data = await getWorkloads()

        if (mounted) {
          setWorkloads(data)
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

    loadWorkloads()

    return () => {
      mounted = false
    }
  }, [])

  const summary = useMemo(() => {
    const totalExecutionTime = workloads.reduce(
      (sum, workload) =>
        sum + (workload.total_execution_time_ms || 0),
      0,
    )

    return {
      total: workloads.length,
      critical: workloads.filter(
        (workload) => workload.priority === 'Critical',
      ).length,
      high: workloads.filter(
        (workload) => workload.priority === 'High',
      ).length,
      moderate: workloads.filter(
        (workload) => workload.priority === 'Moderate',
      ).length,
      totalExecutionTime,
    }
  }, [workloads])

  if (loading) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm text-slate-500">
          Loading workloads...
        </p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-white p-8 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900">
          Unable to load workloads
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
          Workload Explorer
        </h3>

        <p className="mt-1 text-sm text-slate-500">
          Query fingerprints grouped by structural similarity and
          ranked by workload execution time.
        </p>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <SummaryCard
          label="Workload Patterns"
          value={summary.total}
          description="Structural fingerprints"
        />

        <SummaryCard
          label="Critical"
          value={summary.critical}
          description="50% or more of execution time"
        />

        <SummaryCard
          label="High"
          value={summary.high}
          description="10% to under 50%"
        />

        <SummaryCard
          label="Moderate"
          value={summary.moderate}
          description="5% to under 10%"
        />

        <SummaryCard
          label="Total Execution Time"
          value={formatMilliseconds(summary.totalExecutionTime)}
          description="Across profiled workloads"
        />
      </section>

      {workloads.length > 0 && (
        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h4 className="text-sm font-semibold text-slate-900">
                Highest workload concentration
              </h4>

              <p className="mt-1 text-xs text-slate-500">
                The workload list is ordered by total execution time.
              </p>
            </div>

            <StatusBadge value={workloads[0].priority} />
          </div>

          <div className="mt-4 rounded-lg bg-slate-50 p-4">
            <p className="font-mono text-xs leading-5 text-slate-700">
              {workloads[0].template}
            </p>

            <div className="mt-3 flex flex-wrap gap-x-6 gap-y-2 text-xs text-slate-500">
              <span>
                Executions:{' '}
                <strong className="text-slate-700">
                  {workloads[0].execution_count}
                </strong>
              </span>

              <span>
                Time share:{' '}
                <strong className="text-slate-700">
                  {Number(workloads[0].time_share).toFixed(2)}%
                </strong>
              </span>

              <span>
                Total time:{' '}
                <strong className="text-slate-700">
                  {formatMilliseconds(
                    workloads[0].total_execution_time_ms,
                  )}
                </strong>
              </span>
            </div>
          </div>
        </section>
      )}

      <PerformanceAnalytics workloads={workloads} />

      <WorkloadTable
        workloads={workloads}
        onSelectRecommendation={onSelectRecommendation}
      />
    </div>
  )
}

export default WorkloadsPage

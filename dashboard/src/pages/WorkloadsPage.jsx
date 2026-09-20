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

function SummaryCard({
  label,
  value,
  description,
  accent = 'blue',
}) {
  const accents = {
    blue: 'before:bg-blue-500',
    violet: 'before:bg-violet-500',
    cyan: 'before:bg-cyan-500',
    emerald: 'before:bg-emerald-500',
    slate: 'before:bg-slate-400',
  }

  return (
    <article
      className={`dashboard-card-interactive relative overflow-hidden rounded-xl border border-slate-200 bg-white p-5 before:absolute before:inset-x-0 before:top-0 before:h-0.5 ${accents[accent] || accents.blue}`}
    >
      <div className="flex items-start justify-between gap-3">
        <p className="text-[0.65rem] font-bold uppercase tracking-[0.1em] text-slate-400">
          {label}
        </p>

        <span
          className={`mt-1 h-2 w-2 shrink-0 rounded-full ${
            accent === 'violet'
              ? 'bg-violet-400'
              : accent === 'cyan'
                ? 'bg-cyan-400'
                : accent === 'emerald'
                  ? 'bg-emerald-400'
                  : accent === 'slate'
                    ? 'bg-slate-400'
                    : 'bg-blue-400'
          }`}
        />
      </div>

      <p className="mt-3 text-2xl font-bold tracking-tight text-slate-950">
        {value}
      </p>

      {description && (
        <p className="mt-1.5 text-xs leading-5 text-slate-400">
          {description}
        </p>
      )}
    </article>
  )
}

function WorkloadConcentration({ workload }) {
  const timeShare = Math.max(
    0,
    Math.min(Number(workload.time_share) || 0, 100),
  )

  return (
    <section className="dashboard-card overflow-hidden">
      <div className="border-b border-slate-100 bg-gradient-to-r from-blue-50/70 via-white to-cyan-50/40 px-6 py-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-blue-500 shadow-[0_0_0_4px_rgba(59,130,246,0.10)]" />

              <p className="text-[0.65rem] font-bold uppercase tracking-[0.1em] text-blue-600">
                Workload concentration
              </p>
            </div>

            <h3 className="mt-2 text-base font-bold tracking-[-0.01em] text-slate-950">
              Highest execution-time workload
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              The leading workload pattern by total profiled execution time.
            </p>
          </div>

          <StatusBadge value={workload.priority} />
        </div>
      </div>

      <div className="p-6">
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_240px] lg:items-center">
          <div className="min-w-0">
            <div className="flex items-end justify-between gap-4">
              <div>
                <p className="text-[0.65rem] font-bold uppercase tracking-[0.1em] text-slate-400">
                  Time share
                </p>

                <p className="mt-1 text-4xl font-bold tracking-[-0.04em] text-slate-950">
                  {timeShare.toFixed(2)}%
                </p>
              </div>

              <p className="pb-1 text-xs font-medium text-slate-400">
                of profiled execution time
              </p>
            </div>

            <div className="mt-4 h-3 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-400 transition-all duration-500"
                style={{ width: `${timeShare}%` }}
              />
            </div>

            <div className="mt-5 rounded-xl border border-slate-200 bg-slate-950 p-4">
              <div className="mb-2 flex items-center justify-between gap-3">
                <p className="text-[0.62rem] font-bold uppercase tracking-[0.1em] text-slate-400">
                  Query pattern
                </p>

                <span className="rounded-md bg-white/10 px-2 py-1 text-[0.58rem] font-bold uppercase tracking-[0.08em] text-slate-400">
                  Fingerprinted
                </span>
              </div>

              <p className="break-words font-mono text-xs leading-6 text-slate-200">
                {workload.template}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 lg:grid-cols-1">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-[0.6rem] font-bold uppercase tracking-[0.08em] text-slate-400">
                Executions
              </p>

              <p className="mt-2 text-xl font-bold text-slate-950">
                {workload.execution_count}
              </p>
            </div>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <p className="text-[0.6rem] font-bold uppercase tracking-[0.08em] text-slate-400">
                Frequency share
              </p>

              <p className="mt-2 text-xl font-bold text-slate-950">
                {Number(workload.frequency_share).toFixed(2)}%
              </p>
            </div>

            <div className="col-span-2 rounded-xl border border-slate-200 bg-slate-50 p-4 lg:col-span-1">
              <p className="text-[0.6rem] font-bold uppercase tracking-[0.08em] text-slate-400">
                Total execution time
              </p>

              <p className="mt-2 text-xl font-bold text-slate-950">
                {formatMilliseconds(workload.total_execution_time_ms)}
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
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
      <div className="dashboard-card p-8">
        <div className="flex items-center gap-3">
          <span className="h-2 w-2 animate-pulse rounded-full bg-blue-500" />

          <p className="text-sm font-medium text-slate-500">
            Loading workloads...
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-rose-200 bg-white p-8 shadow-sm">
        <div className="flex items-start gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-rose-50 font-bold text-rose-600">
            !
          </div>

          <div>
            <h3 className="text-lg font-bold text-slate-950">
              Unable to load workloads
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              The reporting API could not be reached.
            </p>

            <p className="mt-3 rounded-lg bg-rose-50 px-3 py-2 text-xs text-rose-700">
              {error}
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-7">
      <section className="dashboard-page-header">
        <div className="relative z-10 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="mb-2 flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-cyan-500 shadow-[0_0_0_4px_rgba(6,182,212,0.10)]" />

              <span className="text-[0.68rem] font-bold uppercase tracking-[0.12em] text-cyan-600">
                Workload intelligence
              </span>
            </div>

            <h1 className="text-[1.7rem] font-bold tracking-[-0.03em] text-slate-950">
              Workload Explorer
            </h1>

            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
              Query fingerprints grouped by structural similarity and ranked
              by workload execution time.
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white/85 px-4 py-3 shadow-sm backdrop-blur">
            <p className="text-[0.62rem] font-bold uppercase tracking-[0.1em] text-slate-400">
              Inventory
            </p>

            <p className="mt-1 text-xl font-bold tracking-tight text-slate-900">
              {summary.total}
            </p>

            <p className="text-[0.68rem] text-slate-400">
              workload patterns
            </p>
          </div>
        </div>
      </section>

      <section>
        <div className="mb-4">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-blue-500" />

            <h2 className="text-base font-bold tracking-[-0.01em] text-slate-950">
              Workload snapshot
            </h2>
          </div>

          <p className="mt-1 text-sm text-slate-500">
            Current workload concentration and priority classification.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
          <SummaryCard
            label="Workload patterns"
            value={summary.total}
            description="Structural fingerprints"
            accent="blue"
          />

          <SummaryCard
            label="Critical"
            value={summary.critical}
            description="50% or more of execution time"
            accent="violet"
          />

          <SummaryCard
            label="High"
            value={summary.high}
            description="10% to under 50%"
            accent="cyan"
          />

          <SummaryCard
            label="Moderate"
            value={summary.moderate}
            description="5% to under 10%"
            accent="slate"
          />

          <SummaryCard
            label="Total execution time"
            value={formatMilliseconds(summary.totalExecutionTime)}
            description="Across profiled workloads"
            accent="emerald"
          />
        </div>
      </section>

      {workloads.length > 0 && (
        <WorkloadConcentration workload={workloads[0]} />
      )}

      <PerformanceAnalytics workloads={workloads} />

      <section>
        <div className="mb-4">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-violet-500" />

            <h2 className="text-base font-bold tracking-[-0.01em] text-slate-950">
              Workload inventory
            </h2>
          </div>

          <p className="mt-1 text-sm text-slate-500">
            Detailed workload fingerprints and execution metrics.
          </p>
        </div>

        <WorkloadTable
          workloads={workloads}
          onSelectRecommendation={onSelectRecommendation}
        />
      </section>
    </div>
  )
}

export default WorkloadsPage

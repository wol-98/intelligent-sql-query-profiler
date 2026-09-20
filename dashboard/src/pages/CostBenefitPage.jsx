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

function clampPercentage(value) {
  if (value === null || value === undefined) {
    return 0
  }

  return Math.max(0, Math.min(100, Number(value)))
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
    <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.18em] text-slate-400">
      <span className={`h-2 w-2 rounded-full ${tones[tone]}`} />
      {children}
    </div>
  )
}

function PageHeader({ total }) {
  return (
    <section className="relative overflow-hidden rounded-2xl border border-slate-200 bg-white px-7 py-7 shadow-sm">
      <div className="absolute right-0 top-0 h-32 w-56 bg-gradient-to-bl from-cyan-50 via-blue-50/40 to-transparent" />

      <div className="relative flex flex-col gap-6 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <SectionEyebrow tone="cyan">Evaluation intelligence</SectionEyebrow>

          <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-950">
            Cost &amp; Benefit Intelligence
          </h2>

          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
            Read-performance benefit, storage footprint, and write-maintenance
            evidence from explicitly linked controlled experiments.
          </p>
        </div>

        <div className="relative min-w-[170px] rounded-xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
          <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-slate-400">
            Linked evidence
          </p>

          <p className="mt-1 text-3xl font-bold tracking-tight text-slate-950">
            {total}
          </p>

          <p className="mt-1 text-xs text-slate-400">
            M18 experiments available
          </p>
        </div>
      </div>
    </section>
  )
}

function SummaryCard({
  label,
  value,
  description,
  tone = 'blue',
}) {
  const tones = {
    blue: 'border-blue-400',
    cyan: 'border-cyan-400',
    violet: 'border-violet-400',
    emerald: 'border-emerald-400',
    amber: 'border-amber-400',
  }

  return (
    <article
      className={`relative overflow-hidden rounded-xl border border-slate-200 border-l-4 ${tones[tone]} bg-white p-5 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md`}
    >
      <div className="flex items-start justify-between gap-3">
        <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-slate-400">
          {label}
        </p>

        <span
          className={`h-2 w-2 rounded-full ${
            tone === 'cyan'
              ? 'bg-cyan-400'
              : tone === 'violet'
                ? 'bg-violet-400'
                : tone === 'emerald'
                  ? 'bg-emerald-400'
                  : tone === 'amber'
                    ? 'bg-amber-400'
                    : 'bg-blue-400'
          }`}
        />
      </div>

      <p className="mt-3 text-2xl font-bold tracking-tight text-slate-950">
        {value}
      </p>

      {description && (
        <p className="mt-1 text-xs leading-5 text-slate-400">
          {description}
        </p>
      )}
    </article>
  )
}

function ReadBenefitCard({ experiment }) {
  const improvement = experiment.read.average_improvement_percent
  const improvementWidth = clampPercentage(improvement)

  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="font-mono text-sm font-bold text-slate-950">
            {experiment.experiment_id}
          </p>

          <p className="mt-1 text-xs text-slate-400">
            Recommendation #
            {experiment.recommendation_id ?? 'Not available'}
          </p>
        </div>

        <StatusBadge value={experiment.evidence_status} />
      </div>

      <div className="mt-6">
        <div className="flex items-end justify-between gap-4">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-slate-400">
              Average read improvement
            </p>

            <p className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
              {formatPercent(improvement)}
            </p>
          </div>

          <div className="text-right">
            <p className="text-[10px] font-bold uppercase tracking-[0.15em] text-slate-400">
              Execution-time savings
            </p>

            <p className="mt-2 text-sm font-semibold text-slate-800">
              {formatMilliseconds(experiment.read.savings_ms)}
            </p>
          </div>
        </div>

        <div className="mt-5 h-2 overflow-hidden rounded-full bg-slate-100">
          <div
            className="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-400 transition-all duration-700"
            style={{ width: `${improvementWidth}%` }}
          />
        </div>

        <div className="mt-2 flex items-center justify-between text-[10px] text-slate-400">
          <span>0%</span>
          <span>100%</span>
        </div>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <div className="rounded-lg border border-slate-200 bg-slate-50/70 p-3">
          <p className="text-[9px] font-bold uppercase tracking-[0.14em] text-slate-400">
            Median improvement
          </p>

          <p className="mt-1 text-sm font-semibold text-slate-800">
            {formatPercent(experiment.read.median_improvement_percent)}
          </p>
        </div>

        <div className="rounded-lg border border-slate-200 bg-slate-50/70 p-3">
          <p className="text-[9px] font-bold uppercase tracking-[0.14em] text-slate-400">
            Index usage
          </p>

          <p className="mt-1 text-sm font-semibold text-slate-800">
            {experiment.read.index_used === null ||
            experiment.read.index_used === undefined
              ? 'Not available'
              : experiment.read.index_used
                ? 'Yes'
                : 'No'}
          </p>
        </div>
      </div>
    </article>
  )
}

function CostMetric({
  label,
  value,
  description,
  tone = 'violet',
}) {
  const accent =
    tone === 'amber'
      ? 'border-amber-300 bg-amber-50/40'
      : 'border-violet-300 bg-violet-50/40'

  return (
    <div className={`rounded-xl border p-4 ${accent}`}>
      <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400">
        {label}
      </p>

      <p className="mt-2 text-2xl font-bold tracking-tight text-slate-950">
        {value}
      </p>

      {description && (
        <p className="mt-1 text-xs leading-5 text-slate-400">
          {description}
        </p>
      )}
    </div>
  )
}

function CostProfileCard({ experiment }) {
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <SectionEyebrow tone="violet">Cost profile</SectionEyebrow>

          <h4 className="mt-2 font-mono text-sm font-bold text-slate-950">
            {experiment.experiment_id}
          </h4>

          <p className="mt-1 text-xs text-slate-400">
            Recommendation #
            {experiment.recommendation_id ?? 'Not available'}
          </p>
        </div>

        <StatusBadge value={experiment.evidence_status} />
      </div>

      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <CostMetric
          label="Storage ratio"
          value={formatPercent(experiment.storage.ratio_percent)}
          description={`Index size: ${formatBytes(
            experiment.storage.index_size_bytes,
          )}`}
        />

        <CostMetric
          label="Average write overhead"
          value={formatPercent(
            experiment.write.average_overhead_percent,
          )}
          description={`Median: ${formatPercent(
            experiment.write.median_overhead_percent,
          )}`}
          tone="amber"
        />
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <div className="rounded-lg border border-slate-200 bg-slate-50/70 p-3">
          <p className="text-[9px] font-bold uppercase tracking-[0.14em] text-slate-400">
            Table size
          </p>

          <p className="mt-1 text-xs font-semibold text-slate-700">
            {formatBytes(experiment.storage.table_size_bytes)}
          </p>
        </div>

        <div className="rounded-lg border border-slate-200 bg-slate-50/70 p-3">
          <p className="text-[9px] font-bold uppercase tracking-[0.14em] text-slate-400">
            Median write overhead
          </p>

          <p className="mt-1 text-xs font-semibold text-slate-700">
            {formatPercent(experiment.write.median_overhead_percent)}
          </p>
        </div>
      </div>
    </article>
  )
}

function EvidenceRow({ experiment }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 transition-all duration-200 hover:border-blue-200 hover:shadow-sm">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-3">
            <span className="font-mono text-sm font-bold text-slate-950">
              {experiment.experiment_id}
            </span>

            <StatusBadge value={experiment.evidence_status} />
          </div>

          <p className="mt-1 text-xs text-slate-400">
            Recommendation #
            {experiment.recommendation_id ?? 'Not available'}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:min-w-[620px]">
          <div>
            <p className="text-[9px] font-bold uppercase tracking-[0.12em] text-slate-400">
              Read
            </p>

            <p className="mt-1 text-sm font-bold text-slate-800">
              {formatPercent(
                experiment.read.average_improvement_percent,
              )}
            </p>
          </div>

          <div>
            <p className="text-[9px] font-bold uppercase tracking-[0.12em] text-slate-400">
              Saved
            </p>

            <p className="mt-1 text-sm font-bold text-slate-800">
              {formatMilliseconds(experiment.read.savings_ms)}
            </p>
          </div>

          <div>
            <p className="text-[9px] font-bold uppercase tracking-[0.12em] text-slate-400">
              Storage
            </p>

            <p className="mt-1 text-sm font-bold text-slate-800">
              {formatPercent(experiment.storage.ratio_percent)}
            </p>
          </div>

          <div>
            <p className="text-[9px] font-bold uppercase tracking-[0.12em] text-slate-400">
              Write
            </p>

            <p className="mt-1 text-sm font-bold text-slate-800">
              {formatPercent(
                experiment.write.average_overhead_percent,
              )}
            </p>
          </div>
        </div>
      </div>
    </div>
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
      <div className="rounded-2xl border border-slate-200 bg-white p-10 shadow-sm">
        <div className="flex items-center gap-3">
          <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-cyan-500" />

          <p className="text-sm font-medium text-slate-500">
            Loading cost-benefit evidence...
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-rose-200 bg-white p-8 shadow-sm">
        <SectionEyebrow tone="amber">Reporting error</SectionEyebrow>

        <h3 className="mt-3 text-xl font-bold text-slate-950">
          Unable to load cost-benefit evidence
        </h3>

        <p className="mt-2 text-sm leading-6 text-slate-500">
          The reporting API could not be reached.
        </p>

        <p className="mt-4 rounded-lg bg-rose-50 p-3 font-mono text-xs text-rose-600">
          {error}
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-7">
      <PageHeader total={summary.total} />

      <section>
        <div className="mb-4">
          <SectionEyebrow tone="blue">Evidence snapshot</SectionEyebrow>

          <h3 className="mt-2 text-xl font-bold tracking-tight text-slate-950">
            Linked experiment overview
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Summary of the cost-benefit evidence currently available
            through the reporting API.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <SummaryCard
            label="Linked experiments"
            value={summary.total}
            description="Explicitly linked M18 evidence"
            tone="blue"
          />

          <SummaryCard
            label="Complete evidence"
            value={summary.complete}
            description="Evidence status COMPLETE"
            tone="emerald"
          />

          <SummaryCard
            label="Average read improvement"
            value={formatPercent(summary.averageImprovement)}
            description="Across available complete evidence"
            tone="cyan"
          />

          <SummaryCard
            label="Average storage ratio"
            value={formatPercent(summary.averageStorageRatio)}
            description="Index size relative to table size"
            tone="violet"
          />
        </div>
      </section>

      <section>
        <div className="mb-4">
          <SectionEyebrow tone="cyan">Read performance</SectionEyebrow>

          <h3 className="mt-2 text-xl font-bold tracking-tight text-slate-950">
            Measured read benefit
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Read-performance measurements from the linked controlled
            experiments.
          </p>
        </div>

        {experiments.length === 0 ? (
          <div className="rounded-xl border border-slate-200 bg-white p-8 text-sm text-slate-500 shadow-sm">
            No linked cost-benefit experiments are available.
          </div>
        ) : (
          <div className="grid gap-4 xl:grid-cols-2">
            {experiments.map((experiment) => (
              <ReadBenefitCard
                key={`${experiment.experiment_id}-read`}
                experiment={experiment}
              />
            ))}
          </div>
        )}
      </section>

      <section>
        <div className="mb-4">
          <SectionEyebrow tone="violet">Cost profile</SectionEyebrow>

          <h3 className="mt-2 text-xl font-bold tracking-tight text-slate-950">
            Storage and write-maintenance impact
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Cost evidence associated with the same linked experiments.
          </p>
        </div>

        {experiments.length === 0 ? (
          <div className="rounded-xl border border-slate-200 bg-white p-8 text-sm text-slate-500 shadow-sm">
            No cost evidence is currently available.
          </div>
        ) : (
          <div className="grid gap-4 xl:grid-cols-2">
            {experiments.map((experiment) => (
              <CostProfileCard
                key={`${experiment.experiment_id}-cost`}
                experiment={experiment}
              />
            ))}
          </div>
        )}
      </section>

      <section>
        <div className="mb-4">
          <SectionEyebrow tone="emerald">Evidence register</SectionEyebrow>

          <h3 className="mt-2 text-xl font-bold tracking-tight text-slate-950">
            Experiment evidence
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            A compact register of the measured values associated with each
            linked experiment.
          </p>
        </div>

        <div className="space-y-3">
          {experiments.length === 0 ? (
            <div className="rounded-xl border border-slate-200 bg-white p-8 text-sm text-slate-500 shadow-sm">
              No linked cost-benefit experiments are available.
            </div>
          ) : (
            experiments.map((experiment) => (
              <EvidenceRow
                key={`${experiment.experiment_id}-evidence`}
                experiment={experiment}
              />
            ))
          )}
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-gradient-to-r from-slate-50 to-white p-5 shadow-sm">
        <SectionEyebrow tone="amber">Evidence boundary</SectionEyebrow>

        <h3 className="mt-2 text-sm font-bold text-slate-900">
          How to interpret this page
        </h3>

        <p className="mt-2 max-w-4xl text-xs leading-6 text-slate-500">
          This page reports stored cost-benefit evidence from explicitly
          linked experiments. It does not rerun benchmarks, create or remove
          indexes, recalculate production decisions, or treat missing
          measurements as zero.
        </p>
      </section>
    </div>
  )
}

export default CostBenefitPage

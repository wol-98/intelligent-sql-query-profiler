import EvidenceField from './EvidenceField'
import EvidenceSection from './EvidenceSection'
import StatusBadge from '../../common/StatusBadge'

function formatPercent(value) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return `${value.toFixed(2)}%`
}

function CostEvidence({ recommendation }) {
  const cost = recommendation.cost

  return (
    <EvidenceSection
      eyebrow="04 · Cost & benefit"
      title="Cost & benefit evidence"
      description="Storage and write-maintenance evidence linked to the recommendation."
      accent="blue"
    >
      <div className="mb-5 flex flex-wrap items-center gap-3">
        <StatusBadge value={cost.evidence_status} />

        <span className="text-xs text-slate-400">
          Cost evidence availability
        </span>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <EvidenceField
          label="Index storage ratio"
          value={formatPercent(cost.storage_ratio_percent)}
          emphasize
        />

        <EvidenceField
          label="Average write overhead"
          value={formatPercent(cost.write_overhead_percent)}
        />

        <EvidenceField
          label="Median write overhead"
          value={formatPercent(cost.median_write_overhead_percent)}
        />
      </div>

      <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
        <p className="text-[0.62rem] font-bold uppercase tracking-[0.08em] text-slate-500">
          Evidence boundary
        </p>

        <p className="mt-2 text-sm leading-6 text-slate-600">
          Cost values are reported only when supporting experimental evidence
          is available. Missing cost evidence is shown as unavailable rather
          than interpreted as zero.
        </p>
      </div>
    </EvidenceSection>
  )
}

export default CostEvidence

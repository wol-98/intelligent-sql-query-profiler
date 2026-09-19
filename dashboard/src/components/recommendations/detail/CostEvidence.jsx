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
      title="Cost evidence"
      description="Storage and write-maintenance evidence linked to the recommendation."
    >
      <div className="mb-5">
        <StatusBadge value={cost.evidence_status} />
      </div>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <EvidenceField
          label="Index storage ratio"
          value={formatPercent(cost.storage_ratio_percent)}
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
    </EvidenceSection>
  )
}

export default CostEvidence

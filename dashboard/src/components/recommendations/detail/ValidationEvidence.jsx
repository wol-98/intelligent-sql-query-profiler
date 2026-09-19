import EvidenceField from './EvidenceField'
import EvidenceSection from './EvidenceSection'
import StatusBadge from '../../common/StatusBadge'

function formatPercent(value) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return `${value.toFixed(2)}%`
}

function formatMilliseconds(value) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return `${value.toFixed(3)} ms`
}

function ValidationEvidence({ recommendation }) {
  const validation = recommendation.validation

  return (
    <EvidenceSection
      title="Validation evidence"
      description="Measured experimental evidence from the recommendation benchmark."
    >
      <div className="mb-5 flex flex-wrap gap-2">
        <StatusBadge value={validation.outcome} />

        {validation.index_used !== null &&
          validation.index_used !== undefined && (
            <span className="inline-flex rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600 ring-1 ring-inset ring-slate-200">
              Index {validation.index_used ? 'used' : 'not used'}
            </span>
          )}

        {validation.plan_changed !== null &&
          validation.plan_changed !== undefined && (
            <span className="inline-flex rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600 ring-1 ring-inset ring-slate-200">
              Plan {validation.plan_changed ? 'changed' : 'unchanged'}
            </span>
          )}
      </div>

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <EvidenceField
          label="Average improvement"
          value={formatPercent(validation.improvement)}
        />

        <EvidenceField
          label="Median improvement"
          value={formatPercent(validation.median_improvement)}
        />

        <EvidenceField
          label="Execution-time savings"
          value={formatMilliseconds(validation.savings_ms)}
        />

        <EvidenceField
          label="Rows preserved"
          value={
            validation.rows_preserved === null ||
            validation.rows_preserved === undefined
              ? 'Not available'
              : validation.rows_preserved
                ? 'Yes'
                : 'No'
          }
        />
      </div>
    </EvidenceSection>
  )
}

export default ValidationEvidence

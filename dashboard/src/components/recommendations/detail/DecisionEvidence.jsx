import EvidenceField from './EvidenceField'
import EvidenceSection from './EvidenceSection'
import StatusBadge from '../../common/StatusBadge'

function DecisionEvidence({ recommendation }) {
  const { decision, provenance } = recommendation

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <EvidenceSection
        title="Production decision"
        description="Decision produced by the M19 production optimization framework."
      >
        <div className="grid gap-5 sm:grid-cols-2">
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Decision state
            </p>

            <div className="mt-2">
              <StatusBadge value={decision.state} />
            </div>
          </div>

          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Safety guardrail
            </p>

            <div className="mt-2">
              <StatusBadge value={decision.guardrail} />
            </div>
          </div>
        </div>
      </EvidenceSection>

      <EvidenceSection
        title="Evidence provenance"
        description="Traceability between this recommendation and linked experimental evidence."
      >
        <div className="grid gap-5 sm:grid-cols-2">
          <EvidenceField
            label="Provenance status"
            value={provenance.status}
          />

          <EvidenceField
            label="Evidence status"
            value={provenance.evidence_status}
          />

          <EvidenceField
            label="Linked experiment"
            value={provenance.linked_experiment_id}
            mono
          />
        </div>
      </EvidenceSection>
    </div>
  )
}

export default DecisionEvidence

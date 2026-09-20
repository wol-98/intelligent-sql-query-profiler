import EvidenceField from './EvidenceField'
import EvidenceSection from './EvidenceSection'
import StatusBadge from '../../common/StatusBadge'

function DecisionEvidence({ recommendation }) {
  const { decision, provenance } = recommendation

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <EvidenceSection
        eyebrow="05 · Production framework"
        title="Production decision"
        description="Decision produced by the M19 production optimization framework."
        accent="amber"
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-slate-50/65 p-4">
            <p className="text-[0.62rem] font-bold uppercase tracking-[0.08em] text-slate-400">
              Decision state
            </p>

            <div className="mt-3">
              <StatusBadge value={decision.state} />
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-slate-50/65 p-4">
            <p className="text-[0.62rem] font-bold uppercase tracking-[0.08em] text-slate-400">
              Safety guardrail
            </p>

            <div className="mt-3">
              <StatusBadge value={decision.guardrail} />
            </div>
          </div>
        </div>
      </EvidenceSection>

      <EvidenceSection
        eyebrow="06 · Traceability"
        title="Evidence provenance"
        description="Traceability between this recommendation and linked experimental evidence."
        accent="cyan"
      >
        <div className="grid gap-3 sm:grid-cols-2">
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

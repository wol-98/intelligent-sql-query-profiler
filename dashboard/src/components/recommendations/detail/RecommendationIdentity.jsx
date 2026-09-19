import EvidenceField from './EvidenceField'
import StatusBadge from '../../common/StatusBadge'

function RecommendationIdentity({ recommendation }) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Recommendation #{recommendation.recommendation_id}
          </p>

          <h2 className="mt-1 text-xl font-semibold text-slate-900">
            {recommendation.table_name}
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            {recommendation.columns.length > 0
              ? recommendation.columns.join(', ')
              : 'Column information not available'}
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <StatusBadge value={recommendation.priority?.toUpperCase()} />
          <StatusBadge value={recommendation.decision.state} />
          <StatusBadge value={recommendation.provenance.evidence_status} />
        </div>
      </div>

      <div className="mt-6 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <EvidenceField
          label="Recommendation score"
          value={recommendation.score.toFixed(2)}
        />

        <EvidenceField
          label="Index type"
          value={recommendation.index_type}
        />

        <EvidenceField
          label="Candidate type"
          value={recommendation.candidate_type}
        />

        <EvidenceField
          label="Index name"
          value={recommendation.index_name}
          mono
        />
      </div>

      {recommendation.reason && (
        <div className="mt-6 rounded-lg bg-slate-50 p-4">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Recommendation rationale
          </p>

          <p className="mt-2 text-sm leading-6 text-slate-700">
            {recommendation.reason}
          </p>
        </div>
      )}
    </section>
  )
}

export default RecommendationIdentity

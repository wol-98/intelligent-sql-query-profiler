import EvidenceField from './EvidenceField'
import StatusBadge from '../../common/StatusBadge'

function RecommendationIdentity({ recommendation }) {
  return (
    <section className="dashboard-card relative overflow-hidden p-6">
      <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-blue-500 via-violet-500 to-cyan-500" />

      <div className="relative">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
          <div className="min-w-0">
            <div className="mb-2 flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-blue-500" />

              <p className="text-[0.65rem] font-bold uppercase tracking-[0.1em] text-blue-600">
                Recommendation #{recommendation.recommendation_id}
              </p>
            </div>

            <h2 className="text-[1.45rem] font-bold tracking-[-0.03em] text-slate-950">
              {recommendation.table_name}
            </h2>

            <p className="mt-1.5 text-sm font-medium text-slate-500">
              {recommendation.columns.length > 0
                ? recommendation.columns.join(', ')
                : 'Column information not available'}
            </p>
          </div>

          <div className="flex flex-wrap gap-2 lg:max-w-sm lg:justify-end">
            <StatusBadge
              value={recommendation.priority?.toUpperCase()}
            />

            <StatusBadge value={recommendation.decision.state} />

            <StatusBadge
              value={recommendation.provenance.evidence_status}
            />
          </div>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <EvidenceField
            label="Recommendation score"
            value={recommendation.score.toFixed(2)}
            emphasize
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
          <div className="mt-4 rounded-xl border border-blue-100 bg-blue-50/50 p-4">
            <p className="text-[0.62rem] font-bold uppercase tracking-[0.08em] text-blue-600">
              Recommendation rationale
            </p>

            <p className="mt-2 text-sm leading-6 text-slate-700">
              {recommendation.reason}
            </p>
          </div>
        )}
      </div>
    </section>
  )
}

export default RecommendationIdentity

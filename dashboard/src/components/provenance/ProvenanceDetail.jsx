import StatusBadge from '../common/StatusBadge'

function Metric({ label, value, mono = false }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </p>

      <p
        className={`mt-1 break-all text-sm font-semibold text-slate-900 ${
          mono ? 'font-mono' : ''
        }`}
      >
        {value === null || value === undefined || value === ''
          ? 'Not available'
          : value}
      </p>
    </div>
  )
}

function ProvenanceDetail({ provenance }) {
  if (!provenance) {
    return (
      <section className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm text-slate-500">
          Select a provenance record to inspect its evidence chain.
        </p>
      </section>
    )
  }

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Provenance Detail
            </p>

            <h2 className="mt-1 text-xl font-semibold text-slate-900">
              Recommendation #{provenance.recommendation_id}
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Explicit evidence linkage for this recommendation.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <StatusBadge value={provenance.status} />
            <StatusBadge value={provenance.evidence_status} />
          </div>
        </div>
      </section>

      <section>
        <h3 className="mb-3 text-base font-semibold text-slate-900">
          Evidence Identity
        </h3>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <Metric
            label="Recommendation ID"
            value={`#${provenance.recommendation_id}`}
          />

          <Metric
            label="Query Fingerprint"
            value={provenance.query_fingerprint}
            mono
          />

          <Metric
            label="Index Name"
            value={provenance.index_name}
            mono
          />

          <Metric
            label="Linked Experiment"
            value={provenance.linked_experiment_id}
            mono
          />
        </div>
      </section>

      <section>
        <h3 className="mb-3 text-base font-semibold text-slate-900">
          Provenance Status
        </h3>

        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Linkage
            </p>

            <div className="mt-3">
              <StatusBadge value={provenance.status} />
            </div>

            <p className="mt-3 text-sm leading-6 text-slate-600">
              {provenance.status === 'LINKED'
                ? 'The recommendation has an explicitly established experimental provenance link.'
                : 'An explicit experimental provenance link has not been established.'}
            </p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              Evidence Completeness
            </p>

            <div className="mt-3">
              <StatusBadge value={provenance.evidence_status} />
            </div>

            <p className="mt-3 text-sm leading-6 text-slate-600">
              {provenance.evidence_status === 'COMPLETE'
                ? 'Required provenance evidence is available for the established linkage.'
                : 'Required provenance evidence is not fully established for this recommendation.'}
            </p>
          </div>
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-slate-50 p-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Evidence Boundary
        </p>

        <p className="mt-2 text-sm leading-6 text-slate-600">
          This page reports provenance established by the project evidence
          chain. Query, table, or column similarity is not treated as proof of
          experimental linkage. Missing provenance is reported as unavailable
          rather than inferred.
        </p>
      </section>
    </div>
  )
}

export default ProvenanceDetail

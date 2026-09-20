import StatusBadge from '../common/StatusBadge'

function Metric({ label, value, mono = false }) {
  const available =
    value !== null &&
    value !== undefined &&
    value !== ''

  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-4">
      <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">
        {label}
      </p>

      <p
        className={`mt-2 break-all text-sm font-semibold ${
          available ? 'text-slate-900' : 'text-slate-400'
        } ${mono ? 'font-mono' : ''}`}
      >
        {available ? value : 'Not available'}
      </p>
    </div>
  )
}

function ChainStep({
  number,
  label,
  value,
  available,
  last = false,
}) {
  return (
    <div className="relative flex gap-4">
      <div className="relative flex flex-col items-center">
        <span
          className={`flex h-9 w-9 items-center justify-center rounded-xl text-xs font-bold ${
            available
              ? 'bg-blue-50 text-blue-600 ring-1 ring-blue-100'
              : 'bg-slate-100 text-slate-400'
          }`}
        >
          {number}
        </span>

        {!last && (
          <span className="mt-1 h-full min-h-8 w-px bg-slate-200" />
        )}
      </div>

      <div className="pb-5">
        <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">
          {label}
        </p>

        <p
          className={`mt-1 break-all text-sm font-semibold ${
            available ? 'text-slate-900' : 'text-slate-400'
          }`}
        >
          {available ? value : 'Not available'}
        </p>
      </div>
    </div>
  )
}

function ProvenanceDetail({ provenance }) {
  if (!provenance) {
    return (
      <section className="rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-sm">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-blue-500">
          →
        </div>

        <h3 className="mt-4 text-base font-semibold text-slate-900">
          Select a provenance record
        </h3>

        <p className="mt-2 text-sm text-slate-500">
          Choose a record above to inspect its evidence identity and
          explicitly established provenance chain.
        </p>
      </section>
    )
  }

  const linked = provenance.status === 'LINKED'
  const complete = provenance.evidence_status === 'COMPLETE'

  return (
    <div className="space-y-6">
      {/* Detail header */}
      <section
        className={`relative overflow-hidden rounded-2xl border bg-white p-6 shadow-sm ${
          linked
            ? 'border-cyan-100'
            : 'border-slate-200'
        }`}
      >
        <div
          className={`absolute right-0 top-0 h-32 w-56 rounded-bl-full ${
            linked
              ? 'bg-gradient-to-br from-cyan-50 to-transparent'
              : 'bg-gradient-to-br from-slate-50 to-transparent'
          }`}
        />

        <div className="relative flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-cyan-500">
              Selected evidence
            </p>

            <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950">
              Recommendation #{provenance.recommendation_id}
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Explicit provenance and evidence completeness for this
              recommendation.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <StatusBadge value={provenance.status} />
            <StatusBadge value={provenance.evidence_status} />
          </div>
        </div>
      </section>

      {/* Status */}
      <section className="grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">
            Provenance state
          </p>

          <div className="mt-3">
            <StatusBadge value={provenance.status} />
          </div>

          <p className="mt-4 text-sm leading-6 text-slate-500">
            {linked
              ? 'An explicit experimental provenance link has been established for this recommendation.'
              : 'An explicit experimental provenance link has not been established. Missing linkage is not inferred from similarity.'}
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">
            Evidence completeness
          </p>

          <div className="mt-3">
            <StatusBadge value={provenance.evidence_status} />
          </div>

          <p className="mt-4 text-sm leading-6 text-slate-500">
            {complete
              ? 'The required provenance evidence is available for the established record.'
              : 'The available provenance evidence is not complete enough to establish a complete evidence record.'}
          </p>
        </div>
      </section>

      {/* Chain */}
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-blue-500">
            Evidence chain
          </p>

          <h3 className="mt-2 text-lg font-semibold text-slate-950">
            Trace the experimental identity
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            The chain shows only values explicitly present in the provenance
            record.
          </p>
        </div>

        <div className="mt-6 grid gap-8 lg:grid-cols-2">
          <div>
            <ChainStep
              number="01"
              label="Recommendation"
              value={`#${provenance.recommendation_id}`}
              available
            />

            <ChainStep
              number="02"
              label="Query fingerprint"
              value={provenance.query_fingerprint}
              available={Boolean(provenance.query_fingerprint)}
            />

            <ChainStep
              number="03"
              label="Index identity"
              value={provenance.index_name}
              available={Boolean(provenance.index_name)}
              last
            />
          </div>

          <div>
            <ChainStep
              number="04"
              label="Linked experiment"
              value={provenance.linked_experiment_id}
              available={Boolean(provenance.linked_experiment_id)}
            />

            <div className="rounded-xl border border-blue-100 bg-blue-50/50 p-4">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-blue-500">
                Evidence state
              </p>

              <div className="mt-3 flex flex-wrap gap-2">
                <StatusBadge value={provenance.status} />
                <StatusBadge value={provenance.evidence_status} />
              </div>

              <p className="mt-3 text-xs leading-5 text-slate-500">
                Provenance status and evidence completeness remain separate
                dimensions of the reporting model.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Identity register */}
      <section>
        <p className="mb-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-violet-500">
          Evidence identity
        </p>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Metric
            label="Recommendation ID"
            value={`#${provenance.recommendation_id}`}
          />

          <Metric
            label="Query fingerprint"
            value={provenance.query_fingerprint}
            mono
          />

          <Metric
            label="Index name"
            value={provenance.index_name}
            mono
          />

          <Metric
            label="Linked experiment"
            value={provenance.linked_experiment_id}
            mono
          />
        </div>
      </section>

      {/* Evidence boundary */}
      <section className="rounded-2xl border border-amber-200 bg-gradient-to-r from-amber-50/80 via-white to-white p-6">
        <div className="flex gap-4">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-amber-100 text-amber-600">
            !
          </div>

          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-amber-600">
              Evidence boundary
            </p>

            <h3 className="mt-2 text-base font-semibold text-slate-950">
              How to interpret provenance
            </h3>

            <p className="mt-2 max-w-4xl text-sm leading-6 text-slate-500">
              This interface reports provenance established by the project
              evidence chain. Query, table, or column similarity is not
              treated as proof of experimental linkage. Missing provenance is
              reported as unavailable rather than inferred.
            </p>

            <div className="mt-4 flex flex-wrap gap-2">
              <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-medium text-slate-500">
                Reporting only
              </span>

              <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-medium text-slate-500">
                Explicit linkage required
              </span>

              <span className="rounded-full border border-slate-200 bg-white px-3 py-1 text-[11px] font-medium text-slate-500">
                Missing ≠ zero
              </span>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default ProvenanceDetail

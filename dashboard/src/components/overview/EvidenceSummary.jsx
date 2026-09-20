const evidenceStyles = {
  Complete: {
    accent: 'bg-emerald-500',
    value: 'text-emerald-700',
    background: 'bg-emerald-50',
    description: 'Complete supporting evidence',
  },
  Partial: {
    accent: 'bg-amber-500',
    value: 'text-amber-700',
    background: 'bg-amber-50',
    description: 'Partially available evidence',
  },
  Insufficient: {
    accent: 'bg-slate-400',
    value: 'text-slate-700',
    background: 'bg-slate-100',
    description: 'Evidence not sufficient',
  },
}

function EvidenceItem({ label, value }) {
  const style = evidenceStyles[label]

  return (
    <div className="relative overflow-hidden rounded-xl border border-slate-200 bg-white p-4">
      <div
        className={`absolute bottom-0 left-0 top-0 w-0.5 ${style.accent}`}
      />

      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-slate-700">
            {label}
          </p>

          <p className="mt-1 text-[0.68rem] text-slate-400">
            {style.description}
          </p>
        </div>

        <div
          className={`flex h-10 min-w-10 items-center justify-center rounded-lg px-2 ${style.background}`}
        >
          <span
            className={`text-lg font-bold tracking-[-0.03em] ${style.value}`}
          >
            {value}
          </span>
        </div>
      </div>
    </div>
  )
}

function EvidenceSummary({ evidence }) {
  const items = [
    {
      label: 'Complete',
      value: evidence.complete,
    },
    {
      label: 'Partial',
      value: evidence.partial,
    },
    {
      label: 'Insufficient',
      value: evidence.insufficient,
    },
  ]

  return (
    <section className="dashboard-card p-6">
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <h3 className="dashboard-section-title">
            Evidence coverage
          </h3>

          <p className="dashboard-section-description">
            Availability of evidence supporting recommendation-level analysis.
          </p>
        </div>

        <div className="rounded-lg bg-slate-100 px-2.5 py-1.5 text-[0.65rem] font-semibold text-slate-600">
          COVERAGE
        </div>
      </div>

      <div className="space-y-3">
        {items.map((item) => (
          <EvidenceItem
            key={item.label}
            label={item.label}
            value={item.value}
          />
        ))}
      </div>
    </section>
  )
}

export default EvidenceSummary

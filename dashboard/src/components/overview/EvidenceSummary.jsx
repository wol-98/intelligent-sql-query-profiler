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
    <section>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-slate-900">
          Evidence coverage
        </h3>
        <p className="mt-1 text-sm text-slate-500">
          Availability of evidence supporting recommendation-level analysis.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {items.map((item) => (
          <div
            key={item.label}
            className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
          >
            <p className="text-sm text-slate-500">{item.label}</p>
            <p className="mt-2 text-2xl font-semibold text-slate-900">
              {item.value}
            </p>
          </div>
        ))}
      </div>
    </section>
  )
}

export default EvidenceSummary

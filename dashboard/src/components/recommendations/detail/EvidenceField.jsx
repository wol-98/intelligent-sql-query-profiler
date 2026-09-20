function EvidenceField({ label, value, mono = false, emphasize = false }) {
  const unavailable =
    value === null || value === undefined || value === ''

  const displayValue = unavailable ? 'Not available' : value

  return (
    <div className="min-w-0 rounded-xl border border-slate-200 bg-slate-50/65 p-3.5 transition-colors hover:border-slate-300 hover:bg-slate-50">
      <p className="text-[0.62rem] font-bold uppercase tracking-[0.08em] text-slate-400">
        {label}
      </p>

      <p
        className={`mt-2 break-words leading-5 ${
          mono
            ? 'font-mono text-xs text-slate-700'
            : emphasize
              ? 'text-base font-bold tracking-tight text-slate-950'
              : 'text-sm font-semibold text-slate-800'
        } ${
          unavailable ? 'text-slate-400' : ''
        }`}
      >
        {displayValue}
      </p>
    </div>
  )
}

export default EvidenceField

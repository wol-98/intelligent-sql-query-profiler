function EvidenceField({ label, value, mono = false }) {
  const displayValue =
    value === null || value === undefined || value === ''
      ? 'Not available'
      : value

  return (
    <div>
      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
        {label}
      </p>

      <p
        className={`mt-1 text-sm ${
          mono
            ? 'font-mono text-slate-700'
            : 'font-medium text-slate-800'
        }`}
      >
        {displayValue}
      </p>
    </div>
  )
}

export default EvidenceField

const styles = {
  RECOMMEND: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  REVIEW: 'bg-amber-50 text-amber-700 ring-amber-200',
  REJECT: 'bg-red-50 text-red-700 ring-red-200',
  INSUFFICIENT_EVIDENCE: 'bg-slate-100 text-slate-600 ring-slate-200',

  COMPLETE: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  PARTIAL: 'bg-amber-50 text-amber-700 ring-amber-200',
  INSUFFICIENT: 'bg-slate-100 text-slate-600 ring-slate-200',

  SUCCESS: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  NEUTRAL: 'bg-slate-100 text-slate-600 ring-slate-200',
  UNSUCCESSFUL: 'bg-red-50 text-red-700 ring-red-200',
  UNSAFE: 'bg-red-50 text-red-700 ring-red-200',
}

function formatLabel(value) {
  if (!value) {
    return 'Not available'
  }

  return value
    .toLowerCase()
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

function StatusBadge({ value }) {
  if (!value) {
    return (
      <span className="text-xs text-slate-400">
        Not available
      </span>
    )
  }

  const style =
    styles[value] ?? 'bg-slate-100 text-slate-600 ring-slate-200'

  return (
    <span
      className={`inline-flex whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset ${style}`}
    >
      {formatLabel(value)}
    </span>
  )
}

export default StatusBadge

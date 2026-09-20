const styles = {
  RECOMMEND:
    'border-emerald-200 bg-emerald-50 text-emerald-700',
  REVIEW:
    'border-amber-200 bg-amber-50 text-amber-700',
  REJECT:
    'border-rose-200 bg-rose-50 text-rose-700',
  INSUFFICIENT_EVIDENCE:
    'border-slate-200 bg-slate-100 text-slate-600',

  COMPLETE:
    'border-emerald-200 bg-emerald-50 text-emerald-700',
  PARTIAL:
    'border-amber-200 bg-amber-50 text-amber-700',
  INSUFFICIENT:
    'border-slate-200 bg-slate-100 text-slate-600',

  SUCCESS:
    'border-emerald-200 bg-emerald-50 text-emerald-700',
  NEUTRAL:
    'border-slate-200 bg-slate-100 text-slate-600',
  UNSUCCESSFUL:
    'border-rose-200 bg-rose-50 text-rose-700',
  UNSAFE:
    'border-rose-200 bg-rose-50 text-rose-700',

  PASS:
    'border-emerald-200 bg-emerald-50 text-emerald-700',
  BLOCK:
    'border-rose-200 bg-rose-50 text-rose-700',

  LINKED:
    'border-cyan-200 bg-cyan-50 text-cyan-700',
  NOT_ESTABLISHED:
    'border-slate-200 bg-slate-100 text-slate-600',
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
      <span className="text-xs font-medium text-slate-400">
        Not available
      </span>
    )
  }

  const style =
    styles[value] ??
    'border-slate-200 bg-slate-100 text-slate-600'

  return (
    <span
      className={`inline-flex whitespace-nowrap items-center rounded-full border px-2.5 py-1 text-[0.68rem] font-semibold tracking-wide ${style}`}
    >
      {formatLabel(value)}
    </span>
  )
}

export default StatusBadge

const tones = {
  default: {
    accent: 'bg-blue-600',
    dot: 'bg-blue-600',
  },
  success: {
    accent: 'bg-emerald-500',
    dot: 'bg-emerald-500',
  },
  warning: {
    accent: 'bg-amber-500',
    dot: 'bg-amber-500',
  },
  danger: {
    accent: 'bg-rose-500',
    dot: 'bg-rose-500',
  },
  neutral: {
    accent: 'bg-slate-400',
    dot: 'bg-slate-400',
  },
}

function KpiCard({
  label,
  value,
  description,
  tone = 'default',
  meta,
}) {
  const style = tones[tone] ?? tones.default

  return (
    <article className="dashboard-card dashboard-card-interactive group relative overflow-hidden p-5">
      <div
        className={`absolute inset-x-0 top-0 h-0.5 ${style.accent}`}
        aria-hidden="true"
      />

      <div className="relative">
        <div className="flex items-start justify-between gap-3">
          <p className="text-[0.7rem] font-semibold uppercase tracking-[0.08em] text-slate-500">
            {label}
          </p>

          <span
            className={`mt-1 h-2 w-2 shrink-0 rounded-full ${style.dot}`}
            aria-hidden="true"
          />
        </div>

        <p className="mt-3 text-[2rem] font-bold leading-none tracking-[-0.04em] text-slate-950">
          {value}
        </p>

        {(description || meta) && (
          <div className="mt-3 flex items-center justify-between gap-3">
            {description && (
              <p className="text-xs leading-5 text-slate-400">
                {description}
              </p>
            )}

            {meta && (
              <span className="shrink-0 text-[0.62rem] font-bold uppercase tracking-[0.08em] text-slate-400">
                {meta}
              </span>
            )}
          </div>
        )}
      </div>
    </article>
  )
}

export default KpiCard

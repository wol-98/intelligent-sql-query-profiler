const variants = {
  blue: {
    accent: 'bg-blue-500',
    glow: 'bg-blue-500/10',
    number: 'text-slate-950',
    icon: 'bg-blue-50 text-blue-600',
  },
  violet: {
    accent: 'bg-violet-500',
    glow: 'bg-violet-500/10',
    number: 'text-slate-950',
    icon: 'bg-violet-50 text-violet-600',
  },
  cyan: {
    accent: 'bg-cyan-500',
    glow: 'bg-cyan-500/10',
    number: 'text-slate-950',
    icon: 'bg-cyan-50 text-cyan-600',
  },
  emerald: {
    accent: 'bg-emerald-500',
    glow: 'bg-emerald-500/10',
    number: 'text-slate-950',
    icon: 'bg-emerald-50 text-emerald-600',
  },
  slate: {
    accent: 'bg-slate-400',
    glow: 'bg-slate-400/10',
    number: 'text-slate-950',
    icon: 'bg-slate-100 text-slate-600',
  },
  rose: {
    accent: 'bg-rose-500',
    glow: 'bg-rose-500/10',
    number: 'text-slate-950',
    icon: 'bg-rose-50 text-rose-600',
  },
}

function MetricCard({
  label,
  value,
  description,
  variant = 'blue',
}) {
  const style = variants[variant] ?? variants.blue

  return (
    <article className="dashboard-card dashboard-card-interactive group relative overflow-hidden p-5">
      <div
        className={`absolute inset-x-0 top-0 h-0.5 ${style.accent}`}
      />

      <div
        className={`pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full ${style.glow} opacity-0 blur-2xl transition-opacity duration-300 group-hover:opacity-100`}
      />

      <div className="relative">
        <div className="flex items-start justify-between gap-3">
          <p className="text-[0.7rem] font-semibold uppercase tracking-[0.08em] text-slate-500">
            {label}
          </p>

          <span
            className={`h-2 w-2 rounded-full ${style.accent} opacity-80`}
          />
        </div>

        <p
          className={`mt-3 text-[2rem] font-bold leading-none tracking-[-0.04em] ${style.number}`}
        >
          {value}
        </p>

        {description && (
          <p className="mt-3 text-xs leading-5 text-slate-400">
            {description}
          </p>
        )}
      </div>
    </article>
  )
}

export default MetricCard

function EvidenceSection({
  title,
  description,
  children,
  eyebrow = 'Evidence',
  accent = 'blue',
}) {
  const accents = {
    blue: {
      dot: 'bg-blue-500',
      line: 'bg-blue-500',
      eyebrow: 'text-blue-600',
    },
    violet: {
      dot: 'bg-violet-500',
      line: 'bg-violet-500',
      eyebrow: 'text-violet-600',
    },
    cyan: {
      dot: 'bg-cyan-500',
      line: 'bg-cyan-500',
      eyebrow: 'text-cyan-600',
    },
    emerald: {
      dot: 'bg-emerald-500',
      line: 'bg-emerald-500',
      eyebrow: 'text-emerald-600',
    },
    amber: {
      dot: 'bg-amber-500',
      line: 'bg-amber-500',
      eyebrow: 'text-amber-600',
    },
    slate: {
      dot: 'bg-slate-400',
      line: 'bg-slate-400',
      eyebrow: 'text-slate-500',
    },
  }

  const style = accents[accent] ?? accents.blue

  return (
    <section className="dashboard-card relative overflow-hidden p-6">
      <div
        className={`absolute bottom-0 left-0 top-0 w-1 ${style.line}`}
      />

      <div className="relative">
        <div className="mb-5 flex items-start gap-3">
          <span
            className={`mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full ${style.dot} shadow-[0_0_0_4px_rgba(59,130,246,0.08)]`}
          />

          <div className="min-w-0">
            <p
              className={`text-[0.65rem] font-bold uppercase tracking-[0.1em] ${style.eyebrow}`}
            >
              {eyebrow}
            </p>

            <h3 className="mt-1 text-base font-bold tracking-[-0.01em] text-slate-950">
              {title}
            </h3>

            {description && (
              <p className="mt-1.5 max-w-3xl text-sm leading-6 text-slate-500">
                {description}
              </p>
            )}
          </div>
        </div>

        {children}
      </div>
    </section>
  )
}

export default EvidenceSection

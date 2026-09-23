const navigationSections = [
  {
    label: 'Analysis',
    items: [
      {
        id: 'optimization-studio',
        label: 'SQL Optimization Studio',
        enabled: true,
      },
      {
        id: 'interactive-analytics',
        label: 'Interactive Analytics',
        enabled: true,
      },
      {
        id: 'overview',
        label: 'Overview',
        enabled: true,
      },
      {
        id: 'recommendations',
        label: 'Recommendations',
        enabled: true,
      },
      {
        id: 'queries',
        label: 'Queries',
        enabled: true,
      },
      {
        id: 'workloads',
        label: 'Workloads',
        enabled: true,
      },
    ],
  },
  {
    label: 'Evaluation',
    items: [
      {
        id: 'benchmarks',
        label: 'Benchmarks',
        enabled: true,
      },
      {
        id: 'cost-benefit',
        label: 'Cost & Benefit',
        enabled: true,
      },
      {
        id: 'composite-indexes',
        label: 'Composite Indexes',
        enabled: true,
      },
    ],
  },
  {
    label: 'Decision & Evidence',
    items: [
      {
        id: 'production-decisions',
        label: 'Production Decisions',
        enabled: true,
      },
      {
        id: 'provenance',
        label: 'Evidence & Provenance',
        enabled: true,
      },
    ],
  },
]

function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="dashboard-sidebar flex shrink-0 flex-col">
      <div className="dashboard-brand px-5 py-5">
        <div className="relative z-10 flex items-center gap-3">
          <div className="dashboard-brand-mark">SQL</div>

          <div>
            <h1 className="dashboard-brand-title">
              SQL Profiler
            </h1>

            <p className="dashboard-brand-subtitle">
              Optimization Intelligence
            </p>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-5">
        {navigationSections.map((section) => (
          <div className="dashboard-nav-section" key={section.label}>
            <p className="dashboard-nav-label">{section.label}</p>

            <div className="space-y-1">
              {section.items.map((item) => {
                const isActive = activePage === item.id

                if (!item.enabled) {
                  return (
                    <div
                      key={item.id}
                      className="dashboard-nav-item dashboard-nav-disabled"
                    >
                      <span className="dashboard-nav-dot" />
                      <span>{item.label}</span>
                    </div>
                  )
                }

                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => onNavigate(item.id)}
                    className={`dashboard-nav-item dashboard-focus ${
                      isActive ? 'dashboard-nav-item-active' : ''
                    }`}
                  >
                    <span className="dashboard-nav-dot" />
                    <span>{item.label}</span>
                  </button>
                )
              })}
            </div>
          </div>
        ))}
      </nav>

      <div className="border-t border-white/10 px-5 py-4">
        <div className="flex items-center gap-2">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 shadow-[0_0_0_3px_rgba(52,211,153,0.08)]" />

          <p className="text-[0.68rem] font-medium text-slate-400">
            Read-only reporting dashboard
          </p>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar

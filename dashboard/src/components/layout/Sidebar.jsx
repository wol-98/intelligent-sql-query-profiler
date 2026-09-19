const navigationItems = [
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
    enabled: false,
  },
  {
    id: 'workloads',
    label: 'Workloads',
    enabled: true,
  },
  {
    id: 'benchmarks',
    label: 'Benchmarks',
    enabled: false,
  },
  {
    id: 'cost-benefit',
    label: 'Cost & Benefit',
    enabled: false,
  },
  {
    id: 'composite-indexes',
    label: 'Composite Indexes',
    enabled: false,
  },
  {
    id: 'production-decisions',
    label: 'Production Decisions',
    enabled: false,
  },
  {
    id: 'provenance',
    label: 'Evidence & Provenance',
    enabled: false,
  },
]

function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="flex w-64 shrink-0 flex-col border-r border-slate-200 bg-white">
      <div className="border-b border-slate-200 px-6 py-6">
        <h1 className="text-base font-semibold leading-tight text-slate-900">
          SQL Profiler
        </h1>

        <p className="mt-1 text-xs text-slate-500">
          Optimization Intelligence
        </p>
      </div>

      <nav className="flex-1 px-3 py-4">
        <div className="space-y-1">
          {navigationItems.map((item) => {
            const isActive = activePage === item.id

            if (!item.enabled) {
              return (
                <div
                  key={item.id}
                  className="flex cursor-not-allowed items-center rounded-lg px-3 py-2.5 text-sm text-slate-300"
                >
                  {item.label}
                </div>
              )
            }

            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onNavigate(item.id)}
                className={`flex w-full items-center rounded-lg px-3 py-2.5 text-left text-sm font-medium transition ${
                  isActive
                    ? 'bg-slate-100 text-slate-900'
                    : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                {item.label}
              </button>
            )
          })}
        </div>
      </nav>

      <div className="border-t border-slate-200 px-6 py-4">
        <p className="text-xs text-slate-400">
          Read-only reporting dashboard
        </p>
      </div>
    </aside>
  )
}

export default Sidebar

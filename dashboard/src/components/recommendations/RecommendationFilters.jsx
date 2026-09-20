function SelectFilter({ label, value, onChange, options }) {
  return (
    <label className="flex min-w-0 flex-col gap-2">
      <span className="text-[0.65rem] font-bold uppercase tracking-[0.08em] text-slate-400">
        {label}
      </span>

      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="dashboard-focus w-full rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-2.5 text-sm font-medium text-slate-700 outline-none transition hover:border-slate-300 hover:bg-white focus:border-blue-400 focus:bg-white focus:ring-4 focus:ring-blue-500/10"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  )
}

function RecommendationFilters({
  search,
  onSearchChange,
  priority,
  onPriorityChange,
  decision,
  onDecisionChange,
  evidence,
  onEvidenceChange,
  validation,
  onValidationChange,
  onClear,
  activeFilterCount = 0,
}) {
  return (
    <section className="dashboard-card p-5">
      <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-blue-500" />

            <h3 className="dashboard-section-title">
              Explore recommendations
            </h3>
          </div>

          <p className="dashboard-section-description">
            Filter the recommendation inventory without changing the underlying
            recommendation order or scores.
          </p>
        </div>

        {activeFilterCount > 0 && (
          <div className="rounded-full bg-blue-50 px-3 py-1.5 text-[0.68rem] font-semibold text-blue-700">
            {activeFilterCount} active filter
            {activeFilterCount === 1 ? '' : 's'}
          </div>
        )}
      </div>

      <div className="grid gap-4 lg:grid-cols-6">
        <label className="flex min-w-0 flex-col gap-2 lg:col-span-2">
          <span className="text-[0.65rem] font-bold uppercase tracking-[0.08em] text-slate-400">
            Search
          </span>

          <div className="relative">
            <span className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400">
              ⌕
            </span>

            <input
              type="search"
              value={search}
              onChange={(event) => onSearchChange(event.target.value)}
              placeholder="ID, table, column, index, or reason..."
              className="dashboard-focus w-full rounded-xl border border-slate-200 bg-slate-50 py-2.5 pl-9 pr-3.5 text-sm font-medium text-slate-700 outline-none transition placeholder:text-slate-400 hover:border-slate-300 hover:bg-white focus:border-blue-400 focus:bg-white focus:ring-4 focus:ring-blue-500/10"
            />
          </div>
        </label>

        <SelectFilter
          label="Priority"
          value={priority}
          onChange={onPriorityChange}
          options={[
            { value: 'ALL', label: 'All priorities' },
            { value: 'High', label: 'High' },
            { value: 'Medium', label: 'Medium' },
            { value: 'Low', label: 'Low' },
          ]}
        />

        <SelectFilter
          label="Decision"
          value={decision}
          onChange={onDecisionChange}
          options={[
            { value: 'ALL', label: 'All decisions' },
            { value: 'RECOMMEND', label: 'Recommend' },
            { value: 'REVIEW', label: 'Review' },
            { value: 'REJECT', label: 'Reject' },
            {
              value: 'INSUFFICIENT_EVIDENCE',
              label: 'Insufficient evidence',
            },
          ]}
        />

        <SelectFilter
          label="Evidence"
          value={evidence}
          onChange={onEvidenceChange}
          options={[
            { value: 'ALL', label: 'All evidence' },
            { value: 'COMPLETE', label: 'Complete' },
            { value: 'PARTIAL', label: 'Partial' },
            { value: 'INSUFFICIENT', label: 'Insufficient' },
          ]}
        />

        <SelectFilter
          label="Validation"
          value={validation}
          onChange={onValidationChange}
          options={[
            { value: 'ALL', label: 'All validation outcomes' },
            { value: 'SUCCESS', label: 'Success' },
            { value: 'NEUTRAL', label: 'Neutral' },
            { value: 'UNSUCCESSFUL', label: 'Unsuccessful' },
            { value: 'UNSAFE', label: 'Unsafe' },
          ]}
        />
      </div>

      <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-4">
        <p className="text-xs text-slate-400">
          Filters affect only the displayed recommendation inventory.
        </p>

        <button
          type="button"
          onClick={onClear}
          className="dashboard-focus rounded-xl border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-600 transition hover:border-slate-300 hover:bg-slate-50 hover:text-slate-900"
        >
          Clear filters
        </button>
      </div>
    </section>
  )
}

export default RecommendationFilters

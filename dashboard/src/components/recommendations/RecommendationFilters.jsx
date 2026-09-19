function SelectFilter({ label, value, onChange, options }) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </span>

      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 outline-none transition focus:border-slate-400"
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
}) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4">
        <h3 className="text-base font-semibold text-slate-900">
          Explore recommendations
        </h3>

        <p className="mt-1 text-sm text-slate-500">
          Filter the recommendation inventory without changing the underlying
          recommendation order or scores.
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        <label className="flex flex-col gap-1.5 lg:col-span-2">
          <span className="text-xs font-medium uppercase tracking-wide text-slate-500">
            Search
          </span>

          <input
            type="search"
            value={search}
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder="Search ID, table, column, index, or reason..."
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-slate-400"
          />
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
      </div>

      <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
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

        <button
          type="button"
          onClick={onClear}
          className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50"
        >
          Clear filters
        </button>
      </div>
    </section>
  )
}

export default RecommendationFilters

function formatMilliseconds(value) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return `${Number(value).toFixed(3)} ms`
}

function formatPercent(value) {
  if (value === null || value === undefined) {
    return 'Not available'
  }

  return `${Number(value).toFixed(2)}%`
}

function SectionHeading({ eyebrow, title, description, accent = 'blue' }) {
  const accents = {
    blue: 'bg-blue-500',
    violet: 'bg-violet-500',
    cyan: 'bg-cyan-500',
  }

  return (
    <div>
      <div className="flex items-center gap-2">
        <span
          className={`h-2 w-2 rounded-full ${
            accents[accent] || accents.blue
          }`}
        />

        <p className="text-[0.62rem] font-bold uppercase tracking-[0.1em] text-slate-400">
          {eyebrow}
        </p>
      </div>

      <h3 className="mt-1.5 text-base font-bold tracking-[-0.01em] text-slate-950">
        {title}
      </h3>

      {description && (
        <p className="mt-1 text-sm leading-6 text-slate-500">
          {description}
        </p>
      )}
    </div>
  )
}

function ExecutionConcentration({ workloads }) {
  const dominant = workloads[0]

  if (!dominant) {
    return null
  }

  const timeShare = Math.max(
    0,
    Math.min(Number(dominant.time_share) || 0, 100),
  )

  return (
    <section className="dashboard-card overflow-hidden">
      <div className="border-b border-slate-100 bg-gradient-to-r from-blue-50/70 via-white to-cyan-50/30 px-5 py-5">
        <SectionHeading
          eyebrow="Execution concentration"
          title="Where the workload spends its time"
          description="Share of total profiled execution time attributed to the leading workload pattern."
          accent="blue"
        />
      </div>

      <div className="p-5">
        <div className="flex items-end justify-between gap-4">
          <div>
            <p className="text-4xl font-bold tracking-[-0.05em] text-slate-950">
              {formatPercent(dominant.time_share)}
            </p>

            <p className="mt-1 text-xs font-medium text-slate-400">
              W1 · dominant workload
            </p>
          </div>

          <div className="text-right">
            <p className="text-sm font-bold text-slate-800">
              {formatMilliseconds(dominant.total_execution_time_ms)}
            </p>

            <p className="mt-1 text-xs text-slate-400">
              total execution time
            </p>
          </div>
        </div>

        <div className="mt-5 h-3 overflow-hidden rounded-full bg-slate-100">
          <div
            className="h-full rounded-full bg-gradient-to-r from-blue-500 via-blue-500 to-cyan-400 transition-all duration-700"
            style={{ width: `${timeShare}%` }}
          />
        </div>

        <div className="mt-3 flex items-center justify-between text-[0.62rem] text-slate-400">
          <span>0%</span>
          <span>100% of profiled execution time</span>
        </div>

        <div className="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-4">
          <div className="grid gap-3 sm:grid-cols-3">
            <div>
              <p className="text-[0.58rem] font-bold uppercase tracking-[0.08em] text-slate-400">
                Executions
              </p>

              <p className="mt-1 text-lg font-bold text-slate-950">
                {dominant.execution_count}
              </p>
            </div>

            <div>
              <p className="text-[0.58rem] font-bold uppercase tracking-[0.08em] text-slate-400">
                Frequency share
              </p>

              <p className="mt-1 text-lg font-bold text-slate-950">
                {formatPercent(dominant.frequency_share)}
              </p>
            </div>

            <div>
              <p className="text-[0.58rem] font-bold uppercase tracking-[0.08em] text-slate-400">
                Priority
              </p>

              <p className="mt-1 text-lg font-bold text-violet-700">
                {dominant.priority}
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

function PriorityMix({ workloads }) {
  const categories = [
    {
      name: 'Critical',
      description: '50% or more of execution time',
      color: 'bg-violet-500',
      soft: 'bg-violet-50',
      text: 'text-violet-700',
    },
    {
      name: 'High',
      description: '10% to under 50%',
      color: 'bg-cyan-500',
      soft: 'bg-cyan-50',
      text: 'text-cyan-700',
    },
    {
      name: 'Moderate',
      description: '5% to under 10%',
      color: 'bg-blue-500',
      soft: 'bg-blue-50',
      text: 'text-blue-700',
    },
    {
      name: 'Low',
      description: 'Below the moderate threshold',
      color: 'bg-slate-400',
      soft: 'bg-slate-50',
      text: 'text-slate-700',
    },
  ]

  const counts = Object.fromEntries(
    categories.map((category) => [
      category.name,
      workloads.filter(
        (workload) => workload.priority === category.name,
      ).length,
    ]),
  )

  return (
    <section className="dashboard-card p-5">
      <SectionHeading
        eyebrow="Priority composition"
        title="Workload priority mix"
        description="Distribution of fingerprinted workloads across the established priority classes."
        accent="violet"
      />

      <div className="mt-6 space-y-3">
        {categories.map((category) => {
          const count = counts[category.name]
          const percentage =
            workloads.length > 0
              ? (count / workloads.length) * 100
              : 0

          return (
            <div
              key={category.name}
              className={`rounded-xl border border-slate-200 ${category.soft} p-3.5`}
            >
              <div className="flex items-center justify-between gap-3">
                <div className="flex min-w-0 items-center gap-2.5">
                  <span
                    className={`h-2.5 w-2.5 shrink-0 rounded-full ${category.color}`}
                  />

                  <span className="text-sm font-semibold text-slate-800">
                    {category.name}
                  </span>
                </div>

                <span
                  className={`text-sm font-bold ${category.text}`}
                >
                  {count}
                </span>
              </div>

              <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/80">
                <div
                  className={`h-full rounded-full ${category.color}`}
                  style={{ width: `${percentage}%` }}
                />
              </div>

              <p className="mt-2 text-[0.62rem] text-slate-400">
                {category.description}
              </p>
            </div>
          )
        })}
      </div>

      <div className="mt-4 flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
        <span className="text-xs font-medium text-slate-500">
          Total fingerprints
        </span>

        <span className="text-sm font-bold text-slate-900">
          {workloads.length}
        </span>
      </div>
    </section>
  )
}

function ExecutionTimeDistribution({ workloads }) {
  const visibleWorkloads = workloads.slice(0, 10)

  return (
    <section className="dashboard-card p-5">
      <SectionHeading
        eyebrow="Execution distribution"
        title="Where execution time is concentrated"
        description="The ten largest workload patterns by total profiled execution time."
        accent="cyan"
      />

      <div className="mt-6 space-y-3">
        {visibleWorkloads.map((workload, index) => {
          const timeShare = Math.max(
            0,
            Math.min(Number(workload.time_share) || 0, 100),
          )

          return (
            <div key={workload.fingerprint}>
              <div className="mb-1.5 flex items-center gap-3">
                <span className="w-7 shrink-0 text-[0.62rem] font-bold text-cyan-600">
                  W{index + 1}
                </span>

                <div className="min-w-0 flex-1">
                  <p
                    className="truncate font-mono text-[0.62rem] text-slate-500"
                    title={workload.template}
                  >
                    {workload.template}
                  </p>
                </div>

                <span className="shrink-0 text-xs font-bold text-slate-800">
                  {formatPercent(workload.time_share)}
                </span>
              </div>

              <div className="ml-10 h-2 overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-500"
                  style={{ width: `${Math.max(timeShare, 0.5)}%` }}
                />
              </div>
            </div>
          )
        })}
      </div>

      <div className="mt-5 border-t border-slate-100 pt-4">
        <p className="text-xs text-slate-400">
          Values represent the existing workload time-share calculation and
          are presented descriptively.
        </p>
      </div>
    </section>
  )
}

function FrequencyTimeChart({ workloads }) {
  const executionCounts = workloads.map(
    (workload) => Number(workload.execution_count) || 0,
  )

  const executionTimes = workloads.map(
    (workload) =>
      Number(workload.total_execution_time_ms) || 0,
  )

  const maxFrequency = Math.max(...executionCounts, 1)
  const maxTime = Math.max(...executionTimes, 1)

  const minFrequency = Math.min(
    ...executionCounts.filter((value) => value > 0),
    1,
  )

  const minTime = Math.min(
    ...executionTimes.filter((value) => value > 0),
    1,
  )

  const frequencyRange =
    Math.log10(maxFrequency + 1) -
    Math.log10(minFrequency + 1) || 1

  const timeRange =
    Math.log10(maxTime + 1) -
    Math.log10(minTime + 1) || 1

  const dominantWorkload = workloads[0]

  function getX(value) {
    const transformed =
      Math.log10((Number(value) || 0) + 1)

    return (
      8 +
      ((transformed - Math.log10(minFrequency + 1)) /
        frequencyRange) *
        84
    )
  }

  function getY(value) {
    const transformed =
      Math.log10((Number(value) || 0) + 1)

    return (
      92 -
      ((transformed - Math.log10(minTime + 1)) /
        timeRange) *
        78
    )
  }

  return (
    <section className="dashboard-card overflow-hidden">
      <div className="border-b border-slate-100 px-5 py-5">
        <SectionHeading
          eyebrow="Workload relationship"
          title="Frequency × execution time"
          description="Descriptive view of workload execution frequency against total execution time."
          accent="blue"
        />
      </div>

      <div className="grid lg:grid-cols-[minmax(0,1fr)_280px]">
        <div className="p-5">
          <div className="relative h-[360px] overflow-hidden rounded-2xl border border-slate-200 bg-slate-50">
            {/* Horizontal grid */}
            <div className="absolute inset-0">
              <div className="absolute inset-x-0 top-[20%] border-t border-dashed border-slate-200" />
              <div className="absolute inset-x-0 top-[40%] border-t border-dashed border-slate-200" />
              <div className="absolute inset-x-0 top-[60%] border-t border-dashed border-slate-200" />
              <div className="absolute inset-x-0 top-[80%] border-t border-dashed border-slate-200" />

              <div className="absolute inset-y-0 left-[20%] border-l border-dashed border-slate-200" />
              <div className="absolute inset-y-0 left-[40%] border-l border-dashed border-slate-200" />
              <div className="absolute inset-y-0 left-[60%] border-l border-dashed border-slate-200" />
              <div className="absolute inset-y-0 left-[80%] border-l border-dashed border-slate-200" />
            </div>

            {/* Axis labels */}
            <div className="absolute left-3 top-3 rounded-md bg-white/90 px-2 py-1 text-[0.56rem] font-bold uppercase tracking-[0.08em] text-slate-400 shadow-sm">
              Total time ↑
            </div>

            <div className="absolute bottom-3 left-1/2 -translate-x-1/2 rounded-md bg-white/90 px-2 py-1 text-[0.56rem] font-bold uppercase tracking-[0.08em] text-slate-400 shadow-sm">
              Execution frequency →
            </div>

            {/* Points */}
            {workloads.map((workload, index) => {
              const isDominant = index === 0

              const x = getX(workload.execution_count)
              const y = getY(workload.total_execution_time_ms)

              return (
                <div
                  key={workload.fingerprint}
                  className="group absolute"
                  style={{
                    left: `${Math.max(4, Math.min(x, 94))}%`,
                    top: `${Math.max(5, Math.min(y, 91))}%`,
                  }}
                  title={`W${index + 1} · ${workload.execution_count} executions · ${formatMilliseconds(workload.total_execution_time_ms)} · ${formatPercent(workload.time_share)}`}
                >
                  <div
                    className={`-translate-x-1/2 -translate-y-1/2 rounded-full ring-2 ring-white transition duration-200 group-hover:scale-125 ${
                      isDominant
                        ? 'h-5 w-5 bg-blue-500 shadow-[0_0_0_5px_rgba(59,130,246,0.14)]'
                        : 'h-3.5 w-3.5 bg-slate-500'
                    }`}
                  />

                  {isDominant && (
                    <div className="absolute left-4 top-1/2 -translate-y-1/2 whitespace-nowrap rounded-md border border-blue-100 bg-white px-2 py-1 text-[0.58rem] font-bold text-blue-700 shadow-sm">
                      W1 · {formatPercent(workload.time_share)}
                    </div>
                  )}
                </div>
              )
            })}

            {/* Scale note */}
            <div className="absolute right-3 top-3 rounded-md border border-slate-200 bg-white/90 px-2 py-1 text-[0.55rem] font-semibold text-slate-400 shadow-sm">
              Log-scaled visual axes
            </div>

            <div className="absolute bottom-3 left-3 text-[0.55rem] text-slate-400">
              Lower
            </div>

            <div className="absolute bottom-3 right-3 text-[0.55rem] text-slate-400">
              Higher
            </div>
          </div>

          <div className="mt-3 flex flex-wrap items-center justify-between gap-2 text-[0.62rem] text-slate-400">
            <span>
              Each point represents one workload fingerprint.
            </span>

            <span className="font-semibold text-slate-500">
              {workloads.length} fingerprints
            </span>
          </div>
        </div>

        <aside className="border-t border-slate-100 bg-slate-50/70 p-5 lg:border-l lg:border-t-0">
          <p className="text-[0.62rem] font-bold uppercase tracking-[0.1em] text-slate-400">
            Reading the chart
          </p>

          <h4 className="mt-2 text-sm font-bold text-slate-900">
            Frequency and time are different dimensions
          </h4>

          <p className="mt-2 text-xs leading-5 text-slate-500">
            A workload may execute frequently without dominating total
            execution time. Conversely, a workload with fewer executions can
            account for a large share of total time.
          </p>

          {dominantWorkload && (
            <div className="mt-5 rounded-xl border border-blue-100 bg-blue-50/70 p-4">
              <div className="flex items-center justify-between gap-3">
                <span className="text-[0.58rem] font-bold uppercase tracking-[0.08em] text-blue-600">
                  Dominant workload
                </span>

                <span className="rounded-md bg-white px-2 py-1 text-[0.58rem] font-bold text-blue-700 shadow-sm">
                  W1
                </span>
              </div>

              <p className="mt-3 text-3xl font-bold tracking-[-0.04em] text-slate-950">
                {formatPercent(dominantWorkload.time_share)}
              </p>

              <p className="mt-1 text-xs text-slate-500">
                of total profiled execution time
              </p>

              <div className="mt-4 space-y-2.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Executions</span>
                  <span className="font-bold text-slate-800">
                    {dominantWorkload.execution_count}
                  </span>
                </div>

                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Total time</span>
                  <span className="font-bold text-slate-800">
                    {formatMilliseconds(
                      dominantWorkload.total_execution_time_ms,
                    )}
                  </span>
                </div>

                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">Frequency share</span>
                  <span className="font-bold text-slate-800">
                    {formatPercent(dominantWorkload.frequency_share)}
                  </span>
                </div>
              </div>
            </div>
          )}

          <div className="mt-4 rounded-xl border border-slate-200 bg-white p-3">
            <p className="text-[0.58rem] font-bold uppercase tracking-[0.08em] text-slate-400">
              Visualization note
            </p>

            <p className="mt-2 text-[0.68rem] leading-5 text-slate-500">
              Both axes use logarithmic visual scaling because the observed
              workload values span substantially different magnitudes. The
              underlying execution counts and execution times are unchanged.
            </p>
          </div>
        </aside>
      </div>
    </section>
  )
}

function PerformanceAnalytics({ workloads }) {
  if (workloads.length === 0) {
    return null
  }

  return (
    <section className="space-y-5">
      <SectionHeading
        eyebrow="Performance analytics"
        title="Workload execution intelligence"
        description="Descriptive views of execution-time concentration, workload priority, and frequency relationships. These visualizations do not introduce a new ranking or scoring model."
        accent="cyan"
      />

      <div className="grid gap-5 lg:grid-cols-2">
        <ExecutionConcentration workloads={workloads} />

        <PriorityMix workloads={workloads} />
      </div>

      <ExecutionTimeDistribution workloads={workloads} />

      <FrequencyTimeChart workloads={workloads} />
    </section>
  )
}

export default PerformanceAnalytics

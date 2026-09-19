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

function WorkloadDistribution({ workloads }) {
  const counts = {
    Critical: workloads.filter(
      (workload) => workload.priority === 'Critical',
    ).length,
    High: workloads.filter(
      (workload) => workload.priority === 'High',
    ).length,
    Moderate: workloads.filter(
      (workload) => workload.priority === 'Moderate',
    ).length,
    Low: workloads.filter(
      (workload) => workload.priority === 'Low',
    ).length,
  }

  const items = [
    {
      label: 'Critical',
      value: counts.Critical,
      description: '50% or more of execution time',
    },
    {
      label: 'High',
      value: counts.High,
      description: '10% to under 50%',
    },
    {
      label: 'Moderate',
      value: counts.Moderate,
      description: '5% to under 10%',
    },
    {
      label: 'Low',
      value: counts.Low,
      description: 'Below the moderate threshold',
    },
  ]

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div>
        <h4 className="text-sm font-semibold text-slate-900">
          Workload distribution
        </h4>

        <p className="mt-1 text-xs text-slate-500">
          Distribution of workload patterns by the established workload
          priority classification.
        </p>
      </div>

      <div className="mt-5 space-y-4">
        {items.map((item) => (
          <div
            key={item.label}
            className="flex items-center gap-4"
          >
            <div className="w-20 shrink-0">
              <p className="text-sm font-medium text-slate-700">
                {item.label}
              </p>
            </div>

            <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-slate-400"
                style={{
                  width:
                    workloads.length > 0
                      ? `${(item.value / workloads.length) * 100}%`
                      : '0%',
                }}
              />
            </div>

            <div className="w-8 text-right text-sm font-semibold text-slate-700">
              {item.value}
            </div>

            <p className="hidden w-52 text-xs text-slate-400 lg:block">
              {item.description}
            </p>
          </div>
        ))}
      </div>
    </section>
  )
}

function TimeShareChart({ workloads }) {
  const chartWorkloads = workloads.slice(0, 10)

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div>
        <h4 className="text-sm font-semibold text-slate-900">
          Execution-time distribution
        </h4>

        <p className="mt-1 text-xs text-slate-500">
          Workload share of total profiled execution time.
        </p>
      </div>

      <div className="mt-5 space-y-4">
        {chartWorkloads.map((workload, index) => {
          const label = `W${index + 1}`

          return (
            <div key={workload.fingerprint}>
              <div className="mb-1 flex items-center justify-between gap-4 text-xs">
                <div className="flex min-w-0 items-center gap-2">
                  <span className="w-7 shrink-0 font-semibold text-slate-500">
                    {label}
                  </span>

                  <span
                    className="truncate font-mono text-slate-600"
                    title={workload.template}
                  >
                    {workload.template}
                  </span>
                </div>

                <span className="shrink-0 font-semibold text-slate-700">
                  {formatPercent(workload.time_share)}
                </span>
              </div>

              <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-slate-500"
                  style={{
                    width: `${Math.min(
                      Math.max(workload.time_share || 0, 0),
                      100,
                    )}%`,
                  }}
                />
              </div>
            </div>
          )
        })}
      </div>

      {workloads.length > 10 && (
        <p className="mt-4 text-xs text-slate-400">
          Showing the 10 largest workloads by execution time.
        </p>
      )}
    </section>
  )
}

function FrequencyTimeChart({ workloads }) {
  const maxFrequency = Math.max(
    ...workloads.map((workload) => workload.execution_count || 0),
    1,
  )

  const maxTime = Math.max(
    ...workloads.map(
      (workload) => workload.total_execution_time_ms || 0,
    ),
    1,
  )

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div>
        <h4 className="text-sm font-semibold text-slate-900">
          Frequency vs. execution time
        </h4>

        <p className="mt-1 text-xs text-slate-500">
          Each point represents one workload fingerprint.
        </p>
      </div>

      <div className="mt-6">
        <div className="relative h-64 border-b border-l border-slate-200 bg-slate-50">
          <div className="absolute left-2 top-2 text-[10px] text-slate-400">
            Higher total time
          </div>

          {workloads.map((workload, index) => {
            const x =
              ((workload.execution_count || 0) / maxFrequency) * 92 + 4

            const y =
              96 -
              ((workload.total_execution_time_ms || 0) / maxTime) * 88

            return (
              <div
                key={workload.fingerprint}
                className="absolute h-3 w-3 rounded-full bg-slate-600 ring-2 ring-white"
                style={{
                  left: `${x}%`,
                  top: `${Math.max(4, Math.min(y, 92))}%`,
                }}
                title={`W${index + 1}: ${workload.execution_count} executions, ${formatMilliseconds(workload.total_execution_time_ms)}`}
              />
            )
          })}

          <div className="absolute bottom-1 left-1/2 -translate-x-1/2 text-[10px] text-slate-400">
            Execution frequency
          </div>
        </div>

        <div className="mt-2 flex justify-between pl-4 text-[10px] text-slate-400">
          <span>Lower frequency</span>
          <span>Higher frequency</span>
        </div>
      </div>
    </section>
  )
}

function PerformanceAnalytics({ workloads }) {
  if (workloads.length === 0) {
    return null
  }

  return (
    <section className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-slate-900">
          Performance Analytics
        </h3>

        <p className="mt-1 text-sm text-slate-500">
          Descriptive views of workload execution time and frequency.
          These visualizations do not introduce a new ranking or scoring
          model.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <TimeShareChart workloads={workloads} />
        <WorkloadDistribution workloads={workloads} />
      </div>

      <FrequencyTimeChart workloads={workloads} />
    </section>
  )
}

export default PerformanceAnalytics

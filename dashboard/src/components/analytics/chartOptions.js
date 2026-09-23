function truncate(value, length = 28) {
  const text = String(value ?? '')

  return text.length > length
    ? `${text.slice(0, length - 1)}…`
    : text
}

function number(value) {
  const parsed = Number(value)

  return Number.isFinite(parsed) ? parsed : 0
}

export function workloadExecutionOption(workloads = []) {
  const rows = workloads
    .slice()
    .sort(
      (a, b) =>
        number(b.total_execution_time_ms) -
        number(a.total_execution_time_ms),
    )
    .slice(0, 10)
    .reverse()

  return {
    animationDuration: 500,
    grid: {
      left: 150,
      right: 32,
      top: 18,
      bottom: 28,
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
      formatter(params) {
        const item = params?.[0]

        if (!item) {
          return ''
        }

        const workload = rows[item.dataIndex]

        return [
          `<strong>${truncate(workload?.template, 60)}</strong>`,
          `Total execution: ${number(workload?.total_execution_time_ms).toLocaleString()} ms`,
          `Executions: ${number(workload?.execution_count).toLocaleString()}`,
          `Time share: ${number(workload?.time_share).toFixed(2)}%`,
          `Priority: ${workload?.priority ?? '—'}`,
        ].join('<br/>')
      },
    },
    xAxis: {
      type: 'value',
      name: 'Execution time (ms)',
      nameTextStyle: {
        color: '#64748b',
      },
      axisLabel: {
        color: '#64748b',
      },
      splitLine: {
        lineStyle: {
          color: '#e2e8f0',
        },
      },
    },
    yAxis: {
      type: 'category',
      data: rows.map((item) => truncate(item.template)),
      axisLabel: {
        color: '#475569',
        width: 130,
        overflow: 'truncate',
      },
      axisLine: {
        lineStyle: {
          color: '#cbd5e1',
        },
      },
    },
    series: [
      {
        type: 'bar',
        data: rows.map((item) => ({
          value: number(item.total_execution_time_ms),
          fingerprint: item.fingerprint,
        })),
        barMaxWidth: 24,
        itemStyle: {
          borderRadius: [0, 6, 6, 0],
        },
      },
    ],
  }
}

export function benchmarkComparisonOption(benchmarks = []) {
  const rows = benchmarks
    .filter(
      (item) =>
        item.baseline_time_ms !== null ||
        item.indexed_time_ms !== null,
    )
    .slice()
    .sort(
      (a, b) =>
        number(b.baseline_time_ms) -
        number(a.baseline_time_ms),
    )
    .slice(0, 8)

  return {
    animationDuration: 500,
    grid: {
      left: 48,
      right: 24,
      top: 42,
      bottom: 70,
    },
    legend: {
      top: 4,
      textStyle: {
        color: '#475569',
      },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
      formatter(params) {
        const index = params?.[0]?.dataIndex
        const row = rows[index]

        if (!row) {
          return ''
        }

        return [
          `<strong>Recommendation #${row.recommendation_id ?? '—'}</strong>`,
          `Baseline: ${number(row.baseline_time_ms).toFixed(2)} ms`,
          `Indexed: ${number(row.indexed_time_ms).toFixed(2)} ms`,
          `Improvement: ${number(row.improvement_percent).toFixed(2)}%`,
          `Outcome: ${row.outcome ?? '—'}`,
        ].join('<br/>')
      },
    },
    xAxis: {
      type: 'category',
      data: rows.map(
        (item) => `#${item.recommendation_id ?? '—'}`,
      ),
      axisLabel: {
        color: '#64748b',
      },
    },
    yAxis: {
      type: 'value',
      name: 'Execution time (ms)',
      nameTextStyle: {
        color: '#64748b',
      },
      axisLabel: {
        color: '#64748b',
      },
      splitLine: {
        lineStyle: {
          color: '#e2e8f0',
        },
      },
    },
    series: [
      {
        name: 'Baseline',
        type: 'bar',
        data: rows.map((item) => ({
          value: number(item.baseline_time_ms),
          recommendation_id: item.recommendation_id,
        })),
        barMaxWidth: 18,
      },
      {
        name: 'Indexed',
        type: 'bar',
        data: rows.map((item) => ({
          value: number(item.indexed_time_ms),
          recommendation_id: item.recommendation_id,
        })),
        barMaxWidth: 18,
      },
    ],
  }
}

export function costBenefitOption(items = []) {
  const rows = items.filter(
    (item) =>
      item?.storage?.ratio_percent !== null &&
      item?.read?.average_improvement_percent !== null,
  )

  return {
    animationDuration: 500,
    grid: {
      left: 60,
      right: 30,
      top: 24,
      bottom: 48,
    },
    tooltip: {
      trigger: 'item',
      formatter(params) {
        const item = rows[params.dataIndex]

        if (!item) {
          return ''
        }

        return [
          `<strong>Recommendation #${item.recommendation_id ?? '—'}</strong>`,
          `Read improvement: ${number(item.read.average_improvement_percent).toFixed(2)}%`,
          `Storage ratio: ${number(item.storage.ratio_percent).toFixed(2)}%`,
          `Write overhead: ${
            item.write?.average_overhead_ms === null ||
            item.write?.average_overhead_ms === undefined
              ? '—'
              : `${number(item.write.average_overhead_ms).toFixed(3)} ms`
          }`,
          `Evidence: ${item.evidence_status ?? '—'}`,
        ].join('<br/>')
      },
    },
    xAxis: {
      type: 'value',
      name: 'Storage ratio (%)',
      nameTextStyle: {
        color: '#64748b',
      },
      axisLabel: {
        color: '#64748b',
        formatter: '{value}%',
      },
      splitLine: {
        lineStyle: {
          color: '#f1f5f9',
        },
      },
    },
    yAxis: {
      type: 'value',
      name: 'Read improvement (%)',
      nameTextStyle: {
        color: '#64748b',
      },
      axisLabel: {
        color: '#64748b',
        formatter: '{value}%',
      },
      splitLine: {
        lineStyle: {
          color: '#e2e8f0',
        },
      },
    },
    series: [
      {
        type: 'scatter',
        symbolSize: 16,
        data: rows.map((item) => ({
          value: [
            number(item.storage.ratio_percent),
            number(item.read.average_improvement_percent),
          ],
          recommendation_id: item.recommendation_id,
        })),
      },
    ],
  }
}

export function executionTimelineOption(queries = []) {
  const rows = queries
    .filter((item) => item?.captured_at && item?.total_execution_time_ms !== null)
    .sort(
      (a, b) =>
        new Date(a.captured_at).getTime() -
        new Date(b.captured_at).getTime(),
    )

  return {
    animationDuration: 500,
    grid: { left: 64, right: 30, top: 24, bottom: 56 },
    tooltip: {
      trigger: 'axis',
      formatter(params) {
        const point = params?.[0]
        const item = rows[point?.dataIndex]
        if (!item) return ''

        return [
          `<strong>Query #${item.query_profile_id ?? '—'}</strong>`,
          `Execution: ${number(item.total_execution_time_ms).toFixed(3)} ms`,
          `Average: ${number(item.average_execution_time_ms).toFixed(3)} ms`,
          `Captured: ${new Date(item.captured_at).toLocaleString()}`,
        ].join('<br/>')
      },
    },
    xAxis: {
      type: 'category',
      name: 'Captured time',
      data: rows.map((item) =>
        new Date(item.captured_at).toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        }),
      ),
      axisLabel: {
        rotate: 35,
      },
    },
    yAxis: {
      type: 'value',
      name: 'Total execution (ms)',
    },
    series: [
      {
        type: 'line',
        smooth: false,
        symbol: 'circle',
        symbolSize: 8,
        data: rows.map((item) => ({
          value: number(item.total_execution_time_ms),
          query_profile_id: item.query_profile_id,
        })),
      },
    ],
  }
}

export function executionDistributionOption(queries = []) {
  const values = queries
    .filter((item) => item?.total_execution_time_ms !== null)
    .map((item) => number(item.total_execution_time_ms))
    .filter((value) => Number.isFinite(value))
    .sort((a, b) => a - b)

  if (!values.length) {
    return {
      title: {
        text: 'No execution-time observations available',
        left: 'center',
        top: 'middle',
      },
    }
  }

  const percentile = (items, p) => {
    const index = (items.length - 1) * p
    const lower = Math.floor(index)
    const upper = Math.ceil(index)

    if (lower === upper) return items[lower]

    return items[lower] + (items[upper] - items[lower]) * (index - lower)
  }

  const min = values[0]
  const q1 = percentile(values, 0.25)
  const median = percentile(values, 0.5)
  const q3 = percentile(values, 0.75)
  const max = values[values.length - 1]

  const iqr = q3 - q1
  const lowerFence = q1 - 1.5 * iqr
  const upperFence = q3 + 1.5 * iqr

  const lowerWhisker = values.find((value) => value >= lowerFence) ?? min
  const upperWhisker =
    [...values].reverse().find((value) => value <= upperFence) ?? max

  const outliers = values
    .filter((value) => value < lowerWhisker || value > upperWhisker)
    .map((value) => [0, value])

  return {
    animationDuration: 500,
    grid: { left: 64, right: 30, top: 24, bottom: 48 },
    tooltip: {
      trigger: 'item',
      formatter(params) {
        if (params.seriesType === 'boxplot') {
          return [
            '<strong>Execution-time distribution</strong>',
            `Min: ${min.toFixed(3)} ms`,
            `Q1: ${q1.toFixed(3)} ms`,
            `Median: ${median.toFixed(3)} ms`,
            `Q3: ${q3.toFixed(3)} ms`,
            `Max: ${max.toFixed(3)} ms`,
          ].join('<br/>')
        }

        return `Observed execution: ${number(params.value?.[1]).toFixed(3)} ms`
      },
    },
    xAxis: {
      type: 'category',
      data: ['Observed queries'],
    },
    yAxis: {
      type: 'log',
      name: 'Total execution (ms, log scale)',
      min: 0.1,
      axisLabel: {
        formatter: (value) => `${number(value).toLocaleString()} ms`,
      },
    },
    series: [
      {
        name: 'Execution time',
        type: 'boxplot',
        data: [[
          lowerWhisker,
          q1,
          median,
          q3,
          upperWhisker,
        ]],
      },
      {
        name: 'Outliers',
        type: 'scatter',
        data: outliers,
        symbolSize: 10,
      },
    ],
  }
}

export function workloadHeatmapOption(workloads = []) {
  const rows = workloads
    .filter((item) => item?.fingerprint)
    .sort(
      (a, b) =>
        number(b.total_execution_time_ms) -
        number(a.total_execution_time_ms),
    )
    .slice(0, 10)

  const metrics = [
    'Execution count',
    'Average execution',
    'Total execution',
    'Time share',
  ]

  const data = []

  rows.forEach((item, rowIndex) => {
    const values = [
      number(item.execution_count),
      number(item.average_execution_time_ms),
      number(item.total_execution_time_ms),
      number(item.time_share),
    ]

    const maxByMetric = [
      Math.max(...rows.map((row) => number(row.execution_count)), 1),
      Math.max(...rows.map((row) => number(row.average_execution_time_ms)), 1),
      Math.max(...rows.map((row) => number(row.total_execution_time_ms)), 1),
      Math.max(...rows.map((row) => number(row.time_share)), 1),
    ]

    values.forEach((value, columnIndex) => {
      data.push([
        columnIndex,
        rowIndex,
        maxByMetric[columnIndex]
          ? Number((value / maxByMetric[columnIndex]).toFixed(3))
          : 0,
        value,
      ])
    })
  })

  return {
    animationDuration: 500,
    grid: { left: 150, right: 30, top: 24, bottom: 64 },
    tooltip: {
      position: 'top',
      formatter(params) {
        const item = rows[params.value[1]]
        const metric = metrics[params.value[0]]
        if (!item) return ''

        return [
          `<strong>${metric}</strong>`,
          `Fingerprint: ${item.fingerprint}`,
          `Value: ${number(params.value[3]).toLocaleString()}`,
        ].join('<br/>')
      },
    },
    xAxis: {
      type: 'category',
      data: metrics,
      splitArea: { show: true },
      axisLabel: { rotate: 25 },
    },
    yAxis: {
      type: 'category',
      data: rows.map((item) => truncate(item.fingerprint, 24)),
      splitArea: { show: true },
    },
    visualMap: {
      min: 0,
      max: 1,
      calculable: false,
      orient: 'horizontal',
      left: 'center',
      bottom: 8,
    },
    series: [
      {
        type: 'heatmap',
        data,
        label: {
          show: true,
          formatter(params) {
            return number(params.value[3]).toLocaleString(undefined, {
              maximumFractionDigits: 2,
            })
          },
        },
      },
    ],
  }
}

export function evidenceRelationshipOption({
  workloads = [],
  queries = [],
  benchmarks = [],
  costBenefits = [],
  decisions = [],
  provenance = [],
  recommendationId = null,
} = {}) {
  const recommendationIds = [
    ...workloads.flatMap((item) => item.recommendation_ids ?? []),
    ...queries.flatMap((item) => item.recommendation_ids ?? []),
    ...benchmarks.map((item) => item.recommendation_id),
    ...costBenefits.map((item) => item.recommendation_id),
    ...decisions.map((item) => item.recommendation_id),
    ...provenance.map((item) => item.recommendation_id),
  ]
    .filter((id) => id !== null && id !== undefined)
    .map(Number)

  const selectedId =
    recommendationId !== null && recommendationId !== undefined
      ? Number(recommendationId)
      : recommendationIds[0]

  if (!Number.isFinite(selectedId)) {
    return {
      title: {
        text: 'Select a recommendation to inspect its evidence chain',
        left: 'center',
        top: 'middle',
        textStyle: {
          fontSize: 14,
          fontWeight: 600,
        },
      },
    }
  }

  const linkedQueries = queries
    .filter((item) =>
      (item.recommendation_ids ?? []).some((id) => Number(id) === selectedId),
    )
    .slice(0, 4)

  const linkedWorkloads = workloads
    .filter((item) =>
      (item.recommendation_ids ?? []).some((id) => Number(id) === selectedId),
    )
    .slice(0, 4)

  const linkedBenchmarks = benchmarks
    .filter((item) => Number(item.recommendation_id) === selectedId)
    .slice(0, 4)

  const linkedCosts = costBenefits
    .filter((item) => Number(item.recommendation_id) === selectedId)
    .slice(0, 4)

  const linkedDecisions = decisions
    .filter((item) => Number(item.recommendation_id) === selectedId)
    .slice(0, 4)

  const linkedProvenance = provenance
    .filter((item) => Number(item.recommendation_id) === selectedId)
    .slice(0, 4)

  const nodes = []
  const links = []

  const addNode = (node) => {
    if (!nodes.some((item) => item.id === node.id)) {
      nodes.push(node)
    }
  }

  const addLink = (source, target) => {
    if (
      nodes.some((item) => item.id === source) &&
      nodes.some((item) => item.id === target) &&
      !links.some(
        (item) => item.source === source && item.target === target,
      )
    ) {
      links.push({ source, target })
    }
  }

  const categoryIndex = {
    Query: 0,
    Workload: 1,
    Recommendation: 2,
    Benchmark: 3,
    'Cost / Benefit': 4,
    Decision: 5,
    Provenance: 6,
  }

  linkedQueries.forEach((item) => {
    const id = `query-${item.query_profile_id}`

    addNode({
      id,
      name: `Query #${item.query_profile_id}`,
      category: categoryIndex.Query,
      symbolSize: 32,
      query_profile_id: item.query_profile_id,
      tooltipText: `${item.query_type ?? 'Query'} · ${number(item.total_execution_time_ms).toFixed(3)} ms`,
    })

    const workload = linkedWorkloads.find(
      (candidate) => candidate.fingerprint === item.fingerprint,
    )

    if (workload) {
      addLink(id, `workload-${workload.fingerprint}`)
    }
  })

  linkedWorkloads.forEach((item) => {
    const id = `workload-${item.fingerprint}`

    addNode({
      id,
      name: `Workload ${truncate(item.fingerprint, 14)}`,
      category: categoryIndex.Workload,
      symbolSize: 34,
      fingerprint: item.fingerprint,
      tooltipText: [
        `Total: ${number(item.total_execution_time_ms).toFixed(3)} ms`,
        `Runs: ${number(item.execution_count).toLocaleString()}`,
        `Time share: ${number(item.time_share).toFixed(2)}%`,
      ].join(' · '),
    })

    addLink(id, `recommendation-${selectedId}`)
  })

  addNode({
    id: `recommendation-${selectedId}`,
    name: `Recommendation #${selectedId}`,
    category: categoryIndex.Recommendation,
    symbolSize: 48,
    recommendation_id: selectedId,
    tooltipText: 'Selected optimization recommendation',
  })

  linkedQueries.forEach((item) => {
    const workload = linkedWorkloads.find(
      (candidate) => candidate.fingerprint === item.fingerprint,
    )

    if (!workload) {
      addLink(`query-${item.query_profile_id}`, `recommendation-${selectedId}`)
    }
  })

  linkedBenchmarks.forEach((item, index) => {
    const id = `benchmark-${item.benchmark_id ?? `${selectedId}-${index}`}`

    addNode({
      id,
      name: `Benchmark ${item.benchmark_id ?? index + 1}`,
      category: categoryIndex.Benchmark,
      symbolSize: 30,
      recommendation_id: selectedId,
      tooltipText: [
        `Baseline: ${number(item.baseline_time_ms).toFixed(3)} ms`,
        `Indexed: ${number(item.indexed_time_ms).toFixed(3)} ms`,
        `Outcome: ${item.outcome ?? '—'}`,
      ].join(' · '),
    })

    addLink(`recommendation-${selectedId}`, id)
  })

  linkedCosts.forEach((item, index) => {
    const id = `cost-${item.experiment_id ?? `${selectedId}-${index}`}`

    addNode({
      id,
      name: `Cost / Benefit ${index + 1}`,
      category: categoryIndex['Cost / Benefit'],
      symbolSize: 30,
      recommendation_id: selectedId,
      tooltipText: [
        `Read improvement: ${number(item.read?.average_improvement_percent).toFixed(2)}%`,
        `Storage ratio: ${number(item.storage?.ratio_percent).toFixed(2)}%`,
        `Evidence: ${item.evidence_status ?? '—'}`,
      ].join(' · '),
    })

    addLink(`recommendation-${selectedId}`, id)
  })

  linkedDecisions.forEach((item, index) => {
    const id = `decision-${index}-${selectedId}`

    addNode({
      id,
      name: item.state ?? `Decision ${index + 1}`,
      category: categoryIndex.Decision,
      symbolSize: 30,
      recommendation_id: selectedId,
      tooltipText: `Production decision: ${item.state ?? '—'}`,
    })

    addLink(`recommendation-${selectedId}`, id)
  })

  linkedProvenance.forEach((item, index) => {
    const id = `provenance-${index}-${selectedId}`

    addNode({
      id,
      name: item.evidence_status ?? `Provenance ${index + 1}`,
      category: categoryIndex.Provenance,
      symbolSize: 30,
      recommendation_id: selectedId,
      tooltipText: `Evidence status: ${item.evidence_status ?? '—'}`,
    })

    addLink(`recommendation-${selectedId}`, id)
  })

  return {
    animationDuration: 600,
    tooltip: {
      formatter(params) {
        if (params.dataType !== 'node') return ''
        return [
          `<strong>${params.data.name}</strong>`,
          params.data.tooltipText ?? '',
        ]
          .filter(Boolean)
          .join('<br/>')
      },
    },
    legend: [
      {
        data: Object.keys(categoryIndex),
        bottom: 4,
        left: 'center',
        itemGap: 14,
      },
    ],
    series: [
      {
        type: 'graph',
        layout: 'force',
        roam: true,
        draggable: true,
        data: nodes,
        links,
        categories: Object.keys(categoryIndex).map((name) => ({ name })),
        label: {
          show: true,
          position: 'right',
          formatter: '{b}',
          fontSize: 11,
        },
        edgeSymbol: ['none', 'arrow'],
        edgeSymbolSize: [4, 9],
        lineStyle: {
          width: 1.5,
          curveness: 0.08,
          opacity: 0.65,
        },
        force: {
          repulsion: 260,
          gravity: 0.08,
          edgeLength: [90, 150],
          friction: 0.12,
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 3,
          },
        },
      },
    ],
  }
}


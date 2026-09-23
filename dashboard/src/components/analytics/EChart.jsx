import { useEffect, useRef } from 'react'
import ReactECharts from 'echarts-for-react'

function EChart({
  option,
  height = 320,
  className = '',
  onEvents,
}) {
  const chartRef = useRef(null)

  useEffect(() => {
    const chart = chartRef.current?.getEchartsInstance()

    if (!chart) {
      return undefined
    }

    function handleResize() {
      chart.resize()
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
    }
  }, [])

  return (
    <div
      className={`w-full overflow-hidden rounded-xl ${className}`}
      style={{ height }}
    >
      <ReactECharts
        ref={chartRef}
        option={option}
        notMerge
        lazyUpdate
        style={{ width: '100%', height: '100%' }}
        onEvents={onEvents}
      />
    </div>
  )
}

export default EChart

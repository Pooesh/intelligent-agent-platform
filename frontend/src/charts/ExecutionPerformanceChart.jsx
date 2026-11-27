
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

function ExecutionPerformanceChart({ executions = [] }) {
  const agentPerformance = executions.reduce((performance, execution) => {
    const agent = execution.selected_agent || 'unknown'
    const duration = Number(execution.execution_time_ms || 0)

    if (!performance[agent]) {
      performance[agent] = {
        agent,
        totalDuration: 0,
        executionCount: 0,
      }
    }

    performance[agent].totalDuration += duration
    performance[agent].executionCount += 1

    return performance
  }, {})

  const chartData = Object.values(agentPerformance).map((item) => ({
    agent: item.agent,
    averageDuration: Math.round(
      item.totalDuration / item.executionCount,
    ),
  }))

  if (chartData.length === 0) {
    return (
      <div className="flex h-[320px] items-center justify-center text-sm text-slate-400">
        No execution performance data available.
      </div>
    )
  }

  return (
    <div className="h-[320px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{
            top: 20,
            right: 20,
            left: 10,
            bottom: 10,
          }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#334155"
            vertical={false}
          />

          <XAxis
            dataKey="agent"
            tick={{ fill: '#94a3b8', fontSize: 12 }}
            axisLine={{ stroke: '#475569' }}
            tickLine={false}
          />

          <YAxis
            tick={{ fill: '#94a3b8', fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(value) => `${value} ms`}
          />

          <Tooltip
            contentStyle={{
              backgroundColor: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '8px',
              color: '#f1f5f9',
            }}
            formatter={(value) => [
              `${Number(value).toLocaleString()} ms`,
              'Average Duration',
            ]}
          />

          <Bar
            dataKey="averageDuration"
            name="Average Duration"
            fill="#38bdf8"
            radius={[6, 6, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default ExecutionPerformanceChart

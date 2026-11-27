
import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'

const COLORS = [
  '#22d3ee',
  '#818cf8',
  '#34d399',
  '#fbbf24',
  '#f472b6',
  '#fb923c',
]

function AgentDistributionChart({ executions = [] }) {
  const agentCounts = executions.reduce((counts, execution) => {
    const agent = execution.selected_agent || 'unknown'

    counts[agent] = (counts[agent] || 0) + 1

    return counts
  }, {})

  const chartData = Object.entries(agentCounts).map(([agent, count]) => ({
    name: agent,
    value: count,
  }))

  if (chartData.length === 0) {
    return (
      <div className="flex h-[300px] items-center justify-center text-sm text-slate-400">
        No agent execution data available.
      </div>
    )
  }

  return (
    <div className="h-[300px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="45%"
            innerRadius={65}
            outerRadius={95}
            paddingAngle={4}
            stroke="none"
          >
            {chartData.map((entry, index) => (
              <Cell
                key={entry.name}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Pie>

          <Tooltip
            contentStyle={{
              backgroundColor: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '8px',
              color: '#f1f5f9',
            }}
            formatter={(value, name) => [
              `${value} executions`,
              name,
            ]}
          />

          <Legend
            verticalAlign="bottom"
            align="center"
            formatter={(value) => (
              <span className="text-sm capitalize text-slate-300">
                {value}
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}

export default AgentDistributionChart

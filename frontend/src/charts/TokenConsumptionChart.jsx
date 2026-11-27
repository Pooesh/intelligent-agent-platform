
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

function TokenConsumptionChart({ usageRecords = [] }) {
  const agentUsage = usageRecords.reduce((usage, record) => {
    const agent = record.agent_name || 'unknown'

    if (!usage[agent]) {
      usage[agent] = {
        agent,
        promptTokens: 0,
        completionTokens: 0,
      }
    }

    usage[agent].promptTokens += Number(record.prompt_tokens || 0)
    usage[agent].completionTokens += Number(record.completion_tokens || 0)

    return usage
  }, {})

  const chartData = Object.values(agentUsage)

  if (chartData.length === 0) {
    return (
      <div className="flex h-[320px] items-center justify-center text-sm text-slate-400">
        No token usage data available.
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
          />

          <Tooltip
            contentStyle={{
              backgroundColor: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '8px',
              color: '#f1f5f9',
            }}
            formatter={(value, name) => [
              Number(value).toLocaleString(),
              name,
            ]}
          />

          <Legend
            formatter={(value) => (
              <span className="text-sm text-slate-300">
                {value}
              </span>
            )}
          />

          <Bar
            dataKey="promptTokens"
            name="Prompt Tokens"
            stackId="tokens"
            fill="#22d3ee"
            radius={[0, 0, 0, 0]}
          />

          <Bar
            dataKey="completionTokens"
            name="Completion Tokens"
            stackId="tokens"
            fill="#818cf8"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export default TokenConsumptionChart


import {
  Activity,
  Bot,
  Coins,
  RefreshCw,
  Server,
  Sparkles,
  Zap,
} from 'lucide-react'

import useDashboardData from '../hooks/useDashboardData'
import AgentDistributionChart from '../charts/AgentDistributionChart'
import TokenConsumptionChart from '../charts/TokenConsumptionChart'
import ExecutionPerformanceChart from '../charts/ExecutionPerformanceChart'

const formatNumber = (value) => {
  return Number(value || 0).toLocaleString('en-US')
}

const formatCost = (value) => {
  return `$${Number(value || 0).toFixed(4)}`
}

const formatDate = (value) => {
  if (!value) return '—'

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) return '—'

  return date.toLocaleString()
}

function MetricCard({ title, value, description, icon: Icon }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-400">{title}</p>
        <Icon size={20} className="text-cyan-400" />
      </div>

      <h2 className="mt-4 text-2xl font-semibold text-white">{value}</h2>

      <p className="mt-2 text-xs text-slate-500">{description}</p>
    </div>
  )
}

function Dashboard() {
  const {
    executions,
    usageRecords,
    usageSummary,
    loading,
    error,
    refreshDashboard,
  } = useDashboardData()

  const agentCounts = executions.reduce((counts, execution) => {
    const agent = execution.selected_agent || 'unknown'

    counts[agent] = (counts[agent] || 0) + 1

    return counts
  }, {})

  const totalExecutions = executions.length
  const totalRequests = usageSummary?.total_requests || 0
  const totalTokens = usageSummary?.total_tokens || 0
  const totalCost = usageSummary?.total_estimated_cost || 0

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-8 text-slate-100 md:px-10">
      <div className="mx-auto max-w-7xl">

        {/* Header */}
        <header className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <div className="flex items-center gap-2">
              <Sparkles className="text-cyan-400" size={24} />
              <h1 className="text-2xl font-bold text-white">
                Intelligent Agent Platform
              </h1>
            </div>

            <p className="mt-2 text-sm text-slate-400">
              Agent monitoring and observability dashboard
            </p>
          </div>

          <button
            onClick={refreshDashboard}
            disabled={loading}
            className="flex items-center justify-center gap-2 rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <RefreshCw
              size={16}
              className={loading ? 'animate-spin' : ''}
            />
            Refresh
          </button>
        </header>

        {/* Error */}
        {error && (
          <div className="mb-6 rounded-lg border border-red-800 bg-red-950/40 p-4 text-sm text-red-300">
            {error}
          </div>
        )}

        {/* Metrics */}
        <section className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard
            title="Total Executions"
            value={formatNumber(totalExecutions)}
            description="Recent agent executions"
            icon={Activity}
          />

          <MetricCard
            title="LLM Requests"
            value={formatNumber(totalRequests)}
            description="Total recorded LLM requests"
            icon={Server}
          />

          <MetricCard
            title="Total Tokens"
            value={formatNumber(totalTokens)}
            description="Prompt and completion tokens"
            icon={Zap}
          />

          <MetricCard
            title="Estimated API Cost"
            value={formatCost(totalCost)}
            description="Provider API cost estimate"
            icon={Coins}
          />
        </section>

        {/* Agent Activity */}
        <section className="mb-8 rounded-xl border border-slate-800 bg-slate-900 p-6">
          <div className="mb-5 flex items-center gap-2">
            <Bot className="text-cyan-400" size={20} />
            <h2 className="text-lg font-semibold text-white">
              Agent Activity
            </h2>
          </div>

          {loading && executions.length === 0 ? (
            <p className="text-sm text-slate-400">
              Loading agent activity...
            </p>
          ) : Object.keys(agentCounts).length === 0 ? (
            <p className="text-sm text-slate-400">
              No agent executions found.
            </p>
          ) : (
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              {Object.entries(agentCounts).map(([agent, count]) => (
                <div
                  key={agent}
                  className="rounded-lg border border-slate-800 bg-slate-950 p-4"
                >
                  <p className="text-sm capitalize text-slate-400">
                    {agent} Agent
                  </p>

                  <p className="mt-2 text-2xl font-semibold text-cyan-400">
                    {count}
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    Recent executions
                  </p>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Agent Distribution Chart */}
        <section className="mb-8 rounded-xl border border-slate-800 bg-slate-900 p-6">
          <div className="mb-5">
            <h2 className="text-lg font-semibold text-white">
              Agent Distribution
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Distribution of executions across specialist agents
            </p>
          </div>

          <AgentDistributionChart executions={executions} />
        </section>

        {/* Token Consumption Chart */}
        <section className="mb-8 rounded-xl border border-slate-800 bg-slate-900 p-6">
          <div className="mb-5">
            <h2 className="text-lg font-semibold text-white">
              Token Consumption
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Prompt and completion tokens consumed by each agent
            </p>
          </div>

          <TokenConsumptionChart usageRecords={usageRecords} />
        </section>

        {/* Execution Performance Chart */}
        <section className="mb-8 rounded-xl border border-slate-800 bg-slate-900 p-6">
          <div className="mb-5">
            <h2 className="text-lg font-semibold text-white">
              Execution Performance
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Average execution duration for each agent
            </p>
          </div>

          <ExecutionPerformanceChart executions={executions} />
        </section>

        {/* Recent Executions */}
        <section className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
          <div className="flex flex-col justify-between gap-2 border-b border-slate-800 p-6 sm:flex-row sm:items-center">
            <div>
              <h2 className="text-lg font-semibold text-white">
                Recent Executions
              </h2>

              <p className="mt-1 text-sm text-slate-400">
                Latest agent workflow activity
              </p>
            </div>

            <span className="text-xs text-slate-500">
              Showing {executions.length} records
            </span>
          </div>

          {loading && executions.length === 0 ? (
            <p className="p-6 text-sm text-slate-400">
              Loading executions...
            </p>
          ) : executions.length === 0 ? (
            <p className="p-6 text-sm text-slate-400">
              No executions available.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-950 text-xs uppercase text-slate-400">
                  <tr>
                    <th className="px-6 py-4">Execution ID</th>
                    <th className="px-6 py-4">Agent</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4">Duration</th>
                    <th className="px-6 py-4">Created At</th>
                  </tr>
                </thead>

                <tbody>
                  {executions.map((execution) => (
                    <tr
                      key={execution.execution_id}
                      className="border-t border-slate-800 transition hover:bg-slate-800/40"
                    >
                      <td className="px-6 py-4 font-mono text-xs text-slate-300">
                        {execution.execution_id?.slice(0, 8) || '—'}
                      </td>

                      <td className="px-6 py-4 capitalize text-slate-200">
                        {execution.selected_agent || 'Unknown'}
                      </td>

                      <td className="px-6 py-4">
                        <span
                          className={`rounded-full px-2.5 py-1 text-xs ${
                            execution.execution_status === 'success'
                              ? 'bg-emerald-500/10 text-emerald-400'
                              : execution.execution_status === 'failure'
                                ? 'bg-red-500/10 text-red-400'
                                : 'bg-amber-500/10 text-amber-400'
                          }`}
                        >
                          {execution.execution_status || 'Unknown'}
                        </span>
                      </td>

                      <td className="px-6 py-4 text-slate-300">
                        {formatNumber(execution.execution_time_ms)} ms
                      </td>

                      <td className="px-6 py-4 text-slate-400">
                        {formatDate(execution.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* Recent LLM Usage */}
        <section className="mt-8 overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
          <div className="border-b border-slate-800 p-6">
            <h2 className="text-lg font-semibold text-white">
              Recent LLM Usage
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Model requests and token consumption
            </p>
          </div>

          {usageRecords.length === 0 ? (
            <p className="p-6 text-sm text-slate-400">
              {loading ? 'Loading usage records...' : 'No usage records found.'}
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-950 text-xs uppercase text-slate-400">
                  <tr>
                    <th className="px-6 py-4">Agent</th>
                    <th className="px-6 py-4">Provider</th>
                    <th className="px-6 py-4">Model</th>
                    <th className="px-6 py-4">Tokens</th>
                    <th className="px-6 py-4">Cost</th>
                  </tr>
                </thead>

                <tbody>
                  {usageRecords.map((record, index) => (
                    <tr
                      key={record.usage_id || `${record.timestamp}-${index}`}
                      className="border-t border-slate-800"
                    >
                      <td className="px-6 py-4 capitalize text-slate-200">
                        {record.agent_name || 'Unknown'}
                      </td>

                      <td className="px-6 py-4 text-slate-300">
                        {record.provider || '—'}
                      </td>

                      <td className="px-6 py-4 text-slate-300">
                        {record.model || '—'}
                      </td>

                      <td className="px-6 py-4 text-slate-300">
                        {formatNumber(record.total_tokens)}
                      </td>

                      <td className="px-6 py-4 text-slate-300">
                        {formatCost(record.estimated_cost)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <footer className="mt-8 text-center text-xs text-slate-600">
          Intelligent Agent Platform · Monitoring & Observability
        </footer>
      </div>
    </main>
  )
}

export default Dashboard

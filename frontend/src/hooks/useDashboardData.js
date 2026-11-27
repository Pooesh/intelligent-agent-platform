
import { useCallback, useEffect, useState } from 'react'

import {
  getRecentExecutions,
  getRecentUsage,
  getUsageSummary,
} from '../services/api'

const useDashboardData = () => {
  const [executions, setExecutions] = useState([])
  const [usageRecords, setUsageRecords] = useState([])
  const [usageSummary, setUsageSummary] = useState(null)

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadDashboardData = useCallback(async () => {
    try {
      const [executionData, usageData, summaryData] = await Promise.all([
        getRecentExecutions(20),
        getRecentUsage(20),
        getUsageSummary(),
      ])

      setExecutions(executionData.executions || [])
      setUsageRecords(usageData.usage_records || [])
      setUsageSummary(summaryData)
      setError(null)
    } catch (err) {
      console.error('Dashboard data fetch failed:', err)

      setError(
        err.response?.data?.detail ||
        err.message ||
        'Failed to load dashboard data.',
      )
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchDashboardData = useCallback(async () => {
    setLoading(true)
    setError(null)

    await loadDashboardData()
  }, [loadDashboardData])

  useEffect(() => {
    let cancelled = false

    Promise.resolve().then(() => {
      if (!cancelled) {
        return loadDashboardData()
      }
    })

    return () => {
      cancelled = true
    }
  }, [loadDashboardData])

  return {
    executions,
    usageRecords,
    usageSummary,
    loading,
    error,
    refreshDashboard: fetchDashboardData,
  }
}

export default useDashboardData

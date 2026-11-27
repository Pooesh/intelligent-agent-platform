
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

export const getRecentExecutions = async (limit = 20) => {
  const response = await api.get('/observability/executions', {
    params: { limit },
  })

  return response.data
}

export const getExecutionById = async (executionId) => {
  const response = await api.get(
    `/observability/executions/${executionId}`,
  )

  return response.data
}

export const getRecentUsage = async (limit = 20) => {
  const response = await api.get('/observability/usage', {
    params: { limit },
  })

  return response.data
}

export const getUsageSummary = async () => {
  const response = await api.get('/observability/usage/summary')

  return response.data
}

export default api

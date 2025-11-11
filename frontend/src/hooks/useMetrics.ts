import { useEffect, useState, useCallback } from 'react'
import { fetchMetrics, MetricsResponse } from '../services/api'

export type UseMetricsParams = {
  userId: number
  startDate: string
  endDate: string
}

export function useMetrics({ userId, startDate, endDate }: UseMetricsParams) {
  const [data, setData] = useState<MetricsResponse | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<string>('')

  const loadMetrics = useCallback(async () => {
    setIsLoading(true)
    setError('')
    try {
      const result = await fetchMetrics({ userId, startDate, endDate })
      setData(result)
    } catch (err) {
      console.error(err)
      setError('Falha ao carregar métricas. Verifique se as integrações estão conectadas.')
    } finally {
      setIsLoading(false)
    }
  }, [userId, startDate, endDate])

  useEffect(() => {
    loadMetrics()
  }, [loadMetrics])

  return { data, isLoading, error, refetch: loadMetrics }
}

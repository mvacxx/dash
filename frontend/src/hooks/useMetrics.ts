import { useEffect, useState, useCallback } from 'react'
import { fetchMetrics, MetricsResponse } from '../services/api'

export type UseMetricsParams = {
  startDate: string
  endDate: string
  enabled?: boolean
}

export function useMetrics({ startDate, endDate, enabled = true }: UseMetricsParams) {
  const [data, setData] = useState<MetricsResponse | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<string>('')

  const loadMetrics = useCallback(async () => {
    if (!enabled) {
      return
    }
    setIsLoading(true)
    setError('')
    try {
      const result = await fetchMetrics({ startDate, endDate })
      setData(result)
    } catch (err) {
      console.error(err)
      setError('Falha ao carregar métricas. Verifique se as integrações estão conectadas.')
    } finally {
      setIsLoading(false)
    }
  }, [enabled, startDate, endDate])

  useEffect(() => {
    if (enabled) {
      loadMetrics()
    }
  }, [loadMetrics])

  return { data, isLoading, error, refetch: loadMetrics }
}

import axios from 'axios'
import { ChartMetric } from '../components/MetricsChart'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
})

type FetchMetricsParams = {
  userId: number
  startDate: string
  endDate: string
}

export type MetricsResponse = {
  metrics: ChartMetric[]
  totalSpend: number
  totalRevenue: number
  averageRoi: number
}

export async function fetchMetrics({ userId, startDate, endDate }: FetchMetricsParams): Promise<MetricsResponse> {
  const response = await api.get(`/metrics/${userId}`, {
    params: {
      start_date: startDate,
      end_date: endDate,
    },
  })

  const data = response.data
  return {
    metrics: data.metrics.map((metric: any) => ({
      metricDate: metric.metric_date,
      spend: metric.spend,
      revenue: metric.revenue,
      roi: metric.roi,
    })),
    totalSpend: data.total_spend,
    totalRevenue: data.total_revenue,
    averageRoi: data.average_roi,
  }
}

type FacebookPayload = {
  accountId: string
  accessToken: string
  businessId?: string
}

type AdSensePayload = {
  accountId: string
  accessToken: string
  clientId: string
  clientSecret: string
  refreshToken: string
}

export async function connectFacebook(userId: number, payload: FacebookPayload) {
  return api.post(`/integrations/facebook/${userId}`, {
    account_id: payload.accountId,
    access_token: payload.accessToken,
    business_id: payload.businessId || undefined,
  })
}

export async function connectAdSense(userId: number, payload: AdSensePayload) {
  return api.post(`/integrations/adsense/${userId}`, {
    account_id: payload.accountId,
    access_token: payload.accessToken,
    client_id: payload.clientId,
    client_secret: payload.clientSecret,
    refresh_token: payload.refreshToken,
  })
}

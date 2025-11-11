import axios from 'axios'
import { ChartMetric } from '../components/MetricsChart'
import { User } from '../types/user'
import { Integration } from '../types/integration'
import { SyncNotification } from '../types/notification'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
})

export function setAuthToken(token: string | null) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common.Authorization
  }
}

export type MetricsResponse = {
  metrics: ChartMetric[]
  totalSpend: number
  totalRevenue: number
  averageRoi: number
}

export type LoginPayload = {
  email: string
  password: string
}

export type LoginResponse = {
  accessToken: string
  tokenType: string
  user: User
}

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const response = await api.post('/auth/login', {
    email: payload.email,
    password: payload.password,
  })
  const data = response.data
  const mapped: LoginResponse = {
    accessToken: data.access_token,
    tokenType: data.token_type,
    user: data.user,
  }
  setAuthToken(mapped.accessToken)
  return mapped
}

export async function registerUser(payload: { name: string; email: string; password: string }) {
  const response = await api.post('/users', {
    name: payload.name,
    email: payload.email,
    password: payload.password,
  })
  return response.data as User
}

export async function fetchMetrics({
  startDate,
  endDate,
}: {
  startDate: string
  endDate: string
}): Promise<MetricsResponse> {
  const response = await api.get('/metrics', {
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
  expiresIn?: number
  tokenExpiry?: string
}

export async function connectFacebook(payload: FacebookPayload) {
  return api.post('/integrations/facebook', {
    account_id: payload.accountId,
    access_token: payload.accessToken,
    business_id: payload.businessId || undefined,
  })
}

export async function connectAdSense(payload: AdSensePayload) {
  return api.post('/integrations/adsense', {
    account_id: payload.accountId,
    access_token: payload.accessToken,
    client_id: payload.clientId,
    client_secret: payload.clientSecret,
    refresh_token: payload.refreshToken,
    expires_in: payload.expiresIn,
    token_expiry: payload.tokenExpiry,
  })
}

export async function listIntegrations(): Promise<Integration[]> {
  const response = await api.get('/integrations')
  return response.data as Integration[]
}

export async function updateFacebookIntegration(
  integrationId: number,
  payload: Partial<FacebookPayload> & { businessId?: string; apiVersion?: string }
) {
  return api.put(`/integrations/facebook/${integrationId}`, {
    account_id: payload.accountId,
    access_token: payload.accessToken,
    business_id: payload.businessId,
    api_version: payload.apiVersion,
  })
}

export async function updateAdSenseIntegration(
  integrationId: number,
  payload: Partial<AdSensePayload>
) {
  return api.put(`/integrations/adsense/${integrationId}`, {
    account_id: payload.accountId,
    access_token: payload.accessToken,
    client_id: payload.clientId,
    client_secret: payload.clientSecret,
    refresh_token: payload.refreshToken,
    token_expiry: payload.tokenExpiry,
    expires_in: payload.expiresIn,
  })
}

export async function deleteIntegration(integrationId: number) {
  await api.delete(`/integrations/${integrationId}`)
}

export async function listNotifications(): Promise<SyncNotification[]> {
  const response = await api.get('/notifications')
  return response.data as SyncNotification[]
}

export async function markNotificationRead(notificationId: number) {
  await api.post(`/notifications/${notificationId}/read`)
}

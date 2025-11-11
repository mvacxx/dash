export type Integration = {
  id: number
  type: 'facebook_ads' | 'google_adsense'
  created_at: string
  credentials: Record<string, unknown>
}

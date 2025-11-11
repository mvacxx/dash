export type FacebookIntegration = {
  id: number
  type: 'facebook_ads'
  created_at: string
  credentials: {
    account_id: string
    access_token?: string
    business_id?: string
    api_version?: string
  }
}

export type GoogleIntegration = {
  id: number
  type: 'google_adsense'
  created_at: string
  credentials: {
    account_id: string
    access_token?: string
    refresh_token?: string
    client_id?: string
    client_secret?: string
    token_expiry?: string
  }
}

export type Integration = FacebookIntegration | GoogleIntegration

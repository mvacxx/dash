import { FormEvent, useEffect, useMemo, useState } from 'react'
import { Integration } from '../types/integration'
import { updateAdSenseIntegration, updateFacebookIntegration } from '../services/api'

interface Props {
  integration: Integration
  onCancel: () => void
  onSaved: () => void
}

export function IntegrationEditor({ integration, onCancel, onSaved }: Props) {
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const initialFacebook = useMemo(() => {
    if (integration.type !== 'facebook_ads') {
      return null
    }
    return {
      accountId: integration.credentials.account_id,
      accessToken: integration.credentials.access_token ?? '',
      businessId: integration.credentials.business_id ?? '',
      apiVersion: integration.credentials.api_version ?? '',
    }
  }, [integration])

  const initialGoogle = useMemo(() => {
    if (integration.type !== 'google_adsense') {
      return null
    }
    return {
      accountId: integration.credentials.account_id,
      accessToken: integration.credentials.access_token ?? '',
      refreshToken: integration.credentials.refresh_token ?? '',
      clientId: integration.credentials.client_id ?? '',
      clientSecret: integration.credentials.client_secret ?? '',
      tokenExpiry: integration.credentials.token_expiry ?? '',
    }
  }, [integration])

  const [facebookForm, setFacebookForm] = useState(initialFacebook)
  const [googleForm, setGoogleForm] = useState(initialGoogle)

  useEffect(() => {
    if (integration.type === 'facebook_ads') {
      setFacebookForm(initialFacebook)
    } else {
      setFacebookForm(null)
    }
  }, [integration, initialFacebook])

  useEffect(() => {
    if (integration.type === 'google_adsense') {
      setGoogleForm(initialGoogle)
    } else {
      setGoogleForm(null)
    }
  }, [integration, initialGoogle])

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)
    try {
      if (integration.type === 'facebook_ads' && facebookForm) {
        await updateFacebookIntegration(integration.id, {
          accountId: facebookForm.accountId,
          accessToken: facebookForm.accessToken,
          businessId: facebookForm.businessId,
          apiVersion: facebookForm.apiVersion,
        })
      }
      if (integration.type === 'google_adsense' && googleForm) {
        await updateAdSenseIntegration(integration.id, {
          accountId: googleForm.accountId,
          accessToken: googleForm.accessToken,
          clientId: googleForm.clientId,
          clientSecret: googleForm.clientSecret,
          refreshToken: googleForm.refreshToken,
          tokenExpiry: googleForm.tokenExpiry || undefined,
        })
      }
      onSaved()
    } catch (err) {
      console.error(err)
      setError('Não foi possível salvar as alterações. Verifique os dados e tente novamente.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form className="integration-card" onSubmit={handleSubmit}>
      <h3>Editar integração</h3>
      {integration.type === 'facebook_ads' && facebookForm && (
        <>
          <label>
            ID da conta de anúncios
            <input
              required
              value={facebookForm.accountId}
              onChange={(event) =>
                setFacebookForm({ ...facebookForm, accountId: event.target.value })
              }
            />
          </label>
          <label>
            Access token
            <input
              required
              value={facebookForm.accessToken}
              onChange={(event) =>
                setFacebookForm({ ...facebookForm, accessToken: event.target.value })
              }
            />
          </label>
          <label>
            Business ID (opcional)
            <input
              value={facebookForm.businessId}
              onChange={(event) =>
                setFacebookForm({ ...facebookForm, businessId: event.target.value })
              }
            />
          </label>
          <label>
            Versão da API (opcional)
            <input
              value={facebookForm.apiVersion}
              onChange={(event) =>
                setFacebookForm({ ...facebookForm, apiVersion: event.target.value })
              }
              placeholder="v18.0"
            />
          </label>
        </>
      )}

      {integration.type === 'google_adsense' && googleForm && (
        <>
          <label>
            Nome do recurso da conta
            <input
              required
              value={googleForm.accountId}
              onChange={(event) =>
                setGoogleForm({ ...googleForm, accountId: event.target.value })
              }
            />
          </label>
          <label>
            Access token
            <input
              required
              value={googleForm.accessToken}
              onChange={(event) =>
                setGoogleForm({ ...googleForm, accessToken: event.target.value })
              }
            />
          </label>
          <label>
            Refresh token
            <input
              required
              value={googleForm.refreshToken}
              onChange={(event) =>
                setGoogleForm({ ...googleForm, refreshToken: event.target.value })
              }
            />
          </label>
          <label>
            Client ID
            <input
              required
              value={googleForm.clientId}
              onChange={(event) => setGoogleForm({ ...googleForm, clientId: event.target.value })}
            />
          </label>
          <label>
            Client secret
            <input
              required
              value={googleForm.clientSecret}
              onChange={(event) =>
                setGoogleForm({ ...googleForm, clientSecret: event.target.value })
              }
            />
          </label>
          <label>
            Data de expiração (ISO 8601)
            <input
              value={googleForm.tokenExpiry}
              onChange={(event) =>
                setGoogleForm({ ...googleForm, tokenExpiry: event.target.value })
              }
              placeholder="2024-01-01T00:00:00Z"
            />
          </label>
        </>
      )}

      {error && <p className="error">{error}</p>}
      <div className="integration-editor-actions">
        <button className="secondary" type="button" onClick={onCancel} disabled={isSubmitting}>
          Cancelar
        </button>
        <button className="primary" type="submit" disabled={isSubmitting}>
          Salvar alterações
        </button>
      </div>
    </form>
  )
}
